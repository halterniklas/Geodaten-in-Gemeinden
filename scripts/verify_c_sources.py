#!/usr/bin/env python3
"""C-Grundlagenkataster: Links prüfen, Quellen ergänzen, Excel und Berichte erzeugen.

Ablauf (Standard, alle Schritte):
  1. Ausgangsdatei data/C_Grundlagenkataster_Schweiz_Kantone_Gemeinden.xlsx lesen.
  2. Jeder Zeile der Gesamtübersicht eine stabile ID zuweisen (z. B. SEE-C1-01).
  3. Kuratierte Korrekturen und neue Quellen aus data/quellen_kuratiert.json einspielen.
  4. Jede URL technisch prüfen (Syntax, DNS, HEAD mit GET-Fallback, Weiterleitungen,
     Dateityp) und inhaltlich abgleichen (Titel/Text gegen erwartete Schlüsselwörter
     und Ortsangabe). HTTP 200 allein gilt nicht als Verifikation.
  5. Automatische Recherche (Discovery): offizielle Einstiegsseiten und Sitemaps nach
     Dokumentlinks durchsuchen; optional Brave Search API (Secret BRAVE_SEARCH_API_KEY).
     Funde landen als ungeprüfte Kandidaten im Blatt «Recherche-Kandidaten».
  6. C_Grundlagenkataster_verifiziert.xlsx, reports/link_validation.csv,
     reports/link_validation.json, reports/discovery_kandidaten.csv und
     reports/recherchebericht.md schreiben.

Aufruf:
  pip install -r requirements.txt
  python3 scripts/verify_c_sources.py                     # alles (braucht Internet)
  python3 scripts/verify_c_sources.py --offline           # ohne Netz; nutzt reports/link_validation.json als Cache
  python3 scripts/verify_c_sources.py --no-discovery      # nur Linkprüfung + Excel
  python3 scripts/verify_c_sources.py --sync-only FILE    # Gemeindeblätter einer bearbeiteten Datei neu aus der Gesamtübersicht erzeugen
"""
from __future__ import annotations

import argparse
import copy
import csv
import datetime as dt
import io
import json
import os
import re
import socket
import sys
import threading
import time
import urllib.robotparser
from collections import Counter, OrderedDict, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlparse, urlunparse

import openpyxl
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

try:  # Netzwerkbibliotheken sind im Offline-Modus nicht zwingend nötig
    import requests
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    requests = None
    BeautifulSoup = None

ROOT = Path(__file__).resolve().parent.parent
INPUT_XLSX = ROOT / "data" / "C_Grundlagenkataster_Schweiz_Kantone_Gemeinden.xlsx"
CURATED_JSON = ROOT / "data" / "quellen_kuratiert.json"
SEEDS_JSON = ROOT / "data" / "discovery_seeds.json"
OUTPUT_XLSX = ROOT / "C_Grundlagenkataster_verifiziert.xlsx"
REPORT_DIR = ROOT / "reports"

USER_AGENT = (
    "Mozilla/5.0 (compatible; C-Grundlagenkataster-Linkpruefung/1.0; "
    "+https://github.com/halterniklas/Geodaten-in-Gemeinden)"
)
TIMEOUT = 25
MAX_BYTES = 100 * 1024 * 1024
HOST_DELAY = 1.5  # Sekunden zwischen zwei Anfragen an denselben Host
WORKERS = 6
RETRIES = 3

GEMEINDEN = OrderedDict(
    [
        ("Seelisberg", {"kanton": "Uri", "kuerzel": "SEE", "sheet": "Seelisberg", "table": "KatasterSeelisberg"}),
        ("Münchenstein", {"kanton": "Basel-Landschaft", "kuerzel": "MUE", "sheet": "Münchenstein", "table": "KatasterMuenchenstein"}),
        ("Wil", {"kanton": "St. Gallen", "kuerzel": "WIL", "sheet": "Wil", "table": "KatasterWil"}),
    ]
)
KANTON_KUERZEL = {"Uri": "UR", "Basel-Landschaft": "BL", "St. Gallen": "SG"}

# --------------------------------------------------------------------------------------
# Spaltenschema der Gesamtübersicht
# --------------------------------------------------------------------------------------
# (Schlüssel, Kopfzeile, Breite). Die Spalten A–Y der Ausgangsdatei bleiben in
# Reihenfolge und Bezeichnung erhalten; vorne kommt die ID, hinten die neuen Felder.
ORIGINAL_COLS = [
    ("ebene", "Ebene", 15),
    ("land", "Schweiz", 14),
    ("kanton", "Kanton", 22),
    ("gemeinde", "Gemeinde", 18),
    ("dim", "C-Dimension", 15),
    ("thema", "Themenfeld", 24),
    ("titel", "Dokument / Datengrundlage", 48),
    ("doktyp", "Dokumenttyp", 21),
    ("dokstatus", "Dokumentstatus", 28),
    ("rechtsstatus", "Rechts- / Verbindlichkeitsstatus", 26),
    ("herausgeber", "Herausgeber / Zuständigkeit", 24),
    ("url", "Link / Quelle", 45),
    ("bezugsjahr", "Bezugsjahr / Stand", 19),
    ("aktualitaet", "Aktualität geprüft am", 19),
    ("relevanz", "Konkrete Aussage / Relevanz", 54),
    ("kennzahl", "Kennzahl / Prüfkriterium", 35),
    ("methode", "Erhebungs- / Bewertungsmethode", 49),
    ("vergleich", "Vergleichsmassstab", 32),
    ("tragfaehigkeit", "Reifegrad / Tragfähigkeit", 26),
    ("confidence", "Confidence", 14),
    ("datenluecke", "Datenlücke / Gemeindeanfrage", 44),
    ("verbindung", "Verbindung A / B / Q", 24),
    ("sprint2", "Sprint-2-Verwendung", 39),
    ("pruefstatus", "Prüfstatus / nächste Aktion", 40),
    ("herkunft", "Herkunft / Nachweis", 31),
]
NEW_COLS = [
    ("weitere_dim", "Weitere C-Dimensionen", 16),
    ("veroeffentlicht", "Veröffentlichungsdatum", 18),
    ("fundstelle", "Offizielle Fundstelle", 40),
    ("linkstatus", "Linkstatus", 16),
    ("http", "HTTP-Status", 12),
    ("final_url", "Finale URL (nach Weiterleitung)", 40),
    ("dateityp", "Dateityp", 11),
    ("inhalt", "Inhaltsprüfung", 18),
    ("inhalt_detail", "Inhaltsprüfung – Nachweis", 50),
    ("erkannter_titel", "Erkannter Dokumenttitel", 40),
    ("jahre", "Erkannte Jahresangaben", 18),
    ("linkstabilitaet", "Linkstabilität", 26),
    ("letzte_pruefung", "Letzte Linkprüfung", 18),
    ("verfuegbarkeit", "Quellenverfügbarkeit", 30),
    ("einheit", "Einheit / Bezugsjahr", 20),
    ("pruefnachweis", "Prüfnachweis (belegbare Aussage)", 50),
    ("begruendung", "Bewertungsbegründung", 44),
    ("anfrage", "Gemeindeanfrage erforderlich", 15),
    ("zustaendig", "Zuständige Stelle", 30),
    ("bearbeitung", "Bearbeitungsstatus", 16),
    ("hinweis", "Recherchehinweis", 50),
    ("gleiche_quelle", "Gleiche Quelle wie (ID)", 18),
    ("aenderung", "Änderungsprotokoll", 50),
]
COLS = [("id", "ID", 13)] + ORIGINAL_COLS + NEW_COLS
COL_KEYS = [c[0] for c in COLS]
COL_INDEX = {k: i + 1 for i, k in enumerate(COL_KEYS)}
HEADER_TO_KEY = {h: k for k, h, _ in ORIGINAL_COLS}


def col_letter(key: str) -> str:
    return get_column_letter(COL_INDEX[key])


LINKSTATUS = ["Verifiziert", "Weiterleitung", "Fehler", "Nicht prüfbar"]
INHALT = ["Bestätigt", "Teilweise bestätigt", "Offen"]
VERFUEGBARKEIT = [
    "Öffentlich verfügbar und verifiziert",
    "Öffentlich verfügbar – noch nicht geprüft",
    "Nicht öffentlich auffindbar",
    "Nur über Gemeindeanfrage erhältlich",
    "Nicht zugänglich / nicht prüfbar",
]
BEARBEITUNG = ["Offen", "In Prüfung", "Abgeschlossen"]
TRAGFAEHIGKEIT = ["Noch nicht bewertet", "Hoch", "Mittel", "Gering"]
CONFIDENCE = ["Hoch", "Mittel", "Niedrig"]
PRUEFSTATUS = ["Dokument auswerten; Aktualität und Geltung prüfen", "In Bearbeitung", "Geprüft", "Nachforderung offen"]

TODAY = dt.date.today()


# --------------------------------------------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------------------------------------------
def norm(text: str) -> str:
    """Kleinschreibung, Umlaute ausschreiben, Whitespace vereinheitlichen."""
    if not text:
        return ""
    t = text.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss"), ("é", "e"), ("è", "e"),
                 ("­", ""), ("‑", "-"), ("–", "-"), ("—", "-")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t)


def clean_url(url: str) -> str:
    url = (url or "").strip()
    # Leerzeichen in Pfaden kodieren, bestehende Kodierung beibehalten
    p = urlparse(url)
    path = quote(unquote(p.path), safe="/%:@!$&'()*+,;=-._~")
    return urlunparse((p.scheme, p.netloc, path, p.params, p.query, p.fragment))


def url_syntax_ok(url: str) -> tuple[bool, str]:
    p = urlparse(url or "")
    if p.scheme not in ("http", "https"):
        return False, "Schema fehlt oder ist nicht http(s)"
    if not p.netloc or "." not in p.netloc:
        return False, "Domain fehlt"
    if " " in url:
        return False, "Leerzeichen in der URL"
    return True, ""


