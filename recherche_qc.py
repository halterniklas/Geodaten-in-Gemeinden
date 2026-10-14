#!/usr/bin/env python3
"""Recherche Q und C für die drei Pilotgemeinden (läuft im GitHub-Runner).

1. Geodaten Q: zusätzliche Bundeslayer (FFF, Grundwasserschutz, ShowMe-Naturgefahren u. a.)
   in layersConfig suchen und je Gemeinde per identify abfragen (inkl. Attributen).
2. Finanzkennzahlen C1: Jahresrechnungen und kantonale Kennzahlenberichte (PDF) laden und
   die Zeilen mit HRM2-Kennzahlen (Selbstfinanzierungsgrad, Nettoschuld usw.) ausgeben.
3. Neue Q1-Erlasse: Titel in den LexWork-Sammlungen prüfen; Zonenplan Münchenstein in oereblex suchen.

Ausgabe: recherche_qc.json und recherche_qc.md
"""
import io
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

import requests

sys.path.insert(0, ".")
import gis_betroffenheit as gis  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Recherche Q-C Raumgleiter"}
GEMEINDEN = ["Münchenstein", "Wil (SG)", "Seelisberg"]
LAYER_KEYWORDS = ["fruchtfolge", "grundwasserschutz", "gewaesserschutz", "showme", "gewaesserraum",
                  "hitze", "gefahrenkarte", "intensitaet", "naturgefahr", "siedlungsgebiet",
                  "richtplan", "landschaftsschutz", "pruefperimeter", "kataster-belasteter-standorte"]
FINANZ_QUELLEN = {
    "SEE-JR2024": "https://www.seelisberg.ch/files/pdf/JR2024_Gde-Seelisberg.pdf",
    "SEE-JR2023": "https://www.seelisberg.ch/files/pdf/Jahresrechnung_Gde-Seelisberg_2023.pdf",
    "SEE-GV-Nov2025": "https://www.seelisberg.ch/files/pdf/Druckvorlage2_Original_Versammlung-Nov2025_Traktanden-und-Botschaften-gesamt.pdf",
    "MUE-JR2025": "https://www.muenchenstein.ch/publikationen/621658",
    "MUE-JR2024": "https://www.muenchenstein.ch/publikationen/556069",
    "MUE-GV-Dez2025": "https://www.muenchenstein.ch/sitzung/5729137",
    "WIL-JR2025": "https://www.stadtwil.ch/storage/08902ff399818ccc0d53949607b2d0f6f8bf702c334e295d493c2fd842ba4079",
    "WIL-JR2024": "https://www.stadtwil.ch/storage/0f0d7ad95464bf91a72506e63d2aae1d5c18327f9bff4bf34b8400c36999b277",
    "WIL-FP2026": "https://www.stadtwil.ch/storage/875d422378d72386aae96efa76356fbfa05e9a0e1e03f208fbbe599dea21021c",
    "UR-Kennzahlen-2025": "https://www.ur.ch/_doc/451636",
    "UR-Kennzahlen-2024": "https://www.ur.ch/_doc/420775",
    "BL-Statistik-Gemeindefinanzen": "https://statistik.bl.ch/web_portal/18_5",
    "BL-Finanzhandbuch-16": "https://bl-api.webcloud7.ch/politik-und-behorden/gemeinden/gemeindefinanzen/"
                            "rechnungslegung-einwohnergemeinden/finanzhandbuch/pdf-finanzhandbuch/"
                            "finanzhandbuchkapitel-16_finanzkennzahlen_20-03-01_26-05-01.pdf",
    "SG-Rechnungslegung": "https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen/rechnungslegung--rmsg-.html",
}
KENNZAHL_RE = re.compile(r"selbstfinanzierungsgrad|selbstfinanzierungsanteil|nettoschuld|nettoverschuldung|"
                         r"nettovermögen|zinsbelastungsanteil|kapitaldienstanteil|bruttoverschuldungsanteil|"
                         r"investitionsanteil|nettoinvestition|selbstfinanzierung\b|steuerfuss|"
                         r"einwohner(?:zahl)?\b|bilanzüberschuss|eigenkapital", re.I)
LEXWORK = {
    "SGS 400.11": "https://bl.clex.ch", "SGS 149.72": "https://bl.clex.ch", "SGS 420": "https://bl.clex.ch",
    "sGS 731.11": "https://www.gesetzessammlung.sg.ch", "sGS 841.11": "https://www.gesetzessammlung.sg.ch",
    "RB 40.1115": "https://rechtsbuch.ur.ch", "RB 40.1117": "https://rechtsbuch.ur.ch",
}
OEREBLEX_RANGE = range(22650, 22800)


def get(url, **kw):
    return requests.get(url, headers=UA, timeout=60, **kw)


