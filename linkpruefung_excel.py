#!/usr/bin/env python3
"""Linkprüfung der Excel-Übersicht (Q-Rahmen Münchenstein / Wil / Seelisberg).

Prüft für jede Dokumentzeile (Blätter 1–6) und jeden Layer-Link (Blatt 7):
  1. HTTP-Status und Ziel-URL des Links (Zelltext und Hyperlink-Ziel).
  2. Ob der Link auf das richtige Dokument zeigt:
     - Fedlex (SR): über den SPARQL-Endpunkt fedlex.data.admin.ch wird die
       SR-Nummer des verlinkten Erlasses ermittelt und mit «Referenz» verglichen.
       Für jede SR-Nummer wird zusätzlich der korrekte Fedlex-Link gesucht.
     - LexWork-Gesetzessammlungen (BL clex, SG, UR, Wil tlex): Titel und
       Nummer über die JSON-API der Sammlung.
     - map.geo.admin.ch: Layer-ID gegen layersConfig von api3.geo.admin.ch.
     - übrige Seiten/PDFs: Titel bzw. Text wird nach Name und Referenz durchsucht.
Ergebnis: linkpruefung_excel.json (Rohdaten) und Linkpruefung_Excel.md.

Aufruf (läuft im GitHub-Runner, weil die Portale aus der Sandbox gesperrt sind):
  pip install openpyxl requests pypdf
  python3 linkpruefung_excel.py Q-Rahmen_Uebersicht.xlsx
"""
import argparse
import io
import json
import re
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from html import unescape

import openpyxl
import requests

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Linkpruefung Q-Rahmen",
      "Accept-Language": "de-CH,de;q=0.9"}
SPARQL = "https://fedlex.data.admin.ch/sparqlendpoint"
LAYERS_CONFIG = "https://api3.geo.admin.ch/rest/services/api/MapServer/layersConfig?lang=de"
DOC_SHEETS = ["1_Q1_Rechtsordnung", "2_Q2_Landschaft", "3_Q3_Klima_Energie",
              "4_Q4_Resilienz", "5_Q5_Ortsbild", "6_Q6_Bestellung"]
GIS_SHEET = "7_GIS_Layers"
LEXWORK = {  # Präfix der Referenz -> Basis-URL der Gesetzessammlung
    "SGS": "https://bl.clex.ch",
    "sGS": "https://www.gesetzessammlung.sg.ch",
    "RB": "https://rechtsbuch.ur.ch",
    "SRS": "https://wil-sg.tlex.ch",
}
STOP = set("der die das und oder von vom zum zur zu den dem des im in über für mit auf an bei "
           "nach als aus ein eine einer eines bl sg ur gde kanton bund inkl plus sowie".split())


# ---------------------------------------------------------------- Excel lesen
def read_rows(path):
    wb = openpyxl.load_workbook(path)
    rows = []
    for ws in wb.worksheets:
        if ws.title in DOC_SHEETS:
            hdr = None
            for r in ws.iter_rows():
                v = [c.value for c in r]
                if v[0] == "Ebene":
                    hdr = {h: i for i, h in enumerate(v) if h}
                    continue
                if not hdr or not v[hdr["Bezeichnung"]]:
                    continue
                c = r[hdr["Link / Quelle"]]
                rows.append({
                    "sheet": ws.title, "row": c.row, "ebene": v[0],
                    "name": str(v[hdr["Bezeichnung"]]),
                    "ref": str(v[hdr["Referenz (SR/SGS/RB)"]] or ""),
                    "text": str(c.value or "").strip(),
                    "target": c.hyperlink.target if c.hyperlink else None,
                })
        elif ws.title == GIS_SHEET:
            for r in ws.iter_rows(min_row=5):
                v = [c.value for c in r]
                if not v[2]:
                    continue
                for c in r[5:9]:
                    if c.hyperlink or (c.value and str(c.value).startswith("http")):
                        rows.append({
                            "sheet": ws.title, "row": c.row, "col": c.column_letter,
                            "ebene": v[3], "name": str(v[2]), "ref": str(v[4] or ""),
                            "label": str(c.value or ""),
                            "text": str(c.value or "") if str(c.value or "").startswith("http") else "",
                            "target": c.hyperlink.target if c.hyperlink else None,
                        })
    return rows