def link_stability(url: str) -> str:
    u = url.lower()
    host = urlparse(u).netloc
    if "fedlex.admin.ch/eli/" in u:
        return "Hoch (ELI-Permalink)"
    if host.endswith("clex.ch") or "gesetzessammlung.sg.ch" in host or "rechtsbuch.ur.ch" in host:
        return "Hoch (Erlassnummer)"
    if re.search(r"(sessionid|jsessionid|token=|sid=|/_rte/|tmp|temp)", u):
        return "Gering (dynamischer Download)"
    if u.endswith(".pdf") or "/publikationen/" in u or "/dokumente/" in u or "/_docn/" in u:
        return "Mittel (CMS-Dokumentlink)"
    if urlparse(u).path in ("", "/"):
        return "Mittel (Startseite, kein Dokument)"
    return "Mittel (Webseite)"


def extract_years(text: str) -> list[int]:
    years = [int(y) for y in re.findall(r"(?<!\d)(20[0-3]\d)(?!\d)", text or "")]
    years = [y for y in years if 2000 <= y <= TODAY.year + 6]
    return [y for y, _ in Counter(years).most_common(6)]


# --------------------------------------------------------------------------------------
# HTTP-Client mit Host-Drosselung und Retries
# --------------------------------------------------------------------------------------
class Http:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "de-CH,de;q=0.9"})
        self._host_lock = defaultdict(threading.Lock)
        self._host_last = defaultdict(float)
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self.unreachable: Counter = Counter()  # Verbindungs-Timeouts je Host

    def host_blocked(self, url) -> bool:
        """Nach zwei Verbindungs-Timeouts wird ein Host nicht weiter angefragt (schont Server und Laufzeit)."""
        return self.unreachable[urlparse(url).netloc] >= 2

    def _throttle(self, url):
        host = urlparse(url).netloc
        with self._host_lock[host]:
            wait = self._host_last[host] + HOST_DELAY - time.time()
            if wait > 0:
                time.sleep(wait)
            self._host_last[host] = time.time()

    def request(self, method, url, **kw):
        last_exc = None
        if self.host_blocked(url):
            raise requests.ConnectTimeout(f"Host {urlparse(url).netloc} bereits als nicht erreichbar erkannt")
        for attempt in range(RETRIES):
            self._throttle(url)
            try:
                r = self.session.request(method, url, timeout=TIMEOUT, allow_redirects=True, **kw)
                if r.status_code in (429, 500, 502, 503, 504) and attempt < RETRIES - 1:
                    retry_after = r.headers.get("Retry-After", "")
                    time.sleep(min(int(retry_after), 30) if retry_after.isdigit() else 2 ** (attempt + 1))
                    continue
                return r
            except requests.RequestException as exc:  # Verbindungsfehler: erneut versuchen
                last_exc = exc
                if isinstance(exc, requests.ConnectTimeout):
                    self.unreachable[urlparse(url).netloc] += 1
                    if self.host_blocked(url):
                        break
                time.sleep(2 ** (attempt + 1))
        raise last_exc

    def get_limited(self, url):
        r = self.request("GET", url, stream=True)
        chunks, size = [], 0
        try:
            for chunk in r.iter_content(65536):
                chunks.append(chunk)
                size += len(chunk)
                if size > MAX_BYTES:
                    break
        finally:
            r.close()
        return r, b"".join(chunks), size > MAX_BYTES

    def allowed_by_robots(self, url) -> bool:
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                r = self.request("GET", base + "/robots.txt")
                if r.status_code == 200:
                    rp.parse(r.text.splitlines())
                    self._robots[base] = rp
                else:
                    self._robots[base] = None
            except Exception:
                self._robots[base] = None
        rp = self._robots[base]
        return True if rp is None else rp.can_fetch(USER_AGENT, url)

    def sitemaps(self, base) -> list[str]:
        self.allowed_by_robots(base + "/")
        out = []
        try:
            r = self.request("GET", base + "/robots.txt")
            if r.status_code == 200:
                out = [l.split(":", 1)[1].strip() for l in r.text.splitlines() if l.lower().startswith("sitemap:")]
        except Exception:
            pass
        return out or [base + "/sitemap.xml"]