def pdf_text(content, max_pages=400):
    from pypdf import PdfReader
    pdf = PdfReader(io.BytesIO(content))
    pages = []
    for i, p in enumerate(pdf.pages[:max_pages]):
        try:
            pages.append((i + 1, p.extract_text() or ""))
        except Exception:  # noqa: BLE001
            pages.append((i + 1, ""))
    meta = pdf.metadata or {}
    return str(meta.get("/Title") or ""), len(pdf.pages), pages


def kennzahlen(key, url):
    out = {"key": key, "url": url, "docs": []}
    try:
        r = get(url)
        out["status"], out["final"] = r.status_code, r.url
        docs = []
        if r.content[:4] == b"%PDF":
            docs.append((r.url, r.content))
        else:  # HTML: verlinkte PDFs mit Bezug zu Rechnung/Finanzen holen
            links = re.findall(r'href="([^"]+)"', r.text)
            pdfs = [urljoin(r.url, h) for h in links
                    if re.search(r"\.pdf|_docn/|storage/|download", h, re.I)
                    and re.search(r"rechnung|finanz|budget|bericht|afp|kennzahl|_docn|storage", h, re.I)]
            out["pdf_links"] = pdfs[:15]
            for p in pdfs[:6]:
                try:
                    rp = get(p)
                    if rp.content[:4] == b"%PDF":
                        docs.append((rp.url, rp.content))
                except Exception as e:  # noqa: BLE001
                    out.setdefault("errors", []).append(f"{p}: {e}"[:200])
        for durl, content in docs:
            title, n, pages = pdf_text(content)
            hits = []
            for no, txt in pages:
                lines = txt.splitlines()
                for i, line in enumerate(lines):
                    if KENNZAHL_RE.search(line) or (key.startswith("UR") and "Seelisberg" in line):
                        ctx = " ⏎ ".join(lines[max(0, i - 1):i + 3])
                        hits.append(f"S.{no}: {ctx}"[:400])
            out["docs"].append({"url": durl, "title": title, "pages": n, "hits": hits[:150]})
    except Exception as e:  # noqa: BLE001
        out["error"] = str(e)[:300]
    return out


def lexwork(ref, base):
    nr = ref.split()[-1]
    try:
        d = requests.get(f"{base}/api/de/texts_of_law/{nr}", timeout=60,
                         headers={**UA, "Accept": "application/json"}).json()
        t = d.get("text_of_law", {})
        return {"ref": ref, "url": f"{base}/app/de/texts_of_law/{nr}", "title": t.get("title"),
                "abbr": t.get("abbreviation"), "dates": t.get("text_of_law_dates_str")}
    except Exception as e:  # noqa: BLE001
        return {"ref": ref, "error": str(e)[:200]}


def oereblex(i):
    url = f"https://oereblex.bl.ch/api/attachments/{i}"
    try:
        r = get(url)
        if r.status_code != 200 or r.content[:4] != b"%PDF":
            return None
        from pypdf import PdfReader
        pdf = PdfReader(io.BytesIO(r.content))
        first = (pdf.pages[0].extract_text() or "")[:300] if pdf.pages else ""
        if "nchenstein" not in first and "nchenstein" not in str((pdf.metadata or {}).get("/Title", "")):
            return None
        return {"id": i, "url": url, "title": str((pdf.metadata or {}).get("/Title") or ""),
                "pages": len(pdf.pages), "first": re.sub(r"\s+", " ", first)}
    except Exception:  # noqa: BLE001
        return None


CRAWL = {  # Seiten, deren Links nach Stichworten durchsucht werden
    "MUE-JR2025": "https://www.muenchenstein.ch/publikationen/621658",
    "MUE-JR2024": "https://www.muenchenstein.ch/publikationen/556069",
    "MUE-GV-Dez2025": "https://www.muenchenstein.ch/sitzung/5729137",
    "MUE-Publikationen": "https://www.muenchenstein.ch/publikationen",
    "MUE-Reglemente": "https://www.muenchenstein.ch/reglemente",
    "MUE-Bauverwaltung": "https://www.muenchenstein.ch/bauverwaltung",
    "MUE-Ortsplanung": "https://www.muenchenstein.ch/ortsplanung",
    "BL-Gemeindefinanzen-2023": "https://www.baselland.ch/politik-und-behorden/direktionen/finanz-und-kirchendirektion/"
                                "daten-statistik/abteilung-statistik/publikationen-und-statistiken/finanzen-und-steuern/"
                                "webartikel-vom-18-09-2024-gemeindefinanzen-2023",
    "BL-Gemeindefinanzen": "https://www.baselland.ch/politik-und-behorden/gemeinden/gemeindefinanzen",
}
CRAWL_RE = re.compile(r"zonenplan|nutzungsplan|jahresrechnung|rechnung 20|bericht|kennzahl|finanzstatistik|"
                      r"gemeindefinanz|\.xlsx|\.pdf|_docn", re.I)