# ---------------------------------------------------------------- HTTP
def fetch(url):
    out = {"url": url}
    try:
        r = requests.get(url, headers=UA, timeout=40, allow_redirects=True)
        out.update(status=r.status_code, final=r.url,
                   ctype=r.headers.get("content-type", "").split(";")[0])
        body = r.content
        if out["ctype"] == "application/pdf" or body[:4] == b"%PDF":
            out["ctype"] = "application/pdf"
            try:
                from pypdf import PdfReader
                pdf = PdfReader(io.BytesIO(body))
                meta = pdf.metadata or {}
                out["title"] = str(meta.get("/Title") or "")
                out["text"] = " ".join((p.extract_text() or "") for p in pdf.pages[:3])[:4000]
                out["pages"] = len(pdf.pages)
            except Exception as e:  # noqa: BLE001
                out["text"] = f"[PDF nicht lesbar: {e}]"
        else:
            html = r.text
            m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
            out["title"] = unescape(m.group(1)).strip() if m else ""
            txt = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
            txt = re.sub(r"<[^>]+>", " ", txt)
            out["text"] = re.sub(r"\s+", " ", unescape(txt))[:4000]
    except Exception as e:  # noqa: BLE001
        out.update(status=0, error=str(e)[:200])
    return out


# ---------------------------------------------------------------- Fedlex
def sparql(query):
    r = requests.post(SPARQL, data={"query": query},
                      headers={**UA, "Accept": "application/sparql-results+json"}, timeout=90)
    r.raise_for_status()
    return r.json()["results"]["bindings"]


FEDLEX_PREFIX = """PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""


def fedlex_by_sr(srs):
    """SR-Nummer -> [{eli, title, abbr}] (nur in Kraft stehende Erlasse zuerst)."""
    values = " ".join(f'"{s}"' for s in srs)
    q = FEDLEX_PREFIX + f"""
SELECT DISTINCT ?sr ?ca ?title ?abbr ?status WHERE {{
  VALUES ?sr {{ {values} }}
  ?ca a jolux:ConsolidationAbstract ;
      jolux:classifiedByTaxonomyEntry ?e .
  ?e skos:notation ?n . FILTER(str(?n) = ?sr)
  OPTIONAL {{ ?ca jolux:inForceStatus ?status }}
  OPTIONAL {{ ?ca jolux:isRealizedBy ?x .
             ?x jolux:language <http://publications.europa.eu/resource/authority/language/DEU> .
             OPTIONAL {{ ?x jolux:title ?title }}
             OPTIONAL {{ ?x jolux:titleShort ?abbr }} }}
}}"""
    res = {}
    for b in sparql(q):
        res.setdefault(b["sr"]["value"], []).append({
            "eli": b["ca"]["value"], "title": b.get("title", {}).get("value", ""),
            "abbr": b.get("abbr", {}).get("value", ""),
            "status": b.get("status", {}).get("value", "")})
    return res


def fedlex_by_eli(elis):
    """ELI-URI (fedlex.data.admin.ch/eli/cc/...) -> {sr, title, abbr}."""
    values = " ".join(f"<{e}>" for e in elis)
    q = FEDLEX_PREFIX + f"""