# --------------------------------------------------------------------------------------
# Inhaltsanalyse
# --------------------------------------------------------------------------------------
def analyse_content(body: bytes, content_type: str) -> dict:
    ct = (content_type or "").split(";")[0].strip().lower()
    info = {"dateityp": "", "titel": "", "text": "", "soft404": False, "pdf_seiten": None}
    if body[:5] == b"%PDF-" or ct == "application/pdf":
        info["dateityp"] = "PDF"
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(body), strict=False)
            info["pdf_seiten"] = len(reader.pages)
            meta_title = ""
            try:
                meta_title = (reader.metadata or {}).get("/Title") or ""
            except Exception:
                pass
            texts = []
            for page in reader.pages[:15]:
                try:
                    texts.append(page.extract_text() or "")
                except Exception:
                    pass
            text = "\n".join(texts)
            first_line = next((l.strip() for l in text.splitlines() if len(l.strip()) > 8), "")
            info["titel"] = (str(meta_title).strip() or first_line)[:200]
            info["text"] = text[:200000]
        except Exception as exc:
            info["text"] = ""
            info["titel"] = f"(PDF nicht lesbar: {type(exc).__name__})"
        return info
    if "html" in ct or body[:200].lstrip().lower().startswith((b"<!doctype html", b"<html")):
        info["dateityp"] = "HTML"
        soup = BeautifulSoup(body, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        h1 = soup.find("h1")
        h1t = h1.get_text(" ", strip=True) if h1 else ""
        info["titel"] = " | ".join(t for t in (title, h1t) if t)[:250]
        info["text"] = soup.get_text(" ", strip=True)[:200000]
        probe = norm(info["titel"] + " " + h1t)
        if re.search(r"(seite (wurde )?nicht gefunden|page not found|\b40[34]\b|fehlerseite|not found|an error has occur|access denied|zugriff verweigert)", probe):
            info["soft404"] = True
        return info
    if "json" in ct:
        info["dateityp"] = "JSON"
        info["text"] = body[:200000].decode("utf-8", "replace")
        return info
    ext_map = {
        "spreadsheet": "XLSX", "excel": "XLS", "csv": "CSV", "msword": "DOC",
        "wordprocessing": "DOCX", "zip": "ZIP", "xml": "XML",
    }
    info["dateityp"] = next((v for k, v in ext_map.items() if k in ct), ct or "unbekannt")
    return info


def match_keywords(text: str, title: str, expected: list, places: list[str]) -> dict:
    """expected: Liste von Gruppen; jede Gruppe ist ein String oder eine Liste von Alternativen."""
    hay = norm(title) + " \n " + norm(text)
    found, missing = [], []
    for group in expected or []:
        alts = group if isinstance(group, list) else [group]
        hit = next((a for a in alts if norm(a) in hay), None)
        (found if hit else missing).append(hit or " / ".join(alts))
    place_hits = [p for p in places if norm(p) in hay]
    place_ok = (not places) or bool(place_hits)
    return {"found": found, "missing": missing, "place_ok": place_ok, "place_hits": place_hits,
            "n_expected": len(expected or [])}


# --------------------------------------------------------------------------------------
# Sonderprüfungen für Rechtssammlungen
# --------------------------------------------------------------------------------------
FEDLEX_SPARQL = "https://fedlex.data.admin.ch/sparqlendpoint"


def fedlex_lookup(http: Http, url: str) -> dict | None:
    """Titel eines Bundeserlasses über den offiziellen Fedlex-SPARQL-Endpunkt abfragen.

    fedlex.admin.ch ist eine JavaScript-Anwendung; der HTML-Rahmen enthält keinen
    Erlasstext. Der SPARQL-Endpunkt liefert Titel und Ausserkraftsetzung."""
    m = re.search(r"fedlex\.admin\.ch/eli/(cc/[^/?#]+/[^/?#]+)", url)
    if not m:
        return None
    eli = f"https://fedlex.data.admin.ch/eli/{m.group(1)}"
    query = f"""
PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
SELECT DISTINCT ?title ?short ?noLonger WHERE {{
  <{eli}> jolux:isRealizedBy ?e .
  ?e jolux:language <http://publications.europa.eu/resource/authority/language/DEU> .
  ?e jolux:title ?title .
  OPTIONAL {{ ?e jolux:titleShort ?short }}
  OPTIONAL {{ <{eli}> jolux:dateNoLongerInForce ?noLonger }}
}} LIMIT 3"""
    try:
        r = http.request("POST", FEDLEX_SPARQL, data={"query": query},
                         headers={"Accept": "application/sparql-results+json"})
        rows = r.json()["results"]["bindings"]
    except Exception as exc:
        return {"ok": False, "detail": f"Fedlex-SPARQL nicht auswertbar ({type(exc).__name__})"}
    if not rows:
        return {"ok": False, "detail": "Fedlex-SPARQL: kein Titel zur ELI gefunden"}
    row = rows[0]
    title = row["title"]["value"]
    short = row.get("short", {}).get("value", "")
    no_longer = row.get("noLonger", {}).get("value", "")
    return {"ok": True, "titel": title + (f" ({short})" if short else ""), "ausser_kraft": no_longer,
            "detail": f"Titel via Fedlex-SPARQL ({eli})"}


LEXWORK_HOSTS = ("bl.clex.ch", "www.gesetzessammlung.sg.ch", "gesetzessammlung.sg.ch", "rechtsbuch.ur.ch")


def lexwork_lookup(http: Http, url: str) -> dict | None:
    """Titel eines kantonalen Erlasses aus LexWork-Sammlungen (BL, SG, UR) lesen.

    Die Seiten sind JavaScript-Anwendungen; die öffentliche JSON-Schnittstelle der
    Anwendung liefert Titel und Systematiknummer."""
    p = urlparse(url)
    if p.netloc not in LEXWORK_HOSTS:
        return None
    m = re.search(r"/texts_of_law/([^/?#]+)", p.path)
    if not m:
        return None
    num = m.group(1)
    tried = []
    for api in (f"{p.scheme}://{p.netloc}/api/de/texts_of_law/{num}",
                f"{p.scheme}://{p.netloc}/api/de/texts_of_law/{num}/show_as_json"):
        tried.append(api)
        try:
            r = http.request("GET", api, headers={"Accept": "application/json"})
            if r.status_code != 200 or "json" not in r.headers.get("Content-Type", ""):
                continue
            data = r.json()
            blob = json.dumps(data, ensure_ascii=False)
            title = ""
            for key in ("title", "titel", "name"):
                m2 = re.search(rf'"{key}"\s*:\s*"([^"]{{8,300}})"', blob)
                if m2:
                    title = m2.group(1)
                    break
            return {"ok": True, "titel": title, "text": blob[:200000], "detail": f"Titel via LexWork-API ({api})"}
        except Exception:
            continue
    return {"ok": False, "detail": "LexWork-API nicht erreichbar (" + ", ".join(tried) + ")"}


# --------------------------------------------------------------------------------------
# Linkprüfung
# --------------------------------------------------------------------------------------
def check_url(http: Http, url: str, expected: list, places: list[str]) -> dict:
    res = OrderedDict(
        url=url, final_url="", http="", methode="", linkstatus="", fehler="", dateityp="", titel="",
        jahre="", inhalt="Offen", inhalt_detail="", soft404=False, stabilitaet=link_stability(url),
        geprueft=dt.datetime.now().strftime("%Y-%m-%d %H:%M"), redirect_kette="", ausser_kraft="", textauszug="",
    )
    ok, why = url_syntax_ok(url)
    if not ok:
        res.update(linkstatus="Fehler", fehler=f"Syntax: {why}")
        return res
    host = urlparse(url).hostname
    try:
        socket.getaddrinfo(host, 443)
    except socket.gaierror as exc:
        res.update(linkstatus="Fehler", fehler=f"DNS: {exc}")
        return res

    head_status = None
    try:
        h = http.request("HEAD", url)
        head_status = h.status_code
        res["methode"] = "HEAD"
    except Exception as exc:
        res["methode"] = f"HEAD fehlgeschlagen ({type(exc).__name__})"
    try:
        r, body, truncated = http.get_limited(url)
    except (requests.ConnectTimeout, requests.ReadTimeout, requests.ConnectionError) as exc:
        if isinstance(exc, (requests.ConnectTimeout, requests.ReadTimeout)) or "timed out" in str(exc).lower():
            res.update(linkstatus="Nicht prüfbar",
                       fehler=f"Server vom Runner aus nicht erreichbar (Zeitüberschreitung beim Verbindungsaufbau, mehrfach wiederholt; "
                              f"vermutlich Sperre für Rechenzentrums-IP). Link damit weder bestätigt noch widerlegt. [{type(exc).__name__}]")
        else:
            res.update(linkstatus="Fehler", fehler=f"GET: {type(exc).__name__}: {exc}"[:300])
        if head_status:
            res["http"] = str(head_status)
        return res
    except Exception as exc:
        res.update(linkstatus="Fehler", fehler=f"GET: {type(exc).__name__}: {exc}"[:300])
        if head_status:
            res["http"] = str(head_status)
        return res
    res["methode"] = (res["methode"] + " + GET").strip(" +")
    res["http"] = str(r.status_code) + (f" (HEAD {head_status})" if head_status and head_status != r.status_code else "")
    res["final_url"] = r.url
    chain = [f"{x.status_code} {x.url}" for x in r.history]
    res["redirect_kette"] = " -> ".join(chain + [f"{r.status_code} {r.url}"]) if chain else ""

    if r.status_code in (401, 403, 451) or (r.status_code == 429):
        res.update(linkstatus="Nicht prüfbar", fehler=f"Zugriff verweigert/gedrosselt (HTTP {r.status_code}); keine Umgehung versucht")
        return res
    if r.status_code >= 400:
        res.update(linkstatus="Fehler", fehler=f"HTTP {r.status_code}")
        return res

    info = analyse_content(body, r.headers.get("Content-Type", ""))
    res["dateityp"] = info["dateityp"] + (" (gekürzt)" if truncated else "")
    res["titel"] = info["titel"]
    text = info["text"]
    detail_prefix = []

    special = fedlex_lookup(http, url) or lexwork_lookup(http, url)
    if special:
        detail_prefix.append(special["detail"])
        if special.get("ok"):
            res["titel"] = special.get("titel") or res["titel"]
            text = (special.get("text") or "") + " " + special.get("titel", "") + " " + text
            if special.get("ausser_kraft"):
                res["ausser_kraft"] = special["ausser_kraft"]

    res["jahre"] = ", ".join(str(y) for y in extract_years(res["titel"] + " " + text[:30000]))
    res["textauszug"] = re.sub(r"\s+", " ", info["text"])[:400]
    if info["soft404"]:
        if re.search(r"403|access denied|zugriff verweigert|an error has occur", norm(res["titel"])):
            res.update(linkstatus="Nicht prüfbar", fehler="Fehlerseite «Zugriff verweigert» mit HTTP 200; keine Umgehung versucht")
        else:
            res.update(linkstatus="Fehler", fehler="Soft-404 (Fehlerseite mit HTTP 200)")
        res["inhalt_detail"] = "Fehlerseite erkannt"
        return res

    same = r.url.rstrip("/") == url.rstrip("/") or r.url.replace("http://", "https://").rstrip("/") == url.rstrip("/")
    res["linkstatus"] = "Verifiziert" if (not r.history or same) else "Weiterleitung"

    if not text.strip():
        res["inhalt"] = "Offen"
        res["inhalt_detail"] = "; ".join(detail_prefix + ["Kein auswertbarer Text (z. B. JavaScript-Seite oder Scan)"])
        return res
    m = match_keywords(text, res["titel"], expected, places)
    parts = list(detail_prefix)
    if m["n_expected"]:
        parts.append(f"Schlüsselwörter {len(m['found'])}/{m['n_expected']} gefunden" +
                     (f" ({', '.join(m['found'])})" if m["found"] else "") +
                     (f"; fehlend: {', '.join(m['missing'])}" if m["missing"] else ""))
    else:
        parts.append("Keine erwarteten Schlüsselwörter hinterlegt")
    if places:
        parts.append("Ort/Zuständigkeit: " + (", ".join(m["place_hits"]) if m["place_hits"] else "nicht gefunden (" + "/".join(places) + ")"))
    if res["ausser_kraft"]:
        parts.append(f"ACHTUNG: laut Fedlex nicht mehr in Kraft seit {res['ausser_kraft']}")
    if m["n_expected"] and not m["missing"] and m["place_ok"] and not res["ausser_kraft"]:
        res["inhalt"] = "Bestätigt"
    elif m["found"] or m["place_hits"]:
        res["inhalt"] = "Teilweise bestätigt"
    else:
        res["inhalt"] = "Offen"
    res["inhalt_detail"] = "; ".join(parts)
    return res


# --------------------------------------------------------------------------------------
# Automatische Recherche (Discovery)
# --------------------------------------------------------------------------------------
DIM_PATTERNS = {
    "C1": r"jahresrechnung|rechnung[ _-]?20\d\d|budget|voranschlag|finanzplan|aufgaben[- ]und[- ]finanzplan|investitions|finanzbericht|finanzausgleich|finanzhaushalt|finanzkennzahl|finanzstatistik|steuerfuss",
    "C2": r"liegenschaft|immobilien|bodenpolitik|bodenstrategie|baurecht|grundst|areal|landkauf|landverkauf|landerwerb|verkauf.*parzelle",
    "C3": r"gemeindeordnung|rechtssammlung|erlasse|systematische sammlung|organisationsreglement|zweckverband|leistungsvereinbarung|eignerstrategie|beteiligung|interkommunal|zusammenarbeit|regio |agglomeration|gemeindeverband",
    "C4": r"organigramm|geschaeftsbericht|verwaltungsbericht|personalreglement|stellenplan|digitalisierung|beschaffung|submission|organisationsentwicklung|amtsbericht",
    "C5": r"gemeindeversammlung|protokoll|botschaft|legislatur|leitbild|mitwirkung|abstimmung|parlament|einwohnerrat|gemeindekommission|erlaeuterung|vernehmlassung|gemeindestrategie",
}
DOC_EXT = re.compile(r"\.(pdf|xlsx?|docx?|csv)(\?|$)", re.I)


def classify(text: str) -> list[str]:
    t = norm(text)
    return [d for d, pat in DIM_PATTERNS.items() if re.search(pat, t)]


def discover(http: Http, seeds: dict, log) -> list[dict]:
    cands: dict[str, dict] = {}

    def add(url, anchor, seed, gemeinde, kanton, quelle):
        if not url.startswith("http"):
            return
        dims = classify(anchor + " " + unquote(url))
        if not dims:
            return
        key = url.split("#")[0]
        if key in cands:
            return
        cands[key] = OrderedDict(url=key, ankertext=anchor[:200], dimensionen=",".join(dims),
                                 dokument="ja" if DOC_EXT.search(key) else "nein", gemeinde=gemeinde,
                                 kanton=kanton, gefunden_auf=seed, quelle=quelle)

    for seed in seeds.get("seiten", []):
        url, gem, kt = seed["url"], seed.get("gemeinde", ""), seed.get("kanton", "")
        if not http.allowed_by_robots(url):
            log(f"  robots.txt verbietet {url} – übersprungen")
            continue
        try:
            r = http.request("GET", url)
        except Exception as exc:
            log(f"  Discovery-Fehler {url}: {exc}")
            continue
        if r.status_code != 200 or "html" not in r.headers.get("Content-Type", ""):
            log(f"  Discovery {url}: HTTP {r.status_code}")
            continue
        soup = BeautifulSoup(r.content, "lxml")
        host = urlparse(r.url).netloc
        n0 = len(cands)
        follow = []
        for a in soup.find_all("a", href=True):
            href = urljoin(r.url, a["href"])
            anchor = a.get_text(" ", strip=True) or a.get("title", "")
            add(href, anchor, url, gem, kt, "Einstiegsseite")
            if seed.get("tiefe", 1) > 1 and urlparse(href).netloc == host and not DOC_EXT.search(href) and classify(anchor + " " + href):
                follow.append(href)
        for sub in list(OrderedDict.fromkeys(follow))[: seed.get("max_unterseiten", 15)]:
            if not http.allowed_by_robots(sub):
                continue
            try:
                rs = http.request("GET", sub)
                if rs.status_code == 200 and "html" in rs.headers.get("Content-Type", ""):
                    for a in BeautifulSoup(rs.content, "lxml").find_all("a", href=True):
                        add(urljoin(rs.url, a["href"]), a.get_text(" ", strip=True) or a.get("title", ""), sub, gem, kt, "Unterseite")
            except Exception:
                continue
        log(f"  Discovery {url}: {len(cands) - n0} Kandidaten")

    for sm in seeds.get("sitemaps", []):
        base, gem, kt = sm["basis"], sm.get("gemeinde", ""), sm.get("kanton", "")
        queue, seen, n0 = http.sitemaps(base), set(), len(cands)
        while queue and len(seen) < 25:
            smurl = queue.pop(0)
            if smurl in seen:
                continue
            seen.add(smurl)
            try:
                r = http.request("GET", smurl)
                if r.status_code != 200:
                    continue
                locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", r.text)
            except Exception:
                continue
            for loc in locs[:20000]:
                if loc.endswith(".xml") or "sitemap" in loc.lower():
                    queue.append(loc)
                else:
                    add(loc, "", smurl, gem, kt, "Sitemap")
        log(f"  Sitemap {base}: {len(cands) - n0} Kandidaten aus {len(seen)} Sitemap-Dateien")

    key = os.environ.get("BRAVE_SEARCH_API_KEY")
    if key and seeds.get("suchanfragen"):
        for q in seeds["suchanfragen"]:
            try:
                r = http.request("GET", "https://api.search.brave.com/res/v1/web/search",
                                 params={"q": q["q"], "count": 20, "country": "CH", "search_lang": "de"},
                                 headers={"X-Subscription-Token": key, "Accept": "application/json"})
                for item in r.json().get("web", {}).get("results", []):
                    add(item.get("url", ""), item.get("title", ""), f"Brave: {q['q']}", q.get("gemeinde", ""), q.get("kanton", ""), "Such-API")
            except Exception as exc:
                log(f"  Brave-Suche fehlgeschlagen ({q['q']}): {exc}")
    elif seeds.get("suchanfragen"):
        log("  Keine Such-API konfiguriert (BRAVE_SEARCH_API_KEY fehlt) – Fallback: Einstiegsseiten und Sitemaps")
    return list(cands.values())


# --------------------------------------------------------------------------------------
# Katalog aufbauen
# --------------------------------------------------------------------------------------
def read_catalogue(wb) -> list[dict]:
    ws = wb["Gesamtübersicht"]
    header = [c.value for c in ws[1]]
    if "ID" in header:  # bereits verarbeitete Datei
        keys = {h: k for k, h, _ in COLS}
        rows = []
        for r in ws.iter_rows(min_row=2):
            rec = {keys[h]: c.value for h, c in zip(header, r) if h in keys}
            if rec.get("id"):
                rows.append(rec)
        return rows
    rows = []
    for r in ws.iter_rows(min_row=2):
        rec = {}
        for h, c in zip(header, r):
            if h in HEADER_TO_KEY:
                rec[HEADER_TO_KEY[h]] = c.value
                if HEADER_TO_KEY[h] == "url" and c.hyperlink is not None and c.hyperlink.target:
                    rec["url"] = c.hyperlink.target
        if any(rec.values()):
            rows.append(rec)
    return rows


def assign_ids(rows: list[dict]) -> None:
    counter = Counter()
    for rec in rows:
        if rec.get("ebene") == "Bund":
            pre = "CH"
        elif rec.get("ebene") == "Kanton":
            pre = KANTON_KUERZEL[rec["kanton"]]
        else:
            pre = GEMEINDEN[rec["gemeinde"]]["kuerzel"]
        counter[(pre, rec["dim"])] += 1
        rec["id"] = f"{pre}-{rec['dim']}-{counter[(pre, rec['dim'])]:02d}"
        rec["_original"] = True


def places_for(rec: dict) -> list[str]:
    if rec.get("ort") is not None:
        return rec["ort"] if isinstance(rec["ort"], list) else [rec["ort"]]
    if rec.get("ebene") == "Gemeinde":
        return [rec["gemeinde"]]
    if rec.get("ebene") == "Kanton":
        return {"Uri": ["Uri"], "Basel-Landschaft": ["Basel-Landschaft", "Baselland"], "St. Gallen": ["St. Gallen", "St.Gallen"]}[rec["kanton"]]
    return []


def apply_curation(rows: list[dict], cur: dict) -> list[dict]:
    by_id = {r["id"]: r for r in rows}
    for rid, upd in cur.get("bestehende_zeilen", {}).items():
        if rid not in by_id:
            raise SystemExit(f"Kuratierung verweist auf unbekannte ID {rid}")
        rec = by_id[rid]
        if "url" in upd and upd["url"] != rec.get("url"):
            note = f"{cur.get('stand', TODAY.isoformat())}: Link ersetzt (vorher {rec.get('url')}). Grund: {upd.get('grund', '–')}"
            rec["aenderung"] = "; ".join(x for x in (rec.get("aenderung"), note) if x)
            rec["_alte_url"] = rec.get("url")
        elif upd.get("grund"):
            note = f"{cur.get('stand', TODAY.isoformat())}: {upd['grund']}"
            rec["aenderung"] = "; ".join(x for x in (rec.get("aenderung"), note) if x)
        for k, v in upd.items():
            if k != "grund":
                rec[k] = v
    existing = set(by_id)
    for new in cur.get("neue_quellen", []):
        if new["id"] in existing:
            raise SystemExit(f"Doppelte ID {new['id']}")
        existing.add(new["id"])
        rec = {k: v for k, v in new.items()}
        rec.setdefault("land", "Schweiz")
        rec.setdefault("tragfaehigkeit", "Noch nicht bewertet")
        rec.setdefault("aktualitaet", cur.get("stand", TODAY.isoformat()))
        rec.setdefault("herkunft", f"Webrecherche {cur.get('stand', '')}; Linkprüfung GitHub Actions")
        rec.setdefault("pruefstatus", PRUEFSTATUS[0])
        rec["aenderung"] = f"{cur.get('stand', TODAY.isoformat())}: neu aufgenommen"
        rec["_neu"] = True
        rows.append(rec)
    return rows


def derive_fields(rows: list[dict], results: dict[str, dict]) -> None:
    url_ids = defaultdict(list)
    for rec in rows:
        url_ids[rec.get("url")].append(rec["id"])
    for rec in rows:
        res = results.get(rec.get("url")) or {}
        rec["linkstatus"] = res.get("linkstatus") or "Nicht prüfbar"
        rec["http"] = res.get("http", "")
        rec["final_url"] = res.get("final_url") if res.get("final_url") and res.get("final_url") != rec.get("url") else ""
        rec["dateityp"] = res.get("dateityp", "")
        rec["inhalt"] = res.get("inhalt") or "Offen"
        detail = res.get("inhalt_detail") or res.get("fehler") or "Nicht geprüft (keine Netzverbindung)"
        if res.get("fehler") and res.get("inhalt_detail"):
            detail = res["fehler"] + "; " + res["inhalt_detail"]
        rec["inhalt_detail"] = detail
        rec["erkannter_titel"] = res.get("titel", "")
        rec["jahre"] = res.get("jahre", "")
        rec["linkstabilitaet"] = res.get("stabilitaet") or link_stability(rec.get("url") or "")
        rec["letzte_pruefung"] = res.get("geprueft", "")
        if rec["linkstatus"] in ("Verifiziert", "Weiterleitung"):
            rec["verfuegbarkeit"] = VERFUEGBARKEIT[0] if rec["inhalt"] == "Bestätigt" else VERFUEGBARKEIT[1]
        else:
            rec["verfuegbarkeit"] = VERFUEGBARKEIT[4]
        others = [i for i in url_ids[rec.get("url")] if i != rec["id"]]
        rec["gleiche_quelle"] = ", ".join(others)
        # Tragfähigkeit nur mit Begründung; Standard bleibt «Noch nicht bewertet»
        if rec.get("tragfaehigkeit") in (None, "", "Noch nicht bewertet"):
            rec["tragfaehigkeit"] = "Noch nicht bewertet"
            rec.setdefault("begruendung", "Keine Einstufung: Kennzahlen/Befunde noch nicht ausgewertet; Schwellen der Bewertungslogik noch nicht validiert.")
        elif not rec.get("begruendung"):
            raise SystemExit(f"{rec['id']}: Tragfähigkeit ohne Bewertungsbegründung")
        rec.setdefault("pruefnachweis", "Belegt Existenz und Zugänglichkeit der Quelle; inhaltliche Aussagen erst nach Auswertung.")
        if not rec.get("anfrage"):
            rec["anfrage"] = "Ja" if rec.get("ebene") == "Gemeinde" and rec.get("dim") in ("C2", "C3", "C4") else "Nein"
        if not rec.get("zustaendig"):
            rec["zustaendig"] = {
                "Bund": rec.get("herausgeber") or "Bund",
                "Kanton": rec.get("herausgeber") or "Kanton",
            }.get(rec.get("ebene"), f"Gemeindeverwaltung {rec.get('gemeinde')}")
        if not rec.get("bearbeitung"):
            rec["bearbeitung"] = "In Prüfung" if rec["inhalt"] == "Bestätigt" else "Offen"
        if not rec.get("einheit"):
            rec["einheit"] = rec.get("bezugsjahr") or ""
        if rec["linkstatus"] == "Nicht prüfbar" and "manuell im Browser" not in (rec.get("hinweis") or ""):
            rec["hinweis"] = "; ".join(x for x in (rec.get("hinweis"), "Automatisch nicht prüfbar – manuell im Browser prüfen") if x)
        if rec["linkstatus"] == "Fehler" and "Link defekt" not in (rec.get("hinweis") or ""):
            rec["hinweis"] = "; ".join(x for x in (rec.get("hinweis"), "Link defekt – Ersatz recherchieren") if x)
        if rec.get("linkstatus") in ("Verifiziert", "Weiterleitung"):
            rec["aktualitaet"] = (res.get("geprueft") or "")[:10] or rec.get("aktualitaet")


# --------------------------------------------------------------------------------------
# Excel schreiben
# --------------------------------------------------------------------------------------
EBENE_FILL = {"Bund": "FFDCE6F0", "Kanton": "FFE2F0EC", "Gemeinde": "FFFBF0DC"}
ORDER_EBENE = {"Bund": 0, "Kanton": 1, "Gemeinde": 2}
ORDER_KANTON = {"Alle": 0, "Uri": 1, "Basel-Landschaft": 2, "St. Gallen": 3}
ORDER_GEM = {"Alle": 0, "Seelisberg": 1, "Münchenstein": 2, "Wil": 3}


def sort_key(rec):
    return (ORDER_EBENE.get(rec.get("ebene"), 9), ORDER_KANTON.get(rec.get("kanton"), 9),
            ORDER_GEM.get(rec.get("gemeinde"), 9), rec.get("dim", ""), rec["id"])


class Styles:
    def __init__(self, ws):
        self.head_font = copy.copy(ws["A1"].font)
        self.head_fill = copy.copy(ws["A1"].fill)
        self.head_align = copy.copy(ws["A1"].alignment)
        self.body_font = copy.copy(ws["A2"].font)
        self.band_fill = copy.copy(ws["A2"].fill)
        self.body_align = copy.copy(ws["A2"].alignment)
        self.link_font = copy.copy(ws["L2"].font)
        self.head_height = ws.row_dimensions[1].height or 36
        self.body_height = ws.row_dimensions[2].height or 43


def clear_sheet(ws):
    ws.delete_rows(1, ws.max_row + 1)
    for name in list(ws.tables.keys()):
        del ws.tables[name]
    ws.data_validations.dataValidation = []
    ws.conditional_formatting = type(ws.conditional_formatting)()
    ws.auto_filter.ref = None


def add_list_validation(ws, key_or_col, values, last_row, cols_map=None):
    col = key_or_col if cols_map is None else cols_map[key_or_col]
    dv = DataValidation(type="list", formula1='"' + ",".join(values) + '"', allow_blank=True)
    dv.add(f"{col}2:{col}{max(last_row, 500)}")
    ws.add_data_validation(dv)


def write_table(ws, st: Styles, cols, rows, table_name, extra_formula=None):
    ws.append([h for _, h, _ in cols] + ([extra_formula[0]] if extra_formula else []))
    for i, rec in enumerate(rows, start=2):
        ws.append([rec.get(k, "") if rec.get(k) is not None else "" for k, _, _ in cols])
        if extra_formula:
            ws.cell(i, len(cols) + 1, extra_formula[1](i))
    ncols = len(cols) + (1 if extra_formula else 0)
    for c in range(1, ncols + 1):
        cell = ws.cell(1, c)
        cell.font, cell.fill, cell.alignment = copy.copy(st.head_font), copy.copy(st.head_fill), copy.copy(st.head_align)
    keys = [k for k, _, _ in cols]
    for r in range(2, len(rows) + 2):
        band = (r % 2 == 0)
        for c in range(1, ncols + 1):
            cell = ws.cell(r, c)
            cell.font = copy.copy(st.body_font)
            cell.alignment = copy.copy(st.body_align)
            if band:
                cell.fill = copy.copy(st.band_fill)
        rec = rows[r - 2]
        for k in ("url", "fundstelle", "final_url"):
            if k in keys and rec.get(k):
                cell = ws.cell(r, keys.index(k) + 1)
                cell.hyperlink = rec[k]
                cell.font = copy.copy(st.link_font)
        if "ebene" in keys and rec.get("ebene") in EBENE_FILL:
            ws.cell(r, keys.index("ebene") + 1).fill = PatternFill("solid", fgColor=EBENE_FILL[rec["ebene"]])
            ws.cell(r, keys.index("ebene") + 1).font = Font(name=st.body_font.name, size=st.body_font.sz, bold=True, color=st.body_font.color)
        ws.row_dimensions[r].height = st.body_height
    ws.row_dimensions[1].height = st.head_height
    for i, (_, _, w) in enumerate(cols, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    if extra_formula:
        ws.column_dimensions[get_column_letter(ncols)].width = 26
    ref = f"A1:{get_column_letter(ncols)}{max(len(rows) + 1, 2)}"
    tab = Table(displayName=table_name, ref=ref)
    tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showFirstColumn=False, showLastColumn=False,
                                        showRowStripes=False, showColumnStripes=False)
    ws.add_table(tab)


def add_catalogue_validations(ws, n):
    m = {k: col_letter(k) for k in COL_KEYS}
    add_list_validation(ws, "ebene", ["Bund", "Kanton", "Gemeinde"], n, m)
    add_list_validation(ws, "dim", ["C1", "C2", "C3", "C4", "C5"], n, m)
    add_list_validation(ws, "tragfaehigkeit", TRAGFAEHIGKEIT, n, m)
    add_list_validation(ws, "confidence", CONFIDENCE, n, m)
    add_list_validation(ws, "pruefstatus", PRUEFSTATUS, n, m)
    add_list_validation(ws, "linkstatus", LINKSTATUS, n, m)
    add_list_validation(ws, "inhalt", INHALT, n, m)
    add_list_validation(ws, "verfuegbarkeit", VERFUEGBARKEIT, n, m)
    add_list_validation(ws, "anfrage", ["Ja", "Nein"], n, m)
    add_list_validation(ws, "bearbeitung", BEARBEITUNG, n, m)
    rng = lambda k: f"{col_letter(k)}2:{col_letter(k)}{max(n, 500)}"
    colors = {"Verifiziert": "FFE2EFDA", "Weiterleitung": "FFFFF2CC", "Fehler": "FFF8D7DA", "Nicht prüfbar": "FFEDEDED",
              "Bestätigt": "FFE2EFDA", "Teilweise bestätigt": "FFFFF2CC", "Offen": "FFEDEDED"}
    for k, vals in (("linkstatus", LINKSTATUS), ("inhalt", INHALT)):
        for v in vals:
            ws.conditional_formatting.add(rng(k), CellIsRule(operator="equal", formula=[f'"{v}"'],
                                                             fill=PatternFill("solid", fgColor=colors[v])))


def view_rows(rows, gemeinde):
    kanton = GEMEINDEN[gemeinde]["kanton"]
    return [r for r in rows if r.get("ebene") == "Bund"
            or (r.get("ebene") == "Kanton" and r.get("kanton") == kanton)
            or (r.get("ebene") == "Gemeinde" and r.get("gemeinde") == gemeinde)]


def abgleich_formula(row):
    g = "'Gesamtübersicht'"
    idc = col_letter("id")
    match = f"MATCH(${idc}{row},{g}!${idc}:${idc},0)"
    checks = []
    for k in ("titel", "url", "linkstatus", "inhalt", "tragfaehigkeit"):
        c = col_letter(k)
        checks.append(f"INDEX({g}!${c}:${c},{match})&\"\"=${c}{row}&\"\"")
    return (f"=IF(ISNA({match}),\"ID fehlt in Gesamtübersicht\","
            f"IF(AND({','.join(checks)}),\"OK\",\"Abweichung – Ansicht neu erzeugen\"))")


def write_views(wb, rows, st):
    for gem, meta in GEMEINDEN.items():
        ws = wb[meta["sheet"]]
        clear_sheet(ws)
        vr = view_rows(rows, gem)
        write_table(ws, st, COLS, vr, meta["table"], extra_formula=("Abgleich mit Gesamtübersicht", abgleich_formula))
        add_catalogue_validations(ws, len(vr) + 1)
        ws.freeze_panes = "H2"


def write_hinweise(wb, cur, stats):
    ws = wb["Hinweise"]
    base_font = copy.copy(ws["A2"].font)
    bold = copy.copy(ws["A2"].font)
    bold = Font(name=bold.name, size=bold.sz, bold=True, color=bold.color)
    # vorhandene Einträge bleiben; ab Zeile 14 Abschnitt zur Verifikation (wird bei jedem Lauf neu geschrieben)
    for r in range(14, ws.max_row + 1):
        for c in range(1, 4):
            ws.cell(r, c).value = None
    ws["B1"] = f"Stand: {TODAY.strftime('%d.%m.%Y')} (verifizierte Fassung)"
    g = "'Gesamtübersicht'"
    eb, kt, gm = col_letter("ebene"), col_letter("kanton"), col_letter("gemeinde")
    lines = [
        ("Verifikation", "Alle URLs werden per Skript scripts/verify_c_sources.py (GitHub Actions) geprüft: Syntax, DNS, HTTP (HEAD, GET-Fallback), Weiterleitungen, Dateityp, Titel/Text gegen erwartete Schlüsselwörter und Ort. HTTP 200 allein gilt nicht als Verifikation."),
        ("Linkstatus", "Verifiziert = erreichbar ohne Umleitung; Weiterleitung = erreichbar nach Umleitung (Finale URL beachten); Fehler = 4xx/5xx/DNS/Fehlerseite; Nicht prüfbar = Zugriff verweigert, gedrosselt oder kein Netz."),
        ("Inhaltsprüfung", "Bestätigt = alle erwarteten Schlüsselwörter und Ort/Zuständigkeit im Titel oder Text gefunden; Teilweise bestätigt = nur ein Teil; Offen = kein auswertbarer Text oder keine Übereinstimmung. Automatischer Abgleich, keine fachliche Auswertung."),
        ("Quellenverfügbarkeit", "; ".join(VERFUEGBARKEIT) + ". Die Kategorien 3 und 4 werden im Blatt Gemeindeanfragen geführt."),
        ("Tragfähigkeit", "Weiterhin «Noch nicht bewertet»: ein verifizierter Link ist kein Beleg für institutionelle Tragfähigkeit. Einstufungen nur mit Bewertungsbegründung (Skript bricht sonst ab)."),
        ("Gemeindeblätter", "Seelisberg, Münchenstein und Wil sind generierte Ansichten der Gesamtübersicht (Bund + eigener Kanton + eigene Gemeinde). Nur in der Gesamtübersicht bearbeiten, danach «python3 scripts/verify_c_sources.py --sync-only <Datei>» ausführen. Die Spalte «Abgleich mit Gesamtübersicht» zeigt Abweichungen per Formel an."),
        ("Recherche-Kandidaten", "Automatisch gefundene Dokumentlinks (Einstiegsseiten, Sitemaps, optional Such-API). Ungeprüft und nicht kuratiert – erst nach Sichtung in die Gesamtübersicht übernehmen."),
        ("Kennzahlen Lauf", f"Geprüfte URLs: {stats['urls']}; verifiziert/weitergeleitet: {stats['ok']}; Fehler: {stats['fehler']}; nicht prüfbar: {stats['np']}; Inhalt bestätigt: {stats['bestaetigt']}; neue Quellen: {stats['neu']}; ersetzte Links: {stats['ersetzt']}."),
    ]
    r = 14
    for a, b in lines:
        ws.cell(r, 1, a).font = bold
        ws.cell(r, 2, b).font = base_font
        ws.cell(r, 2).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(r, 1).alignment = Alignment(wrap_text=True, vertical="top")
        r += 1
    ws.cell(r, 1, "Konsistenz (Formel)").font = bold
    ws.cell(r, 2, "Soll = Zeilen in der Gesamtübersicht, die zur Gemeinde gehören; Ist = Zeilen im Gemeindeblatt.").font = base_font
    r += 1
    for gem, meta in GEMEINDEN.items():
        soll = (f"COUNTIF({g}!${eb}:${eb},\"Bund\")+COUNTIFS({g}!${eb}:${eb},\"Kanton\",{g}!${kt}:${kt},\"{meta['kanton']}\")"
                f"+COUNTIFS({g}!${eb}:${eb},\"Gemeinde\",{g}!${gm}:${gm},\"{gem}\")")
        ist = f"COUNTA('{meta['sheet']}'!$A:$A)-1"
        ws.cell(r, 1, gem).font = bold
        ws.cell(r, 2, f'="Soll "&({soll})&" / Ist "&({ist})&" – "&IF(({soll})=({ist}),"OK","ABWEICHUNG: Ansicht neu erzeugen")').font = base_font
        r += 1


def write_legende(wb):
    name = "Legende"
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)
    ref = wb["Bewertungslogik"]
    hf, hfill = copy.copy(ref["A1"].font), copy.copy(ref["A1"].fill)
    bf = copy.copy(ref["A2"].font)
    ws.append(["Feld", "Wert", "Bedeutung"])
    data = [
        ("Linkstatus", "Verifiziert", "HTTP 2xx, keine Umleitung auf eine andere Adresse."),
        ("Linkstatus", "Weiterleitung", "HTTP 2xx nach Umleitung; Finale URL ersetzt ggf. den Link."),
        ("Linkstatus", "Fehler", "Syntaxfehler, DNS-Fehler, HTTP 4xx/5xx, Zeitüberschreitung oder Fehlerseite mit HTTP 200."),
        ("Linkstatus", "Nicht prüfbar", "Zugriff verweigert (401/403/451), gedrosselt (429) oder keine Netzverbindung. Keine Umgehung versucht."),
        ("Inhaltsprüfung", "Bestätigt", "Alle erwarteten Schlüsselwörter sowie Ort/Zuständigkeit im Dokumenttitel oder -text gefunden."),
        ("Inhaltsprüfung", "Teilweise bestätigt", "Nur ein Teil der Schlüsselwörter oder nur der Ort gefunden."),
        ("Inhaltsprüfung", "Offen", "Kein auswertbarer Text (JavaScript-Seite, Scan) oder keine Übereinstimmung."),
        ("Quellenverfügbarkeit", VERFUEGBARKEIT[0], "Link erreichbar und Dokumentidentität automatisiert bestätigt."),
        ("Quellenverfügbarkeit", VERFUEGBARKEIT[1], "Link erreichbar, Identität nicht oder nur teilweise bestätigt."),
        ("Quellenverfügbarkeit", VERFUEGBARKEIT[2], "Recherche ohne Treffer (nur in Gemeindeanfragen)."),
        ("Quellenverfügbarkeit", VERFUEGBARKEIT[3], "Information liegt erkennbar nur intern vor (nur in Gemeindeanfragen)."),
        ("Quellenverfügbarkeit", VERFUEGBARKEIT[4], "Link defekt, gesperrt oder nicht prüfbar."),
        ("Linkstabilität", "Hoch / Mittel / Gering", "Heuristik nach URL-Typ: ELI-Permalinks und Erlassnummern hoch; CMS-Dokumentlinks mittel; Session-/Temp-Downloads gering."),
        ("Bearbeitungsstatus", "Offen / In Prüfung / Abgeschlossen", "In Prüfung = Dokument identifiziert, Auswertung offen; Abgeschlossen erst nach fachlicher Auswertung (manuell)."),
        ("Reifegrad / Tragfähigkeit", "Noch nicht bewertet", "Standard. Hoch/Mittel/Gering nur mit Bewertungsbegründung gemäss Blatt Bewertungslogik."),
        ("Confidence", "Hoch / Mittel / Niedrig", "Aussagekraft der Katalogzeile (nicht Gemeindequalität). Bestehende Werte unverändert übernommen; neue Zeilen: Hoch = direktes amtliches Dokument, Mittel = amtliche Übersichtsseite."),
        ("ID", "XX-Cn-nn", "CH/UR/BL/SG = Bund/Kantone; SEE/MUE/WIL = Gemeinden; Cn = Dimension; nn = laufende Nummer. IDs bleiben stabil."),
    ]
    for d in data:
        ws.append(list(d))
    for c in range(1, 4):
        ws.cell(1, c).font, ws.cell(1, c).fill = copy.copy(hf), copy.copy(hfill)
    for r in range(2, len(data) + 2):
        for c in range(1, 4):
            ws.cell(r, c).font = copy.copy(bf)
            ws.cell(r, c).alignment = Alignment(wrap_text=True, vertical="top")
            if r % 2 == 0:
                ws.cell(r, c).fill = PatternFill("solid", fgColor="FFF4F8FA")
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 100
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:C{len(data) + 1}"


