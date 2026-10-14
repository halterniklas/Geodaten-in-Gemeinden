# Linkprüfung – Geodaten_mit_Nummerierung.md

Stand 14.10.2026. Statische Prüfung (URL-Aufbau, Koordinaten, Layer-IDs).
Ein HTTP-Test war aus der Cloud-Umgebung nicht möglich, weil die geo.admin- und Kantonsportale gesperrt waren.
Der HTTP-Test lässt sich lokal nachholen: `python3 gis_betroffenheit.py Geodaten_mit_Nummerierung.md --links`.

## Fehler

| Nr | Link | Problem | Vorschlag |
| -- | ---- | ------- | --------- |
| 37 | Seelisberg (geo.ur.ch) | Die URL ist beschädigt: `…Zoom=13¢er%3D955909…`. `&cent` wurde als HTML-Entity in «¢» umgewandelt. Ausserdem ist der Parameter `layers=Nutzungsplanung%20%28Planproduk` abgeschnitten. | Den Link im Viewer neu erzeugen («Teilen»). |
| 37 | Seelisberg (geo.ur.ch) | `Lat=46.857 / Lng=8.661` liegt bei Altdorf/Bürglen, nicht in Seelisberg (ca. 46.97 N / 8.59 E). | Den Kartenausschnitt auf Seelisberg setzen. |
| 29 | Münchenstein (geoview.bl.ch) | `map_x=2621744 / map_y=1259205` liegt bei Liestal, nicht in Münchenstein (ca. 2613300 / 1263100). | Die Koordinaten durch `map_x=2613308&map_y=1263110` ersetzen. |

## Hinweise

| Nr | Link | Hinweis |
| -- | ---- | ------- |
| 35 | Wil (geoportal.ch/ktsg) | Das Zentrum `2717572 / 1252351` liegt rund 6 km südlich von Wil. Bei Massstab 1:50 000 ist Wil nur am Rand sichtbar. |
| 30, 31 | arp-daten.bl.ch / geoview.bl.ch | Die Links führen nur auf die Startseite, ohne Ausschnitt und ohne Layer. |
| 36 | geoportal.ch/ktsg | Der Link führt nur auf die Startseite. |
| 35 | Bemerkung | «Stand 03.09.2026»: bitte prüfen, ob das Datum stimmt. |
| alle | map.geo.admin.ch | Die Bundes-Links sind syntaktisch korrekt. `\&` ist nur Markdown-Escaping und wird als `&` gerendert. Die Zentren der drei Gemeinden passen. |
| – | Tabelle | Die Kopfzeile fehlte (Zeile 1 war eine Datenzeile). Sie wurde ergänzt. |

## Zeilen ohne Layer-ID (Kandidaten zum Ergänzen, bitte im Viewer bestätigen)

| Nr | Thema | möglicher Layer |
| -- | ----- | --------------- |
| 9 | Wasser- und Zugvogelreservate | `ch.bafu.bundesinventare-vogelreservate` |
| 12 | Schutzwald | Layer der Reihe `ch.bafu.silvaprotect-*` / «Schutzwald harmonisiert» (im Viewer suchen) |
| 17 | Wärmenetze / Wind | `ch.bfe.thermische-netze`, `ch.bfe.windenergie-*` |

Sobald eine Layer-ID in der Spalte «Layer-ID» steht, fragt das Skript die Zeile automatisch ab.
