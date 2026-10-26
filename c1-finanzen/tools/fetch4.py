"""Stufe 4 (GitHub-Runner): BFS-Bevölkerung per PxWeb-API, BFS-Gemeindegrenzen, BL-Open-Data (data.bl.ch)."""
import json, sys, pathlib, datetime, urllib.request, urllib.error, ssl, time

RAW = pathlib.Path(sys.argv[1]); RAW.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (c1-finanzen; research)"}
CTX = ssl.create_default_context()
log = {"retrieved": datetime.datetime.utcnow().isoformat() + "Z", "items": {}}

def req(u, data=None, headers=None, timeout=300, limit=400_000_000):
    h = dict(UA); h.update(headers or {})
    r = urllib.request.Request(u, data=data, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=timeout, context=CTX) as x:
            return x.status, x.headers.get("Content-Type", ""), x.read(limit)
    except urllib.error.HTTPError as e:
        return e.code, "", e.read()[:500]
    except Exception as e:
        return 0, "", repr(e).encode()

def save(name, u, st, ct, d, extra=None):
    ok = st == 200 and len(d) > 0
    if ok: (RAW / name).write_bytes(d)
    log["items"][name] = {"url": u, "status": st, "content_type": ct, "bytes": len(d), "saved": ok,
                          "err": "" if ok else d[:300].decode("utf-8", "replace"), **(extra or {})}
    print(name, st, len(d), flush=True)

# 1) BFS PxWeb: ständige Wohnbevölkerung, Gemeinden SG/BL/UR, je Jahr, alle Alter, Total Geschlecht/Staatsang.
PX = "https://www.pxweb.bfs.admin.ch/api/v1/de/px-x-0102010000_101/px-x-0102010000_101.px"
st, ct, d = req(PX)
meta = json.loads(d)
vmap = {v["code"]: v for v in meta["variables"]}
gcode = "Kanton (-) / Bezirk (>>) / Gemeinde (......)"
codes, texts = vmap[gcode]["values"], vmap[gcode]["valueTexts"]
want_kt = {"- St. Gallen", "- Basel-Landschaft", "- Uri"}
cur = None; sel = []
for c, t in zip(codes, texts):
    if t.startswith("- "): cur = t
    elif t.startswith("......") and cur in want_kt: sel.append(c)
print("Gemeinden gewählt:", len(sel))
ages = [v for v in vmap["Alter"]["values"] if v != "-99999"]
for jahr in vmap["Jahr"]["values"]:
    q = {"query": [
        {"code": "Jahr", "selection": {"filter": "item", "values": [jahr]}},
        {"code": gcode, "selection": {"filter": "item", "values": sel}},
        {"code": "Bevölkerungstyp", "selection": {"filter": "item", "values": ["1"]}},
        {"code": "Staatsangehörigkeit (Kategorie)", "selection": {"filter": "item", "values": ["-99999"]}},
        {"code": "Geschlecht", "selection": {"filter": "item", "values": ["-99999"]}},
        {"code": "Alter", "selection": {"filter": "item", "values": ages}}],
        "response": {"format": "csv"}}
    st, ct, d = req(PX, data=json.dumps(q).encode(), headers={"Content-Type": "application/json"})
    save(f"bfs_statpop_sg_bl_ur_{jahr}.csv", PX, st, ct, d, {"table": "px-x-0102010000_101", "jahr": jahr})
    time.sleep(1)

# 2) BFS generalisierte Gemeindegrenzen (Gebietsstand 2025)
u = "https://dam-api.bfs.admin.ch/hub/api/dam/assets/34367751/master"
st, ct, d = req(u); save("bfs_gemeindegrenzen_gg25.zip", u, st, ct, d)

# 3) BL: data.bl.ch (Opendatasoft)
for ds in ["10640", "10650"]:
    base = f"https://data.bl.ch/api/explore/v2.1/catalog/datasets/{ds}"
    st, ct, d = req(base); save(f"bl_dataset_{ds}_meta.json", base, st, ct, d)
    u = base + "/exports/csv?delimiter=%3B&lang=de&timezone=UTC&use_labels=false"
    st, ct, d = req(u); save(f"bl_dataset_{ds}.csv", u, st, ct, d)
st, ct, d = req("https://data.bl.ch/api/explore/v2.1/catalog/datasets?limit=100&where=search(%22Gemeinde%22)")
save("bl_catalog_gemeinde.json", "data.bl.ch catalog search Gemeinde", st, ct, d)
st, ct, d = req("https://data.bl.ch/api/explore/v2.1/catalog/datasets?limit=100&where=search(%22Finanz%22)")
save("bl_catalog_finanz.json", "data.bl.ch catalog search Finanz", st, ct, d)

# 4) UR 2012 erneut
st, ct, d = req("https://www.ur.ch/publikationen/6680", timeout=120)
import re
m = re.findall(r'<a title="Jahr 2012" href="(/_doc/\d+)"', d.decode("utf-8", "replace"))
if m:
    u = "https://www.ur.ch" + m[0]; st, ct, d = req(u, timeout=300); save("ur_gemeindefinanzstatistik_2012.pdf", u, st, ct, d)
(RAW / "_fetch4_log.json").write_text(json.dumps(log, indent=1, ensure_ascii=False), encoding="utf-8")