def write_bewertungslogik(wb):
    ws = wb["Bewertungslogik"]
    ws.cell(1, 8, "Anwendung im verifizierten Stand")
    ws.cell(1, 8).font = copy.copy(ws["G1"].font)
    ws.cell(1, 8).fill = copy.copy(ws["G1"].fill)
    ws.cell(1, 8).alignment = copy.copy(ws["G1"].alignment)
    notes = {
        2: "Nicht angewendet: Kennzahlen (Selbstfinanzierungsgrad, Nettoschuld/Einw., Investitionsanteil) noch nicht aus den verifizierten Jahresrechnungen extrahiert; Peer-Gruppe Kanton × Grössenklasse noch nicht gebildet.",
        3: "Nicht angewendet: kommunales Grundeigentum ist öffentlich nicht belegt (ÖBA-Zonen ≠ Eigentum). Liegenschaftsverzeichnis per Gemeindeanfrage.",
        4: "Nicht angewendet: Gemeindeordnungen/Reglemente teilweise verifiziert; Kooperationsverträge nicht öffentlich vollständig.",
        5: "Nicht angewendet: Organigramme belegen Struktur, nicht Kompetenz/Kapazität. Stellenplan und Projektressourcen per Gemeindeanfrage.",
        6: "Nicht angewendet: Leitbild/Mitwirkung belegt keine Akzeptanz. Beschlüsse und Abstimmungsergebnisse noch auszuwerten.",
    }
    for r, t in notes.items():
        c = ws.cell(r, 8, t)
        c.font = copy.copy(ws.cell(r, 7).font)
        c.fill = copy.copy(ws.cell(r, 7).fill)
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["H"].width = 60
    ws.auto_filter.ref = "A1:H6"