SELECT DISTINCT ?ca ?n ?title ?abbr WHERE {{
  VALUES ?ca {{ {values} }}
  OPTIONAL {{ ?ca jolux:classifiedByTaxonomyEntry/skos:notation ?n }}
  OPTIONAL {{ ?ca jolux:isRealizedBy ?x .
             ?x jolux:language <http://publications.europa.eu/resource/authority/language/DEU> .
             OPTIONAL {{ ?x jolux:title ?title }}
             OPTIONAL {{ ?x jolux:titleShort ?abbr }} }}
}}"""
    res = {}
    for b in sparql(q):
        d = res.setdefault(b["ca"]["value"], {"sr": [], "title": "", "abbr": ""})
        if "n" in b and b["n"]["value"] not in d["sr"]:
            d["sr"].append(b["n"]["value"])
        d["title"] = d["title"] or b.get("title", {}).get("value", "")
        d["abbr"] = d["abbr"] or b.get("abbr", {}).get("value", "")
    return res


def eli_of(url):
    m = re.search(r"fedlex\.admin\.ch/eli/(cc/[^/?#]+/[^/?#]+)", url or "")
    return f"https://fedlex.data.admin.ch/eli/{m.group(1)}" if m else None


# ---------------------------------------------------------------- LexWork
def lexwork(base, nr):
    """Titel eines Erlasses in einer LexWork-Sammlung (clex/tlex) abfragen."""
    tried = []
    for path in (f"/api/de/texts_of_law/{nr}", f"/api/de/texts_of_law/{nr}/show_as_json",
                 f"/app/de/texts_of_law/{nr}"):
        url = base + path
        try:
            r = requests.get(url, headers={**UA, "Accept": "application/json"}, timeout=40)
        except Exception as e:  # noqa: BLE001
            tried.append(f"{path}: {e}"[:150])
            continue
        tried.append(f"{path}: {r.status_code} {r.headers.get('content-type', '')[:30]}")
        if r.status_code == 200 and "json" in r.headers.get("content-type", ""):
            try:
                data = r.json()
            except ValueError:
                continue
            flat = json.dumps(data, ensure_ascii=False)
            t = re.search(r'"title"\s*:\s*"([^"]+)"', flat)
            n = re.search(r'"systematic_number"\s*:\s*"([^"]+)"', flat)
            return {"api": url, "title": t.group(1) if t else "", "nr": n.group(1) if n else "",
                    "raw": flat[:600], "tried": tried}
    return {"api": None, "title": "", "nr": "", "tried": tried}


# ---------------------------------------------------------------- Abgleich
def keywords(name):
    abbr = re.findall(r"\(([A-ZÄÖÜa-zäöü0-9\-\s]{2,15})\)", name)
    words = [w for w in re.findall(r"[A-Za-zÄÖÜäöüß]{5,}", name) if w.lower() not in STOP]
    return [a.strip() for a in abbr], words[:6]


def ref_numbers(ref):
    """«SR 700.1» -> ('SR', '700.1');  «IVöB: RB 3.3111; Reglement: RB 3.3115» -> mehrere."""
    return re.findall(r"\b(SR|SGS|sGS|RB|SRS|TR)\s*(?:-Nr\.)?\s*([0-9][0-9A-Za-z.\-]*)", ref or "")


def content_match(row, page):
    hay = f"{page.get('title', '')} {page.get('text', '')}".lower()
    abbr, words = keywords(row["name"])
    hits = [w for w in words if w.lower() in hay]
    ahits = [a for a in abbr if a.lower() in hay]
    refs = [n for _, n in ref_numbers(row["ref"])]
    rhits = [n for n in refs if re.search(rf"(?<![\d.]){re.escape(n.lower())}(?![\d])", hay)]
    return {"words": hits, "of": len(words), "abbr": ahits, "refs": rhits, "refs_of": len(refs)}


def is_entry_page(url):
    p = urllib.parse.urlparse(url)
    return p.path in ("", "/") and not p.query and not p.fragment


# ---------------------------------------------------------------- Hauptlauf
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx")
    ap.add_argument("--json", default="linkpruefung_excel.json")
    ap.add_argument("--md", default="Linkpruefung_Excel.md")
    args = ap.parse_args()

    rows = read_rows(args.xlsx)
    urls = sorted({u for r in rows for u in (r["text"], r["target"]) if u and u.startswith("http")})
    print(f"{len(rows)} Zeilen, {len(urls)} URLs", flush=True)
    with ThreadPoolExecutor(8) as ex:
        pages = {p["url"]: p for p in ex.map(fetch, urls)}

    # Fedlex
    srs = sorted({n for r in rows for p, n in ref_numbers(r["ref"]) if p == "SR"})
    elis = sorted({e for u in urls if (e := eli_of(u))})
    fed_sr, fed_eli, fed_err = {}, {}, None
    try:
        fed_sr = fedlex_by_sr(srs) if srs else {}
        fed_eli = fedlex_by_eli(elis) if elis else {}
    except Exception as e:  # noqa: BLE001
        fed_err = str(e)[:300]
        print("Fedlex SPARQL Fehler:", fed_err, flush=True)

    # LexWork
    lw_keys = sorted({(p, n) for r in rows for p, n in ref_numbers(r["ref"]) if p in LEXWORK})
    with ThreadPoolExecutor(6) as ex:
        lw = dict(zip(lw_keys, ex.map(lambda k: lexwork(LEXWORK[k[0]], k[1]), lw_keys)))

    # Layer
    layer_ids = {}
    try:
        cfg = requests.get(LAYERS_CONFIG, headers=UA, timeout=90).json()
        layer_ids = {k: v.get("label", "") for k, v in cfg.items()}
    except Exception as e:  # noqa: BLE001
        print("layersConfig Fehler:", e, flush=True)

    for r in rows:
        url = r["text"] if r["text"].startswith("http") else (r["target"] or "")
        r["hyperlink_ok"] = (not r["target"]) or r["target"].rstrip("/") == url.rstrip("/") or \
            urllib.parse.unquote(r["target"]) == urllib.parse.unquote(url)
        pg = pages.get(url, {})
        r["page"] = {k: pg.get(k) for k in ("status", "final", "ctype", "title", "error", "pages")}
        r["snippet"] = (pg.get("text") or "")[:300]
        r["match"] = content_match(r, pg) if pg else {}
        r["entry_page"] = is_entry_page(url)
        if (e := eli_of(url)):
            r["fedlex_link"] = fed_eli.get(e)
        r["fedlex_ref"] = {n: fed_sr.get(n) for p, n in ref_numbers(r["ref"]) if p == "SR"}
        r["lexwork"] = {f"{p} {n}": lw[(p, n)] for p, n in ref_numbers(r["ref"]) if p in LEXWORK}
        lids = re.findall(r"layers=([^&#]+)", url) + ([r["ref"]] if r["ref"].startswith("ch.") else [])
        r["layers"] = {lid: layer_ids.get(lid, "FEHLT") for lid in
                       {x for l in lids for x in urllib.parse.unquote(l).split(",")} if lid.startswith("ch.")} \
            if layer_ids else {}

    with open(args.json, "w", encoding="utf-8") as f:
        json.dump({"fedlex_error": fed_err, "rows": rows}, f, ensure_ascii=False, indent=1)

    lines = ["# Linkprüfung Excel (GitHub-Runner)", "",
             "| Blatt!Zeile | Bezeichnung | Referenz | HTTP | Ziel / Titel | Treffer | Fedlex / LexWork / Layer |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        pg, m = r["page"], r["match"]
        info = []
        if r.get("fedlex_link"):
            fl = r["fedlex_link"]
            info.append(f"Link=SR {','.join(fl['sr'])} {fl['abbr']}")
        for n, v in r["fedlex_ref"].items():
            info.append(f"SR {n}→" + (", ".join(f"{x['eli']} ({x['abbr']})" for x in v) if v else "nicht gefunden"))
        for n, v in r["lexwork"].items():
            info.append(f"{n}: {v['title'] or 'kein Titel'} [{'; '.join(v['tried'])}]")
        for lid, lab in r["layers"].items():
            info.append(f"{lid}: {lab}")
        if not r["hyperlink_ok"]:
            info.append(f"Hyperlink weicht ab: {r['target']}")
        hit = (f"W {len(m.get('words', []))}/{m.get('of', 0)} A {m.get('abbr')} "
               f"R {len(m.get('refs', []))}/{m.get('refs_of', 0)}") if m else ""
        cell = lambda s: str(s or "").replace("|", "/").replace("\n", " ")[:120]  # noqa: E731
        lines.append(f"| {r['sheet'][:4]}!{r['row']}{r.get('col', '')} | {cell(r['name'])[:60]} | {cell(r['ref'])} | "
                     f"{pg.get('status')} | {cell(pg.get('final'))} — {cell(pg.get('title'))} | {hit} | "
                     f"{cell(' · '.join(info))[:400]} |")
    with open(args.md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
