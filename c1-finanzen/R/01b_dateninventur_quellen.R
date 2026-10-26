# ==============================================================================
# 01b_dateninventur_quellen.R – Dateninventur der Quellen (vor jeder Modellierung)
# Ergebnis: output/tables/inventur_quellen.csv
# Inhalt basiert auf der tatsächlichen Sondierung (data/raw/_probe/) und der Sichtung der Rohdateien.
# ==============================================================================
source("R/00_setup.R")
inv <- tribble(
  ~quelle, ~bezugsadresse, ~merkmale_einheiten, ~raum_abdeckung, ~zeit_abdeckung, ~gemeindeid, ~fehlwerte_brueche, ~verknuepfung, ~verwendung,
  "BFS STATPOP: Ständige und nichtständige Wohnbevölkerung nach institutionellen Gliederungen, Staatsangehörigkeit (Kategorie), Geschlecht und Alter, 2010–2025 (px-x-0102010000_101)",
  "https://www.pxweb.bfs.admin.ch/api/v1/de/px-x-0102010000_101/px-x-0102010000_101.px (PxWeb-API, POST; Metadaten per GET)",
  "Personen (Stichtag 31.12.), Einzelalter 0–100+; hier: ständige Wohnbevölkerung, Total Geschlecht und Staatsangehörigkeit",
  "Schweiz; abgefragt: 180 Gemeinden SG (75), BL (86), UR (19) im Gebietsstand 2025", "2010–2025 (Stichtag Jahresende)", "BFS-Gemeindenummer (4-stellig)",
  "Keine Fehlwerte. Bevölkerung wird rückwirkend im Gebietsstand 2025 geliefert (fusionierte Gemeinden zusammengefasst).", "direkt über BFS-Nr. und Jahr", "ja – Einwohnerzahl, Altersstruktur, Wachstum",
  "ARE Bauzonenstatistik Schweiz 2022, Resultate nach Gemeinden", "https://www.are.admin.ch/dam/de/sd-web/7cEPibyb2l-3/bauzonenstatistik_schweiz_2022_gemeinden.xlsx",
  "Bauzonenfläche nach Hauptnutzung (HN_11–HN_19) in Hektaren; Gebietsstand 1.1.2022; Erhebungsstand der kantonalen Nutzungsplanung 1.1.2022",
  "Schweiz (alle Gemeinden)", "Querschnitt 2022", "BFS-Gemeindenummer (Gem_No)",
  "Einzelne Hauptnutzungen fehlen (NA = 0 ha). Neckertal (SG, Fusion 2021) ohne Eintrag im Gebietsstand 2022 -> nicht verknüpfbar. Kein Messwert für Dichte oder Infrastrukturkosten.",
  "direkt über BFS-Nr.; Bevölkerung 31.12.2021 passt zum Stichtag 1.1.2022", "ja – Bauzonenbeanspruchung (m² je Einwohner)",
  "ARE Bauzonenstatistik 2012 und 2017 (ZIP mit Gemeinde-Excel)", "https://www.are.admin.ch/dam/de/sd-web/3lK47686QIeu/Bauzonenstatistik_Schweiz_2012.zip ; …/iLHkdaGp7qi3/Bauzonenstatistik_Schweiz_2017.zip",
  "Bauzonenflächen je Gemeinde (frühere Erhebungen)", "Schweiz", "2012, 2017", "BFS-Nr. (Gebietsstand der jeweiligen Erhebung)",
  "Methodische Anpassungen zwischen Erhebungen (harmonisierte Zonentypen erst ab 2017); Gebietsstände unterschiedlich", "über BFS-Nr. mit Fusionsharmonisierung nötig",
  "nein – heruntergeladen, nicht ausgewertet (Hauptanalyse = konsistenter Querschnitt 2022; keine künstliche Zeitreihe)",
  "KGK/CGC Geodaten Bauzonen Schweiz", "https://www.kgk-cgc.ch/geodaten/geodaten-bauzonen-schweiz", "Verweisseite auf Geodaten (Geobasisdaten Nutzungsplanung)", "Schweiz", "–", "–",
  "Seite erreichbar, enthält keine direkten Daten-Downloads (Verweis auf kantonale Stellen und geodienste.ch)", "–", "nein – Gemeindeaggregate liegen bereits in der ARE-Statistik vor",
  "SG: Kennzahlen neues Rechnungslegungsmodell der St.Galler Gemeinden (RMSG), Blätter 2017–2025",
  "https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen.html (Datei «Kennzahlen neues Rechnungslegungsmodell der St.Galler Gemeinden.xlsx»)",
  "Selbstfinanzierungsanteil (%), Selbstfinanzierungsgrad (%), Nettoschuld I und II je Einwohner (CHF), Nettoverschuldungsquotient, Zinsbelastungsanteil, Steuerfuss (%), einfache Steuer (100 %) je Einwohner (CHF), Einwohner",
  "75–77 Gemeinden SG", "2017–2025 (2017: 1, 2018: 11 Gemeinden befüllt; vollständig ab 2019)", "keine BFS-Nr.; Gemeindename (Verknüpfung über normalisierten Namen, eindeutig innerhalb SG)",
  "Rechnungsmodell-Umstellung RMSG (Lücken 2017/18); Definition Selbstfinanzierungsanteil in Version 1.2 (06.2025) angepasst; Fusionen (Hemberg, Oberhelfenschwil -> Neckertal) nicht im Gebietsstand 2025",
  "über normalisierten Namen + Kanton; Verknüpfungsprotokoll in inventur_nicht_verknuepfte_gemeinden.csv", "ja – Y (SFA), Nettoschuld I, Steuermass",
  "SG: Kennzahlenberechnung RMSG (Version 1.2) und Detailberechnungen", "https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen.html", "Definitionen und Rechenschema der Kennzahlen",
  "SG", "Berechnungsjahr 2024 (Muster)", "–", "PDF Detailberechnungen: Text nicht maschinenlesbar (Schriftkodierung)", "–", "ja – Definition Selbstfinanzierungsanteil dokumentiert (Selbstfinanzierung / laufender Ertrag)",
  "SG: Finanzausgleich Gesamtlisten FAG 2014–2027 (Excel/PDF)", "https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen.html", "Berechnungsarbeitsmappen Finanzausgleich (Ressourcen-, Sonderlastenausgleich)",
  "SG", "2014–2027", "Gemeindename", "Rechenblätter mit Eingabefeldern, keine saubere Gemeindetabelle der Steuerkraft; Parsing nicht robust", "über Name",
  "nein – Steuerkraft-Kontrolle stattdessen aus RMSG-Kennzahlen (einfache Steuer je Einwohner), nur für kantonale Sensitivität",
  "SG: STADA2 / statistik.sg.ch", "https://stada2.sg.ch/ ; https://www.statistik.sg.ch/", "Statistikdatenbank (interaktiv); open.data-Katalog daten.sg.ch enthält Kantonsrechnung und Volksschulträger-Zahlen, keine Gemeindefinanzkennzahlen",
  "SG", "–", "–", "keine Download-Schnittstelle für Gemeindefinanzkennzahlen gefunden", "–", "nein – RMSG-Excel deckt den Bedarf ab",
  "BL: Gemeindefinanzen nach Rechnungsteil, Funktion, Kontenart und Jahr (data.bl.ch Dataset 10640)", "https://data.bl.ch/api/explore/v2.1/catalog/datasets/10640/exports/csv (Opendatasoft)",
  "Beträge in CHF je Konto (HRM2, 4-/5-stellige Kontenarten) für Erfolgsrechnung, Investitionsrechnung, Bilanz; Gesamthaushalt", "86 Gemeinden BL", "2015–2025 (längere Reihe ab 2014 über separaten CSV-Link)", "BFS-Gemeindenummer (bfs_nummer)",
  "Keine Kennzahlen veröffentlicht -> Selbstfinanzierung, laufender Ertrag und Nettoschuld werden nach Finanzhandbuch BL Kap. 16 selbst berechnet (Konten 33, 35, 364–366, 389, 4391, 4490, 45, 489)", "direkt über BFS-Nr. und Jahr", "ja – Y (SFA), Nettoschuld je EW, Fiskalertrag je EW",
  "BL: Gemeindekennzahlen (data.bl.ch Dataset 10650)", "https://data.bl.ch/api/explore/v2.1/catalog/datasets/10650/exports/csv", "Gemeindeporträts: Fläche, Siedlungsfläche, Altersgruppen, Steuerfuss 2026 u. a.", "86 Gemeinden BL", "überwiegend 2024–2026 (Querschnitt)", "BFS-Gemeindenummer",
  "Nur aktuelle Querschnittswerte", "über BFS-Nr.", "nein – Kontrolle der Bevölkerungsdaten möglich, nicht modelliert",
  "BL: statistik.bl.ch / baselland.ch", "https://statistik.bl.ch/ (Weiterleitung auf baselland.ch)", "Statistikportal des Kantons", "BL", "–", "–",
  "statistik.bl.ch leitet auf baselland.ch weiter; dort Cloudflare-Bot-Prüfung (HTTP 403 «Just a moment») für automatisierte Abrufe; keine Umgehung versucht", "–", "nein – Daten stattdessen über data.bl.ch (offener Datenkatalog)",
  "UR: Gemeindefinanzstatistik, Berichte der Finanzkontrolle Uri (PDF je Berichtsjahr)", "https://www.ur.ch/publikationen/6680 (Dokumente /_doc/<Nr>)",
  "Selbstfinanzierungsanteil (abs. CHF und % des laufenden Ertrags), Selbstfinanzierungsgrad, Nettoschuld II (abs., je Einwohner), Nettoinvestitionen u. a. als Mehrjahrestabellen", "20 Gemeinden UR (19 im Gebietsstand 2025)",
  "Berichtsjahre 2011–2025; Kennzahlenreihen je Bericht ca. 6 Jahre", "keine BFS-Nr.; Gemeindename", "HRM2 seit 1.1.2012; Kennzahlen ab 2014 nach überarbeiteter Fachempfehlung; Bauen (Fusion 2021) nicht im Gebietsstand 2025; nur Nettoschuld II; kein Steuerkraft-/Fiskalertrag je Gemeinde",
  "über Namen + Kanton", "ja – Y (SFA); Nettoschuld II nicht vergleichbar",
  "BFS Generalisierte Gemeindegrenzen (Gebietsstand 2025)", "https://dam-api.bfs.admin.ch/hub/api/dam/assets/34367751/master (ZIP)", "Polygone, Kantonskürzel, Gemeindezentren (LV95)", "Schweiz", "Gebietsstand 1.1.2025", "BFS-Gemeindenummer (GDENR)",
  "–", "direkt über BFS-Nr.", "ja – Karten, Kantonszuordnung, räumliche Blöcke und Moran's I",
  "swisstopo swissBOUNDARIES3D", "https://www.swisstopo.admin.ch/de/landschaftsmodell-swissboundaries3d", "Landesgrenzen (Seite zeigt nur Produktinfos)", "Schweiz", "–", "BFS-Nr.", "Download über geo.admin.ch/STAC nicht erschlossen", "–", "nein – BFS-Grenzen genügen",
  "Luucy (lokale Exporte)", "Repository halterniklas/geodaten-in-gemeinden (Kataster-/Q-Rahmen-Excel, Markdown)", "C_Grundlagenkataster_verifiziert.xlsx und Q-Rahmen-Dateien: Quellenverzeichnisse (7 Erwähnungen von Luucy)", "3 Gemeinden (Dokumentenlisten)", "Stand 14.10.2026", "–",
  "Keine Gemeindeattribute, keine Finanz- oder Raumdaten; keine Luucy-Exporte mit Attributen vorhanden", "–", "nein – nichts Verwertbares vorhanden; keine Luucy-Inhalte angenommen"
)
write_tab(inv, "inventur_quellen.csv")
cat("Dateninventur Quellen:", nrow(inv), "Quellen\n")