def write_anfragen(wb, cur, rows):
    ws = wb["Gemeindeanfragen"]
    st_head = (copy.copy(ws["A1"].font), copy.copy(ws["A1"].fill), copy.copy(ws["A1"].alignment))
    body_font, band = copy.copy(ws["A2"].font), copy.copy(ws["A2"].fill)
    old = [[c.value for c in r] for r in ws.iter_rows(min_row=2) if any(c.value for c in r)]
    header = ["Anfrage-ID", "Gemeinde", "C-Dimension", "Benötigte Lieferung", "Warum nötig", "Priorität", "Status",
              "Quellenstatus (Recherche)", "Recherchebefund", "Bezug Katalog-ID", "Präzisierte Frage an die Gemeinde",
              "Zuständige Stelle (vermutet)"]
    widths = [12, 16, 13, 60, 40, 11, 12, 34, 60, 22, 70, 30]
    by_id = {r["id"]: r for r in rows}
    anf_cur = cur.get("gemeindeanfragen", {})
    out = []
    kz = {g: m["kuerzel"] for g, m in GEMEINDEN.items()}
    cnt = Counter()
    for vals in old:
        gem, dim = vals[0], vals[1]
        cnt[gem] += 1
        aid = f"A-{kz[gem]}-{cnt[gem]:02d}"
        rec = OrderedDict(zip(header, [aid] + list(vals[:6]) + [""] * 5))
        rec.update(anf_cur.get("bestehend", {}).get(aid, {}))
        out.append(rec)
    for new in anf_cur.get("neu", []):
        rec = OrderedDict((h, "") for h in header)
        rec.update(new)
        out.append(rec)
    # Quellenstatus aus den Prüfergebnissen der referenzierten Katalogzeilen ableiten,
    # sofern nicht kuratiert festgelegt
    for rec in out:
        refs = [x.strip() for x in str(rec.get("Bezug Katalog-ID") or "").split(",") if x.strip()]
        missing = [x for x in refs if x not in by_id]
        if missing:
            raise SystemExit(f"Gemeindeanfrage {rec['Anfrage-ID']} verweist auf unbekannte IDs {missing}")
        if not rec.get("Quellenstatus (Recherche)"):
            stati = [by_id[x]["verfuegbarkeit"] for x in refs]
            if not refs:
                rec["Quellenstatus (Recherche)"] = VERFUEGBARKEIT[2]
            elif VERFUEGBARKEIT[0] in stati:
                rec["Quellenstatus (Recherche)"] = VERFUEGBARKEIT[0]
            elif VERFUEGBARKEIT[1] in stati:
                rec["Quellenstatus (Recherche)"] = VERFUEGBARKEIT[1]
            else:
                rec["Quellenstatus (Recherche)"] = VERFUEGBARKEIT[4]
        if not rec.get("Zuständige Stelle (vermutet)"):
            rec["Zuständige Stelle (vermutet)"] = f"Gemeindeverwaltung {rec['Gemeinde']}"
    order = {g: i for i, g in enumerate(GEMEINDEN)}
    out.sort(key=lambda r: (order.get(r["Gemeinde"], 9), str(r["C-Dimension"]), r["Anfrage-ID"]))
    ws.delete_rows(1, ws.max_row + 1)
    ws.data_validations.dataValidation = []
    ws.append(header)
    for rec in out:
        ws.append([rec.get(h, "") for h in header])
    for c in range(1, len(header) + 1):
        ws.cell(1, c).font, ws.cell(1, c).fill, ws.cell(1, c).alignment = (copy.copy(x) for x in st_head)
        ws.column_dimensions[get_column_letter(c)].width = widths[c - 1]
    for r in range(2, len(out) + 2):
        for c in range(1, len(header) + 1):
            cell = ws.cell(r, c)
            cell.font = copy.copy(body_font)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if r % 2 == 0:
                cell.fill = copy.copy(band)
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(header))}{len(out) + 1}"
    for col, vals in (("F", ["Hoch", "Mittel", "Niedrig"]), ("G", ["Offen", "Angefragt", "Erhalten", "Erledigt", "Entfällt"]),
                      ("H", VERFUEGBARKEIT), ("C", ["C1", "C2", "C3", "C4", "C5", "C1, C2", "C3, C4", "C3, C5", "C4, C5"])):
        dv = DataValidation(type="list", formula1='"' + ",".join(vals) + '"', allow_blank=True)
        dv.add(f"{col}2:{col}500")
        ws.add_data_validation(dv)
    return out


