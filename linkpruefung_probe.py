#!/usr/bin/env python3
"""Hilfsabfrage für die Linkprüfung: Kandidaten-Nummern und Titelsuche in den
LexWork-Gesetzessammlungen (BL, SG, UR, Wil) prüfen. Ergebnis: linkpruefung_probe.json"""
import json
import requests

UA = {"User-Agent": "Mozilla/5.0 Linkpruefung Q-Rahmen", "Accept": "application/json"}
BASES = {"BL": "https://bl.clex.ch", "SG": "https://www.gesetzessammlung.sg.ch",
         "UR": "https://rechtsbuch.ur.ch", "WIL": "https://wil-sg.tlex.ch"}
KANDIDATEN = {
    "BL": ["791", "792", "793", "794", "420", "420.1", "781", "782"],
    "SG": ["734.1", "734.11", "731.1"],
    "UR": ["10.5101", "10.5111", "10.5103", "40.3101", "40.3111", "40.4101", "3.3112",
           "3.3113", "3.3114", "3.3116", "3.3117", "3.3118"],
    "WIL": ["7.3-1", "7.3-2", "7.4-1", "7.5-1", "7.1-2", "7.1-3", "7.2-1", "7.6-1", "7.7-1", "7.8-1"],
}
SUCHPFADE = ["/api/de/texts_of_law/lightweight_index", "/api/de/texts_of_law",
             "/api/de/systematic_verzeichnis", "/api/de/systematic_tree", "/api/de/search?query=Abwasser",
             "/api/de/texts_of_law/search?q=Abwasser", "/api/de/categories"]


def get(url):
    try:
        r = requests.get(url, headers=UA, timeout=40)
        return r.status_code, r.headers.get("content-type", ""), r.text
    except Exception as e:  # noqa: BLE001
        return 0, "", str(e)


out = {"kandidaten": {}, "suche": {}}
for k, nrs in KANDIDATEN.items():
    for nr in nrs:
        s, ct, t = get(f"{BASES[k]}/api/de/texts_of_law/{nr}")
        title = ""
        if s == 200 and "json" in ct:
            d = json.loads(t).get("text_of_law", {})
            title = f"{d.get('systematic_number')} {d.get('title')} ({d.get('abbreviation')}) " \
                    f"aufgehoben={d.get('is_abrogated', d.get('abrogated'))}"
        out["kandidaten"][f"{k} {nr}"] = f"{s} {title}"
        print(k, nr, s, title, flush=True)
for k, base in BASES.items():
    for p in SUCHPFADE:
        s, ct, t = get(base + p)
        out["suche"][k + p] = {"status": s, "ctype": ct[:40], "len": len(t), "head": t[:1500]}
        print(k, p, s, ct[:30], len(t), flush=True)
out["index"] = {}
for k, base in BASES.items():  # vollständiges Titelverzeichnis jeder Sammlung
    s, ct, t = get(base + "/api/de/texts_of_law/lightweight_index")
    if s == 200:
        out["index"][k] = sorted([x["systematic_number"], x["title"], x.get("abrogated")]
                                 for v in json.loads(t).values() for x in v)
    out["suche"] = {}
json.dump(out, open("linkpruefung_probe.json", "w"), ensure_ascii=False, indent=1)
