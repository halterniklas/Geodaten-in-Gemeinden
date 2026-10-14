#!/usr/bin/env python3
"""Betroffenheit der Gemeinden pro Layer (map.geo.admin.ch / api3.geo.admin.ch).

Für jede Zeile der Tabelle mit einer Bundes-Layer-ID wird geprüft, ob der Layer
innerhalb der Gemeindegrenze (swissBOUNDARIES3D) von Münchenstein, Wil (SG) und
Seelisberg vorkommt. Das Ergebnis (ja / nein) wird in die Spalten
«Betroffenheit» eingetragen. Zeilen ohne Layer-ID oder mit «n. a.» bleiben
unverändert.

Methode:
  1. Gemeindefläche via REST «find» auf
     ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill (LV95, EPSG:2056).
  2. Polygon um 5 m nach innen puffern (damit Objekte, die nur die Grenze der
     Nachbargemeinde berühren, nicht zählen) und vereinfachen (URL-Länge).
  3. REST «identify» mit geometryType=esriGeometryPolygon, tolerance=0,
     limit=1 -> mindestens ein Treffer = «ja», kein Treffer = «nein».

Aufruf:
  pip install shapely
  python3 gis_betroffenheit.py Geodaten_mit_Nummerierung.md            # Tabelle aktualisieren
  python3 gis_betroffenheit.py Geodaten_mit_Nummerierung.md --links    # zusätzlich Links prüfen (HTTP)
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

from shapely.geometry import shape, mapping, Polygon, MultiPolygon

API = "https://api3.geo.admin.ch/rest/services/api/MapServer"
BOUNDARY_LAYER = "ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill"

# Spaltenindex in der Tabelle -> Gemeinde (Name in swissBOUNDARIES3D, Kanton)
GEMEINDEN = {
    10: ("Münchenstein", "BL"),
    11: ("Wil (SG)", "SG"),
    12: ("Seelisberg", "UR"),
}
COL_LAYER = 5
INNER_BUFFER_M = 5
MAX_URL = 7500
IDENTIFY_LIMIT = 50
SUCH_BEGRIFFE = ["wildtier", "oberflaechenabfluss", "Oberflächenabfluss", "laerm", "vogel",
                 "schutzwald", "silvaprotect", "thermische", "windenergie", "geotherm",
                 "hitze", "stoerfall", "Störfall", "gefahren", "belastete"]


def get_json(url, params):
    full = url + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(full, timeout=60) as r:
        return json.load(r)


def gemeinde_polygon(name):
    data = get_json(f"{API}/find", {
        "layer": BOUNDARY_LAYER, "searchText": name, "searchField": "gemname",
        "contains": "false", "returnGeometry": "true", "geometryFormat": "geojson",
        "sr": 2056,
    })
    # Gemeindenamen sind in swissBOUNDARIES3D eindeutig («Wil (SG)»)
    feats = [f for f in data["results"]
             if name in (f.get("properties", {}).get("gemname"), f.get("label"))]
    if not feats:
        sys.exit(f"Gemeinde nicht gefunden: {name}\n{json.dumps(data)[:2000]}")
    geom = shape(feats[0]["geometry"])
    for f in feats[1:]:
        geom = geom.union(shape(f["geometry"]))
    return geom


def esri_rings(geom):
    polys = geom.geoms if isinstance(geom, MultiPolygon) else [geom]
    rings = []
    for p in polys:
        rings.append([[round(x, 1), round(y, 1)] for x, y in p.exterior.coords])
        rings += [[[round(x, 1), round(y, 1)] for x, y in i.coords] for i in p.interiors]
    return rings


def query_geometry(geom):
    """Puffern + so stark vereinfachen, dass die identify-URL kurz genug ist."""
    g = geom.buffer(-INNER_BUFFER_M)
    for tol in (2, 5, 10, 20, 40, 80):
        s = g.simplify(tol, preserve_topology=True)
        js = json.dumps({"rings": esri_rings(s), "spatialReference": {"wkid": 2056}},
                        separators=(",", ":"))
        if len(urllib.parse.quote(js)) < MAX_URL:
            break
    return js, s.bounds, g


def feature_label(f):
    props = f.get("properties") or f.get("attributes") or {}
    for key in ("label", "name", "objname", "obj_name", "bezeichnung", "titel"):
        if f.get(key):
            return str(f[key])
        if props.get(key):
            return str(props[key])
    return str(f.get("featureId", f.get("id", "?")))


def identify(layer_id, geom_json, bounds, exact):
    """Treffer per identify holen und lokal exakt mit der Gemeindefläche verschneiden.

    Gibt ("ja"|"nein", [Namen der Treffer]) zurück.
    """
    minx, miny, maxx, maxy = bounds
    data = get_json(f"{API}/identify", {
        "geometry": geom_json, "geometryType": "esriGeometryPolygon",
        "layers": f"all:{layer_id}", "sr": 2056, "tolerance": 0,
        "mapExtent": f"{minx},{miny},{maxx},{maxy}", "imageDisplay": "1000,1000,96",
        "returnGeometry": "true", "geometryFormat": "geojson", "limit": IDENTIFY_LIMIT,
        "lang": "de",
    })
    hits = []
    for f in data.get("results", []):
        g = f.get("geometry")
        try:
            inside = g is None or shape(g).intersects(exact)
        except Exception:  # noqa: BLE001 - ungültige Geometrie: Server-Treffer gelten
            inside = True
        if inside:
            hits.append(feature_label(f))
    return ("ja" if hits else "nein"), sorted(set(hits))


def search_layers(layers_config, keywords):
    lines = []
    for kw in keywords:
        lines.append(f"## {kw}")
        for lid, cfg in sorted(layers_config.items()):
            if kw.lower() in lid.lower() or kw.lower() in str(cfg.get("label", "")).lower():
                lines.append(f"- {lid} | {cfg.get('label', '')} | queryable={cfg.get('queryable')}")
        lines.append("")
    return "\n".join(lines)


def parse_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def format_row(cells):
    return "| " + " | ".join(cells) + " |"


def check_links(lines):
    import re
    seen = set()
    for url in re.findall(r"\]\((https?://[^)]+)\)", "\n".join(lines)):
        url = url.replace("\\&", "&")
        if url in seen:
            continue
        seen.add(url)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception as e:  # noqa: BLE001
            status = type(e).__name__
        print(f"{status}\t{url}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("table")
    ap.add_argument("--links", action="store_true", help="HTTP-Status aller Links ausgeben")
    ap.add_argument("--details", default="Betroffenheit_Details.md",
                    help="Datei mit den Namen der Treffer pro Layer und Gemeinde")
    ap.add_argument("--layersuche", default="layer_suche.md",
                    help="Datei mit Layer-IDs zu Suchbegriffen (für fehlende/ungültige IDs)")
    ap.add_argument("--dry-run", action="store_true", help="nur ausgeben, Datei nicht schreiben")
    args = ap.parse_args()

    with open(args.table, encoding="utf-8") as f:
        lines = f.read().splitlines()

    if args.links:
        check_links(lines)

    layers_config = get_json(f"{API}/layersConfig", {"lang": "de"})
    with open(args.layersuche, "w", encoding="utf-8") as f:
        f.write("# Layer-Suche in layersConfig (api3.geo.admin.ch)\n\n")
        f.write(search_layers(layers_config, SUCH_BEGRIFFE))
    details = ["# Betroffenheit – Treffer pro Layer und Gemeinde", "",
               f"Methode: identify auf api3.geo.admin.ch, Treffer lokal mit der um {INNER_BUFFER_M} m "
               "nach innen gepufferten Gemeindefläche (swissBOUNDARIES3D) verschnitten. "
               f"Pro Abfrage max. {IDENTIFY_LIMIT} Objekte.", "",
               "| Nr | Layer | Gemeinde | Ergebnis | Treffer |", "| -- | ----- | -------- | -------- | ------- |"]
    geoms = {}
    for col, (name, _) in GEMEINDEN.items():
        geoms[col] = query_geometry(gemeinde_polygon(name))
        print(f"Gemeindegrenze geladen: {name}", file=sys.stderr)

    out = []
    for line in lines:
        if not line.startswith("|") or set(line) <= set("|- "):
            out.append(line)
            continue
        cells = parse_row(line)
        layer = cells[COL_LAYER] if len(cells) > COL_LAYER else ""
        if not layer.startswith("ch."):
            out.append(line)
            continue
        cfg = layers_config.get(layer)
        for col, (name, _) in GEMEINDEN.items():
            if cells[col].replace(" ", "") == "n.a.":
                continue
            if cfg is None:
                cells[col] = "Layer-ID ungültig"
            elif not cfg.get("queryable", True):
                cells[col] = "nicht abfragbar"
            else:
                hits = []
                try:
                    cells[col], hits = identify(layer, *geoms[col])
                except urllib.error.HTTPError as e:
                    body = e.read()[:500].decode("utf-8", "replace")
                    if "No GeoTable" in body:
                        cells[col] = "nicht abfragbar (Rasterlayer)"
                    else:
                        cells[col] = f"Fehler {e.code}"
                        print(body, file=sys.stderr)
                shown = ", ".join(hits[:15]) + (f" … (+{len(hits) - 15})" if len(hits) > 15 else "")
                details.append(f"| {cells[0]} | {layer} | {name} | {cells[col]} | {shown.replace('|', '/')} |")
            print(f"{cells[0]:>3} {layer:55} {name:14} {cells[col]}", file=sys.stderr)
        out.append(format_row(cells))

    with open(args.details, "w", encoding="utf-8") as f:
        f.write("\n".join(details) + "\n")

    text = "\n".join(out) + "\n"
    if args.dry_run:
        print(text)
    else:
        with open(args.table, "w", encoding="utf-8") as f:
            f.write(text)


if __name__ == "__main__":
    main()