def write_candidates(wb, cands, known_urls):
    name = "Recherche-Kandidaten"
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name, index=wb.sheetnames.index("Gemeindeanfragen") + 1)
    ref = wb["Gemeindeanfragen"]
    header = ["Gemeinde", "Kanton", "Dimension (Stichwort)", "Dokumentlink", "Ankertext", "Dokumentdatei", "Gefunden auf", "Quelle", "Bereits im Katalog", "Status"]
    ws.append(header)
    rel = [c for c in cands if c["dokument"] == "ja" or c["quelle"] != "Sitemap"]
    rel.sort(key=lambda c: (c["gemeinde"], c["dimensionen"], c["url"]))
    for c in rel:
        ws.append([c["gemeinde"], c["kanton"], c["dimensionen"], c["url"], c["ankertext"], c["dokument"], c["gefunden_auf"],
                   c["quelle"], "Ja" if c["url"] in known_urls else "Nein", "Ungeprüft – nicht kuratiert"])
    for c in range(1, len(header) + 1):
        ws.cell(1, c).font, ws.cell(1, c).fill = copy.copy(ref["A1"].font), copy.copy(ref["A1"].fill)
        ws.cell(1, c).alignment = copy.copy(ref["A1"].alignment)
    bf = copy.copy(ref["A2"].font)
    for r in range(2, ws.max_row + 1):
        for c in range(1, len(header) + 1):
            ws.cell(r, c).font = copy.copy(bf)
        u = ws.cell(r, 4)
        if u.value:
            u.hyperlink = u.value
            u.font = Font(name=bf.name, size=bf.sz, color="FF087E8B", underline="single")
    for i, w in enumerate([14, 16, 14, 70, 45, 10, 45, 13, 12, 24], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:J{max(ws.max_row, 2)}"
    return len(rel)


def build_workbook(rows, cur, cands, stats, src=INPUT_XLSX, out=OUTPUT_XLSX):
    wb = openpyxl.load_workbook(src)
    ws = wb["Gesamtübersicht"]
    st = Styles(ws) if "ID" not in [c.value for c in ws[1]] else Styles(ws)
    rows.sort(key=sort_key)
    clear_sheet(ws)
    write_table(ws, st, COLS, rows, "KatasterGesamt")
    add_catalogue_validations(ws, len(rows) + 1)
    ws.freeze_panes = "H2"
    write_views(wb, rows, st)
    anfragen = write_anfragen(wb, cur, rows)
    n_cands = write_candidates(wb, cands, {r.get("url") for r in rows})
    write_hinweise(wb, cur, stats)
    write_bewertungslogik(wb)
    write_legende(wb)
    wb.active = wb.sheetnames.index("Gesamtübersicht")
    wb.save(out)
    return anfragen, n_cands


def sync_only(path: Path):
    """Gemeindeblätter einer manuell bearbeiteten Datei aus der Gesamtübersicht neu erzeugen."""
    wb = openpyxl.load_workbook(path)
    ws = wb["Gesamtübersicht"]
    rows = read_catalogue(wb)
    # Hyperlinks/Stile aus der Gesamtübersicht übernehmen
    st = Styles.__new__(Styles)
    st.head_font, st.head_fill, st.head_align = copy.copy(ws["A1"].font), copy.copy(ws["A1"].fill), copy.copy(ws["A1"].alignment)
    st.body_font, st.band_fill, st.body_align = copy.copy(ws["C2"].font), copy.copy(ws["C2"].fill), copy.copy(ws["C2"].alignment)
    st.link_font = copy.copy(ws[f"{col_letter('url')}2"].font)
    st.head_height, st.body_height = ws.row_dimensions[1].height or 36, ws.row_dimensions[2].height or 43
    write_views(wb, rows, st)
    wb.save(path)
    print(f"Gemeindeblätter in {path} aus {len(rows)} Zeilen der Gesamtübersicht neu erzeugt.")


# --------------------------------------------------------------------------------------
# Berichte
# --------------------------------------------------------------------------------------
def write_reports(rows, results, cands, anfragen, stats, cur, discovery_log):
    REPORT_DIR.mkdir(exist_ok=True)
    fields = ["ID", "Ebene", "Kanton", "Gemeinde", "C-Dimension", "Dokumenttitel", "Ursprüngliche URL", "Geprüfte URL",
              "Finale URL", "HTTP-Status", "Prüfmethode", "Ergebnis (Linkstatus)", "Fehler", "Dateityp", "Erkannter Titel",
              "Inhaltsprüfung", "Inhaltsprüfung – Nachweis", "Erkannte Jahresangaben", "Linkstabilität", "Weiterleitungskette", "Prüfdatum"]
    with open(REPORT_DIR / "link_validation.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(fields)
        for rec in rows:
            res = results.get(rec.get("url"), {})
            w.writerow([rec["id"], rec.get("ebene"), rec.get("kanton"), rec.get("gemeinde"), rec.get("dim"), rec.get("titel"),
                        rec.get("_alte_url") or rec.get("url"), rec.get("url"), res.get("final_url", ""), res.get("http", ""),
                        res.get("methode", ""), rec.get("linkstatus"), res.get("fehler", ""), res.get("dateityp", ""),
                        res.get("titel", ""), rec.get("inhalt"), rec.get("inhalt_detail"), res.get("jahre", ""),
                        rec.get("linkstabilitaet"), res.get("redirect_kette", ""), res.get("geprueft", "")])
    # Alte (ersetzte) URLs separat prüfen und dokumentieren
    with open(REPORT_DIR / "link_validation.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    with open(REPORT_DIR / "discovery_kandidaten.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        keys = ["gemeinde", "kanton", "dimensionen", "url", "ankertext", "dokument", "gefunden_auf", "quelle"]
        w.writerow(keys)
        for c in cands:
            w.writerow([c[k] for k in keys])
    write_markdown_report(rows, results, cands, anfragen, stats, cur, discovery_log)


def write_markdown_report(rows, results, cands, anfragen, stats, cur, discovery_log):
    L = []
    run = os.environ.get("GITHUB_RUN_ID")
    repo = os.environ.get("GITHUB_REPOSITORY")
    L.append("# Recherchebericht C-Grundlagenkataster\n")
    L.append(f"Erzeugt am {dt.datetime.now().strftime('%d.%m.%Y %H:%M')} durch `scripts/verify_c_sources.py`"
             + (f" im GitHub-Actions-Lauf [{run}](https://github.com/{repo}/actions/runs/{run})." if run else " (lokaler Lauf)."))
    L.append(f"Kuratierungsstand der Quellenliste: {cur.get('stand', '–')}.\n")
    L.append("> Grundsatz: Nachvollziehbarkeit vor scheinbarer Vollständigkeit. HTTP 200 gilt nicht als Verifikation; "
             "«Bestätigt» heisst, dass erwartete Schlüsselwörter und Ort im Dokument gefunden wurden. "
             "Tragfähigkeit wurde nirgends eingestuft.\n")
    L.append("## 1 Kennzahlen\n")
    L.append("| Kennzahl | Anzahl |\n|---|---:|")
    for k, v in (("Katalogzeilen gesamt", stats["zeilen"]), ("Davon ursprüngliche Zeilen", stats["original"]),
                 ("Geprüfte eindeutige URLs (inkl. ersetzter Alt-Links)", stats["urls"]),
                 ("Erreichbar ohne Umleitung (Verifiziert)", stats["verif"]), ("Erreichbar nach Weiterleitung", stats["weiter"]),
                 ("Fehler", stats["fehler"]), ("Nicht prüfbar", stats["np"]),
                 ("Katalogzeilen mit Inhalt «Bestätigt»", stats["bestaetigt"]), ("… «Teilweise bestätigt»", stats["teilweise"]),
                 ("… «Offen»", stats["offen"]), ("Ersetzte Links", stats["ersetzt"]), ("Neu aufgenommene Dokumente", stats["neu"]),
                 ("Weiterhin offene Quellen (Inhalt nicht bestätigt oder Link nicht OK)", stats["offene_quellen"]),
                 ("Automatisch gefundene Recherche-Kandidaten", len(cands)), ("Gemeindeanfragen", len(anfragen))):
        L.append(f"| {k} | {v} |")
    L.append("\n## 2 Ersetzte Links\n")
    rep = [r for r in rows if r.get("_alte_url")]
    if rep:
        L.append("| ID | Alt | Neu | Ergebnis Alt | Ergebnis Neu | Grund |\n|---|---|---|---|---|---|")
        for r in rep:
            old = results.get(r["_alte_url"], {})
            L.append(f"| {r['id']} | {r['_alte_url']} | {r['url']} | {old.get('linkstatus', '–')} {old.get('http', '')} | "
                     f"{r['linkstatus']} / {r['inhalt']} | {(r.get('aenderung') or '').split('Grund: ')[-1]} |")
    else:
        L.append("Keine.")
    L.append("\n## 3 Neue Quellen nach Dimension\n")
    for d in ("C1", "C2", "C3", "C4", "C5"):
        new = [r for r in rows if r.get("_neu") and r.get("dim") == d]
        L.append(f"### {d} ({len(new)})\n")
        if not new:
            L.append("Keine neuen Quellen.\n")
            continue
        L.append("| ID | Ebene | Dokument | Link | Inhaltsprüfung |\n|---|---|---|---|---|")
        for r in new:
            L.append(f"| {r['id']} | {r.get('gemeinde') if r.get('ebene') == 'Gemeinde' else r.get('kanton') if r.get('ebene') == 'Kanton' else 'Bund'} | "
                     f"{r.get('titel')} | [{r['linkstatus']}]({r['url']}) | {r['inhalt']} |")
        L.append("")
    L.append("## 4 Abdeckung je Gemeinde und Dimension\n")
    L.append("Zellen: bestätigte Dokumente / Zeilen gesamt (nur Gemeindeebene).\n")
    L.append("| Gemeinde | C1 | C2 | C3 | C4 | C5 |\n|---|---|---|---|---|---|")
    for gem in GEMEINDEN:
        cells = []
        for d in ("C1", "C2", "C3", "C4", "C5"):
            g = [r for r in rows if r.get("gemeinde") == gem and r.get("dim") == d]
            cells.append(f"{sum(1 for r in g if r['inhalt'] == 'Bestätigt')} / {len(g)}")
        L.append(f"| {gem} | " + " | ".join(cells) + " |")
    L.append("\n## 5 Offene und problematische Quellen\n")
    prob = [r for r in rows if r["linkstatus"] not in ("Verifiziert", "Weiterleitung") or r["inhalt"] != "Bestätigt"]
    L.append("| ID | Dokument | Linkstatus | Inhalt | Nachweis / Fehler |\n|---|---|---|---|---|")
    for r in prob:
        L.append(f"| {r['id']} | {r.get('titel')} | {r['linkstatus']} {r.get('http', '')} | {r['inhalt']} | {(r.get('inhalt_detail') or '').replace('|', '/')[:220]} |")
    L.append("\n## 6 Datenlücken und Gemeindeanfragen je Gemeinde\n")
    for gem in GEMEINDEN:
        L.append(f"### {gem}\n")
        a = [x for x in anfragen if x["Gemeinde"] == gem]
        L.append("| ID | Dim. | Priorität | Quellenstatus | Lieferung |\n|---|---|---|---|---|")
        for x in a:
            L.append(f"| {x['Anfrage-ID']} | {x['C-Dimension']} | {x['Priorität']} | {x['Quellenstatus (Recherche)']} | {x['Benötigte Lieferung']} |")
        L.append("")
    for title, key in (("7 Fachliche Unsicherheiten", "unsicherheiten"), ("8 Empfehlungen für weitere Recherchen", "empfehlungen")):
        L.append(f"## {title}\n")
        for item in cur.get("bericht", {}).get(key, []):
            L.append(f"- {item}")
        L.append("")
    L.append("## 9 Protokoll der automatischen Recherche\n")
    L.append("```")
    L.extend(discovery_log or ["(Discovery nicht ausgeführt)"])
    L.append("```")
    L.append("\n## 10 Methode\n")
    L.append("- Linkprüfung: Syntax → DNS → HEAD (Fallback GET) → GET mit max. 30 MB; 3 Versuche mit Backoff bei Verbindungsfehlern, 429 und 5xx; "
             f"max. {WORKERS} parallele Anfragen, mind. {HOST_DELAY} s Abstand pro Host; ehrlicher User-Agent; keine Umgehung von Sperren, CAPTCHAs oder Logins.")
    L.append("- Inhaltsprüfung: PDF-Metadaten und Text der ersten 6 Seiten (pypdf) bzw. HTML-Titel/H1/Text; Abgleich mit hinterlegten Schlüsselwörtern und Ortsnamen. "
             "Bundesrecht über den Fedlex-SPARQL-Endpunkt, kantonales Recht über die LexWork-JSON-Schnittstelle (falls verfügbar).")
    L.append("- Discovery: offizielle Einstiegsseiten (1–2 Ebenen, robots.txt beachtet) und XML-Sitemaps; optional Brave Search API über Secret `BRAVE_SEARCH_API_KEY`.")
    (REPORT_DIR / "recherchebericht.md").write_text("\n".join(L) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------------------
# Hauptprogramm
# --------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="keine Netzanfragen; Ergebnisse aus reports/link_validation.json übernehmen")
    ap.add_argument("--no-discovery", action="store_true", help="automatische Recherche überspringen")
    ap.add_argument("--sync-only", metavar="XLSX", help="nur Gemeindeblätter aus der Gesamtübersicht neu erzeugen")
    args = ap.parse_args()

    if args.sync_only:
        sync_only(Path(args.sync_only))
        return

    cur = json.loads(CURATED_JSON.read_text(encoding="utf-8")) if CURATED_JSON.exists() else {}
    seeds = json.loads(SEEDS_JSON.read_text(encoding="utf-8")) if SEEDS_JSON.exists() else {}

    wb = openpyxl.load_workbook(INPUT_XLSX)
    rows = read_catalogue(wb)
    assign_ids(rows)
    n_original = len(rows)
    rows = apply_curation(rows, cur)

    for rec in rows:
        rec["url"] = clean_url(rec.get("url") or "")

    # zu prüfende URLs: aktuelle Links, ersetzte Alt-Links, Fundstellen
    jobs: OrderedDict[str, tuple[list, list]] = OrderedDict()
    for rec in rows:
        jobs.setdefault(rec["url"], (rec.get("erwartet") or [], places_for(rec)))
        if rec.get("_alte_url"):
            jobs.setdefault(rec["_alte_url"], ([], places_for(rec)))
    results: dict[str, dict] = {}
    log_lines: list[str] = []

    def log(msg):
        print(msg, flush=True)
        log_lines.append(msg)

    cands: list[dict] = []
    if args.offline:
        cache = REPORT_DIR / "link_validation.json"
        cached = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
        for url in jobs:
            results[url] = cached.get(url) or {"linkstatus": "Nicht prüfbar", "fehler": "Offline-Lauf, kein Cache-Eintrag"}
        log(f"Offline: {sum(1 for u in jobs if u in cached)} von {len(jobs)} URLs aus Cache übernommen")
        cand_csv = REPORT_DIR / "discovery_kandidaten.csv"
        if cand_csv.exists():
            with open(cand_csv, encoding="utf-8-sig") as f:
                cands = list(csv.DictReader(f, delimiter=";"))
    else:
        if requests is None:
            raise SystemExit("requests/beautifulsoup4 fehlen: pip install -r requirements.txt")
        http = Http()
        log(f"Prüfe {len(jobs)} URLs mit {WORKERS} Threads …")

        def run(item):
            url, (exp, pl) = item
            try:
                res = check_url(http, url, exp, pl)
            except Exception as exc:  # unerwartete Fehler nicht den ganzen Lauf abbrechen lassen
                res = {"url": url, "linkstatus": "Nicht prüfbar", "fehler": f"Prüfskript: {type(exc).__name__}: {exc}"[:300],
                       "geprueft": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "inhalt": "Offen"}
            log(f"  [{res.get('linkstatus')}] {res.get('http', '')} {res.get('inhalt', '')} {url}")
            return url, res

        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            for url, res in ex.map(run, jobs.items()):
                results[url] = res
        if not args.no_discovery and seeds:
            log("Automatische Recherche (Discovery) …")
            cands = discover(http, seeds, log)
            log(f"Discovery: {len(cands)} Kandidaten")

    derive_fields(rows, results)

    st_vals = [results.get(u, {}).get("linkstatus") for u in jobs]
    stats = dict(
        zeilen=len(rows), original=n_original, urls=len(jobs),
        verif=st_vals.count("Verifiziert"), weiter=st_vals.count("Weiterleitung"),
        ok=st_vals.count("Verifiziert") + st_vals.count("Weiterleitung"),
        fehler=st_vals.count("Fehler"), np=sum(1 for s in st_vals if s not in ("Verifiziert", "Weiterleitung", "Fehler")),
        bestaetigt=sum(1 for r in rows if r["inhalt"] == "Bestätigt"),
        teilweise=sum(1 for r in rows if r["inhalt"] == "Teilweise bestätigt"),
        offen=sum(1 for r in rows if r["inhalt"] == "Offen"),
        ersetzt=sum(1 for r in rows if r.get("_alte_url")), neu=sum(1 for r in rows if r.get("_neu")),
        offene_quellen=sum(1 for r in rows if r["inhalt"] != "Bestätigt" or r["linkstatus"] not in ("Verifiziert", "Weiterleitung")),
    )
    anfragen, n_c = build_workbook(rows, cur, cands, stats)
    write_reports(rows, results, cands, anfragen, stats, cur, log_lines)
    print(json.dumps(stats, ensure_ascii=False))
    print(f"Geschrieben: {OUTPUT_XLSX.name}, reports/link_validation.csv, reports/recherchebericht.md, {n_c} Kandidaten im Blatt")


if __name__ == "__main__":
    main()