def crawl(key, url):
    out = {"key": key, "url": url}
    try:
        r = get(url)
        out["status"], out["final"] = r.status_code, r.url
        links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.S | re.I)
        hits = []
        for href, txt in links:
            t = re.sub(r"<[^>]+>|\s+", " ", txt).strip()
            if CRAWL_RE.search(href) or CRAWL_RE.search(t):
                hits.append((urljoin(r.url, href), t[:120]))
        out["links"] = hits[:80]
        out["n_links"] = len(links)
        out["text"] = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", r.text))[:1500]
        pdfs = [h for h, t in hits if re.search(r"jahresrechnung|rechnung|bericht|finanz", h + t, re.I)
                and re.search(r"_docn|\.pdf|download", h, re.I)]
        out["kennzahlen"] = [kennzahlen(f"{key}-pdf", p) for p in pdfs[:4]]
    except Exception as e:  # noqa: BLE001
        out["error"] = str(e)[:300]
    return out


def main():
    out = {}
    if "--crawl" in sys.argv:
        with ThreadPoolExecutor(6) as ex:
            out["crawl"] = list(ex.map(lambda kv: crawl(*kv), CRAWL.items()))
        out["lexwork"] = [lexwork(r, b) for r, b in LEXWORK.items()]
        json.dump(out, open("recherche_qc2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        for c in out["crawl"]:
            print(c["key"], c.get("status"), c.get("n_links"), len(c.get("links", [])))
        return
    # 1. Geodaten
    cfg = get(gis.API + "/layersConfig", params={"lang": "de"}).json()
    found = {k: v.get("label", "") for k, v in cfg.items()
             if any(w in k.lower() for w in LAYER_KEYWORDS)}
    out["layer_kandidaten"] = found
    print(len(found), "Layer-Kandidaten", flush=True)
    polys = {g: gis.gemeinde_polygon(g) for g in GEMEINDEN}
    q = {g: gis.query_geometry(p) for g, p in polys.items()}
    geo = []
    for lid in sorted(found):
        if not cfg[lid].get("queryable", True) and "showme" not in lid:
            continue
        for g in GEMEINDEN:
            js, bounds, exact = q[g]
            try:
                data = gis.get_json(f"{gis.API}/identify", {
                    "geometry": js, "geometryType": "esriGeometryPolygon", "layers": f"all:{lid}",
                    "sr": 2056, "tolerance": 0, "mapExtent": ",".join(map(str, bounds)),
                    "imageDisplay": "1000,1000,96", "returnGeometry": "false", "limit": 20, "lang": "de"})
                res = data.get("results", [])
                attrs = [{k: v for k, v in (f.get("attributes") or {}).items() if v not in (None, "")}
                         for f in res[:5]]
                geo.append({"layer": lid, "label": found[lid], "gemeinde": g, "treffer": len(res),
                            "labels": sorted({gis.feature_label(f) for f in res})[:15], "attribute": attrs})
            except Exception as e:  # noqa: BLE001
                geo.append({"layer": lid, "gemeinde": g, "error": str(e)[:200]})
    out["geo"] = geo
    # 2. Finanzen
    with ThreadPoolExecutor(6) as ex:
        out["finanzen"] = list(ex.map(lambda kv: kennzahlen(*kv), FINANZ_QUELLEN.items()))
    # 3. Q1-Erlasse und Zonenplan Münchenstein
    out["lexwork"] = [lexwork(r, b) for r, b in LEXWORK.items()]
    with ThreadPoolExecutor(8) as ex:
        out["oereblex_muenchenstein"] = [x for x in ex.map(oereblex, OEREBLEX_RANGE) if x]

    json.dump(out, open("recherche_qc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = ["# Recherche Q/C (GitHub-Runner)", "", "## Layer-Kandidaten", ""]
    md += [f"- `{k}` {v}" for k, v in sorted(found.items())]
    md += ["", "## Geodaten je Gemeinde", ""]
    for x in geo:
        md.append(f"- {x['layer']} · {x['gemeinde']}: {x.get('treffer', x.get('error'))} "
                  f"{', '.join(x.get('labels', []))[:200]}")
    md += ["", "## Finanzkennzahlen", ""]
    for f in out["finanzen"]:
        md.append(f"### {f['key']} ({f.get('status')}) {f.get('final', '')}")
        for d in f["docs"]:
            md.append(f"- {d['url']} · {d['title']} · {d['pages']} S.")
            md += [f"  - {h}" for h in d["hits"][:60]]
    md += ["", "## LexWork", ""] + [f"- {x}" for x in out["lexwork"]]
    md += ["", "## oereblex Münchenstein", ""] + [f"- {x}" for x in out["oereblex_muenchenstein"]]
    open("recherche_qc.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md[:80]))


if __name__ == "__main__":
    main()
