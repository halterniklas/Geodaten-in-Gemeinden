"""Sondiert die öffentlichen Datenquellen (läuft auf dem GitHub-Runner) und
speichert Status, Content-Type und gefundene Datei-Links nach data/raw/_probe/."""
import json, re, sys, pathlib, urllib.request, urllib.parse, datetime, ssl

OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (c1-finanzen probe; research)"}
PAGES = {
 "are_bauzonen": "https://www.are.admin.ch/de/bauzonenstatistik-schweiz",
 "kgk_bauzonen": "https://www.kgk-cgc.ch/geodaten/geodaten-bauzonen-schweiz",
 "sg_gemeindefinanzen": "https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen.html",
 "sg_stada2": "https://stada2.sg.ch/",
 "bl_statistik": "https://statistik.bl.ch/",
 "ur_publikation": "https://www.ur.ch/publikationen/6680",
 "bfs_statpop": "https://www.bfs.admin.ch/bfs/de/home/statistiken/bevoelkerung/stand-entwicklung/bevoelkerung.html",
 "bfs_gemeindeverzeichnis": "https://www.bfs.admin.ch/bfs/de/home/grundlagen/agvch.html",
 "swisstopo_swissboundaries": "https://www.swisstopo.admin.ch/de/landschaftsmodell-swissboundaries3d",
}
APIS = {
 "ckan_bauzonen": "https://ckan.opendata.swiss/api/3/action/package_show?id=bauzonenstatistik-schweiz",
 "ckan_statpop_2010_2024": "https://ckan.opendata.swiss/api/3/action/package_show?id=standige-und-nichtstandige-wohnbevolkerung-nach-institutionellen-gliederungen-staatsa-2010-2024",
 "ckan_search_finanzen_sg": "https://ckan.opendata.swiss/api/3/action/package_search?q=gemeindefinanzen&rows=50",
 "ckan_search_finanzen_bl": "https://ckan.opendata.swiss/api/3/action/package_search?q=finanzen+gemeinden+basel-landschaft&rows=50",
 "ckan_search_selbstfinanzierung": "https://ckan.opendata.swiss/api/3/action/package_search?q=selbstfinanzierung&rows=50",
 "ckan_search_steuerkraft": "https://ckan.opendata.swiss/api/3/action/package_search?q=steuerkraft&rows=50",
 "ckan_search_gemeindegrenzen": "https://ckan.opendata.swiss/api/3/action/package_search?q=generalisierte+gemeindegrenzen&rows=20",
 "bfs_pxweb_root": "https://www.pxweb.bfs.admin.ch/api/v1/de/",
 "bfs_pxweb_bev": "https://www.pxweb.bfs.admin.ch/api/v1/de/px-x-0102010000_101",
 "bfs_pxweb_bev_alt": "https://www.pxweb.bfs.admin.ch/api/v1/de/px-x-0102010000_201",
 "bfs_pxweb_fin": "https://www.pxweb.bfs.admin.ch/api/v1/de/px-x-1803010000_101",
 "stat_bl_api": "https://statistik.bl.ch/api/3/action/package_search?q=finanzen",
 "opendata_bl": "https://opendata.bl.ch/api/explore/v2.1/catalog/datasets?limit=100&where=search(%22Gemeindefinanzen%22)",
 "opendata_sg": "https://daten.sg.ch/api/explore/v2.1/catalog/datasets?limit=100&where=search(%22Finanz%22)",
}
ctx = ssl.create_default_context()
def get(url, binary=False, limit=3_000_000):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
            data = r.read(limit)
            return r.status, r.headers.get("Content-Type", ""), data
    except urllib.error.HTTPError as e:
        return e.code, "", str(e).encode()
    except Exception as e:
        return 0, "", repr(e).encode()

summary = {"retrieved": datetime.datetime.utcnow().isoformat() + "Z", "pages": {}, "apis": {}}
EXT = re.compile(r'href="([^"]+\.(?:xlsx?|csv|pdf|zip|gpkg|json|px)(?:\?[^"]*)?)"', re.I)
for k, u in PAGES.items():
    st, ct, data = get(u)
    txt = data.decode("utf-8", "replace")
    links = sorted({urllib.parse.urljoin(u, m) for m in EXT.findall(txt)})
    (OUT / f"page_{k}.html").write_text(txt[:400000], encoding="utf-8")
    summary["pages"][k] = {"url": u, "status": st, "content_type": ct, "bytes": len(data), "file_links": links}
    print(k, st, len(data), len(links))
for k, u in APIS.items():
    st, ct, data = get(u)
    (OUT / f"api_{k}.json").write_bytes(data)
    summary["apis"][k] = {"url": u, "status": st, "content_type": ct, "bytes": len(data)}
    print(k, st, len(data))
(OUT / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
