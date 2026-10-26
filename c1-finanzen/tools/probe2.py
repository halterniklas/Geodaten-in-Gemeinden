"""Stufe 2 (GitHub-Runner): BL-Quellen sondieren, Kerndateien als Rohdaten laden."""
import json, re, sys, pathlib, subprocess, datetime, urllib.request, urllib.parse, ssl, html

OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
RAW = pathlib.Path(sys.argv[2]); RAW.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (c1-finanzen; research)"}
log = {"retrieved": datetime.datetime.utcnow().isoformat() + "Z", "pages": {}, "files": {}}

def fetch(u, limit=60_000_000):
    req = urllib.request.Request(u, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=120, context=ssl.create_default_context()) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read(limit)
    except urllib.error.HTTPError as e:
        return e.code, "", str(e).encode()
    except Exception as e:
        return 0, "", repr(e).encode()

LINK = re.compile(r'(?:href|src)="([^"]+)"', re.I)
BL_PAGES = {
 "bl_gemeindefinanzen": "https://www.baselland.ch/politik-und-behorden/gemeinden/gemeindefinanzen",
 "bl_finanzstatistik": "https://www.baselland.ch/politik-und-behorden/gemeinden/gemeindefinanzen/finanzstatistik",
 "bl_statistik_amt": "https://www.baselland.ch/politik-und-behorden/direktionen/finanz-und-kirchendirektion/statistisches-amt",
 "bl_statistik_portal": "https://statistik.bl.ch/",
 "bl_statistik_portal_www": "https://www.statistik.bl.ch/",
 "bl_api_gemeindefinanzen": "https://bl-api.webcloud7.ch/politik-und-behorden/gemeinden/gemeindefinanzen",
 "bl_open": "https://opendata.bl.ch/",
 "ur_gemeinden": "https://www.ur.ch/gemeinden",
 "sg_statistik": "https://www.statistik.sg.ch/",
}
for k, u in BL_PAGES.items():
    st, ct, d = fetch(u)
    txt = d.decode("utf-8", "replace")
    links = sorted({urllib.parse.urljoin(u, x) for x in LINK.findall(txt)
                    if re.search(r'finanz|gemeinde|statist|xls|csv|pdf|daten|kennzahl', x, re.I)})
    (OUT / f"page2_{k}.html").write_text(txt[:300000], encoding="utf-8")
    log["pages"][k] = {"url": u, "status": st, "bytes": len(d), "links": links[:300],
                        "err": txt[:200] if st == 0 else ""}
    print(k, st, len(d), len(links))

DL = {
 "are_bzs2022_gemeinden.xlsx": "https://www.are.admin.ch/dam/de/sd-web/7cEPibyb2l-3/bauzonenstatistik_schweiz_2022_gemeinden.xlsx",
 "are_bzs2022_resultate.xlsx": "https://www.are.admin.ch/dam/de/sd-web/uPugMgFnGj0m/bauzonenstatistik_schweiz_2022_resultate.xlsx",
 "are_bzs2022_raumgliederung.xlsx": "https://www.are.admin.ch/dam/de/sd-web/lTUT9gVTUx4y/bauzonenstatistik_schweiz_2022_raumgliederung.xlsx",
 "are_bzs2022_steckbrief.pdf": "https://www.are.admin.ch/dam/de/sd-web/7lugJ64jJSgn/bzs-steckbrief.pdf",
 "are_bzs2022_bericht.pdf": "https://www.are.admin.ch/dam/de/sd-web/AS4q88PlZYXF/bzs_2022.pdf",
 "are_bzs2017.zip": "https://www.are.admin.ch/dam/de/sd-web/iLHkdaGp7qi3/Bauzonenstatistik_Schweiz_2017.zip",
 "are_bzs2012.zip": "https://www.are.admin.ch/dam/de/sd-web/3lK47686QIeu/Bauzonenstatistik_Schweiz_2012.zip",
 "sg_kennzahlen_rmsg.xlsx": "https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen/_jcr_content/Par/sgch_accordion_list_1344425806/AccordionListPar/sgch_accordion_396006679/AccordionPar/sgch_downloadlist/DownloadListPar/sgch_download.ocFile/Kennzahlen%20neues%20Rechnungslegungsmodell%20der%20St.Galler%20Gemeinden.xlsx",
 "sg_uebersicht_finanzkennzahlen.xlsx": "https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen/_jcr_content/Par/sgch_accordion_list_396006679/AccordionPar/sgch_downloadlist/DownloadListPar/sgch_download_131465241.ocFile/%C3%9Cbersichtstabelle%20zu%20den%20Finanzkennzahlen%20der%20St.Galler%20Gemeinden.xlsx",
 "sg_kennzahlenberechnung_rmsg_v1_2.xlsx": "https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen/_jcr_content/Par/sgch_accordion_list_1344425806/AccordionListPar/sgch_accordion_228014448/AccordionPar/sgch_downloadlist/DownloadListPar/sgch_download_237847518.ocFile/Kennzahlenberechnung%20RMSG%20(Version%201.2).xlsx",
 "sg_detailberechnungen_rmsg.pdf": "https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen/_jcr_content/Par/sgch_accordion_list_1344425806/AccordionListPar/sgch_accordion_228014448/AccordionPar/sgch_downloadlist/DownloadListPar/sgch_download.ocFile/Detailberechnungen%20Kennzahlen%20RMSG.pdf",
 "sg_fag_2025.xlsx": "https://www.sg.ch/content/dam/sgch/politik-verwaltung/gemeinden/gemeindenfinanzen/finanzausgleichsbeitr%C3%A4ge/FAG%202025%20Gesamtliste.xlsx",
}
for y in range(2011, 2026):
    pass
# Uri: Dokumente der Publikationsseite
st, ct, d = fetch("https://www.ur.ch/publikationen/6680")
ur = re.findall(r'<a title="Jahr (\d{4})" href="(/_doc/\d+)"', d.decode("utf-8", "replace"))
for y, h in sorted(set(ur)):
    DL[f"ur_gemeindefinanzstatistik_{y}.pdf"] = "https://www.ur.ch" + h
# BFS PxWeb: Metadaten der Bevölkerungstabelle
DL["bfs_px_bev_meta.json"] = "https://www.pxweb.bfs.admin.ch/api/v1/de/px-x-0102010000_101/px-x-0102010000_101.px"

for name, u in DL.items():
    st, ct, d = fetch(u)
    ok = st == 200 and len(d) > 0
    if ok: (RAW / name).write_bytes(d)
    log["files"][name] = {"url": u, "status": st, "content_type": ct, "bytes": len(d), "saved": ok,
                          "err": d[:160].decode("utf-8", "replace") if not ok else ""}
    print(name, st, len(d))
(OUT / "summary2.json").write_text(json.dumps(log, indent=1, ensure_ascii=False), encoding="utf-8")
