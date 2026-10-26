# C1 – Finanzielle Ausgangslage und Tragfähigkeit von Gemeinden (SG, BL, UR)

Reproduzierbares R-Projekt: Datenbeschaffung → Aufbereitung → Statistik/ML → deutscher Quarto-Bericht.

* **A:** Erklärt das Bevölkerungswachstum den Selbstfinanzierungsanteil (SFA)?
* **B:** Hängt die Bauzonenfläche je Einwohner (ARE 2022) mit dem SFA zusammen? (Sekundär: Nettoschuld je EW.)
* **Zielgemeinden** (nie im Training/Tuning/Validierung): Wil SG (3427), Münchenstein BL (2769), Seelisberg UR (1215).

Ergebnis: `report/bericht.html` (nach dem Lauf). Alle Aussagen sind **prädiktiv/beschreibend, nicht kausal**.

## Schnellstart (lokal, RStudio)

1. `c1-finanzen.Rproj` in RStudio öffnen.
2. `R/00_run_lokal.R` öffnen → *Source* (installiert fehlende Pakete, lädt Rohdaten, rechnet alles, rendert den Bericht).
   Alternativ: `source("R/run_all.R")`. Laufzeit ca. 10–15 min.
3. Quarto (>= 1.4) wird nur für den Bericht benötigt: <https://quarto.org>.
4. Für identische Paketversionen: `renv::restore()` (sofern `renv.lock` vorhanden), sonst siehe Tabelle «Paketversionen» im Bericht.

Hinweis Zeichensatz: Die Skripte sind UTF-8; `00_setup.R` setzt bei Bedarf eine UTF-8-Locale.

## Ordner

| Pfad | Inhalt |
|---|---|
| `R/00_setup.R` | Konfiguration (Seed `20261026`, Folds, Zielgemeinden), Pfade, Hilfsfunktionen |
| `R/01_download.R` | Rohdaten laden (überspringt vorhandene Dateien), schreibt `data/raw/quellenprotokoll.csv` |
| `R/01b_dateninventur_quellen.R` | Quelleninventur (`output/tables/inventur_quellen.csv`) |
| `R/02_aufbereitung.R` | Verknüpfung über BFS-Nr. und Jahr, Gebietsstand 2025, Panel und Querschnitt |
| `R/03_modelle.R, 03a, 03b` | Nested-CV-Modelle (Null, lm, RF, GAM, XGBoost), OOF-Vorhersagen, Folds |
| `R/04_inferenz_diagnostik.R` | lm mit clusterrobusten SE, Panel-FE, GAM, Breusch–Pagan, VIF, Moran’s I |
| `R/05_visualisierung.R` | Karten, Streudiagramme, Zeitreihen, PDP/ALE, GAM-Effekte, Residuen |
| `R/06_zielgemeinden.R` | Vorhersage und Einordnung der Zielgemeinden |
| `report/bericht.qmd` | Deutscher Bericht (HTML, eigenständig) |
| `data/raw/` | Rohdaten, **unverändert** |
| `data/processed/` | aufbereitete Daten |
| `output/tables`, `output/figures`, `output/models` | CSV-Tabellen, Abbildungen, Fold-Zuordnungen und OOF-Vorhersagen |
| `tools/`, `.github/workflows/` | Hilfsskripte und GitHub-Actions für den Datenabruf von einem Runner mit freiem Internetzugang |

## Datenquellen (Details und Abrufdatum: `data/raw/quellenprotokoll.csv`)

BFS STATPOP (PxWeb), BFS Gemeindegrenzen gg25, ARE Bauzonenstatistik 2022, Kanton SG (RMSG-Kennzahlen), Kanton BL (data.bl.ch, Datensätze 10640/10650), Kanton UR (Finanzkontrolle, Gemeindefinanzstatistik-PDF).

Die Rohdaten im Repository wurden über GitHub Actions (`c1-daten.yml`) abgerufen, weil einzelne Seiten aus der Entwicklungsumgebung nicht erreichbar waren. `01_download.R` lädt sie auch lokal; fehlt ein Zugriff, die Dateien manuell nach `data/raw/download/` legen (Namen siehe Quellenprotokoll). Der Bot-Schutz von baselland.ch wurde **nicht umgangen**.

## Methodik in Kürze

Nested CV (5 äussere Folds, innere 3-fach-Tuning), alle Jahre einer Gemeinde im selben Fold; zusätzlich räumlich geblockte CV und zeitlich vorwärts. Metriken R² (1 − SSE/SST, kann negativ sein), RMSE, MAE, MSE; Zusatznutzen per Cluster-Bootstrap. **MaxEnt** ausgeschlossen (Presence-Background-Verfahren, für kontinuierliche Finanzgrössen ungeeignet). **Keine Klassifikation** (AUC/Kappa/MaxKappa nicht anwendbar).

## Bekannte Grenzen

SG-Daten erst ab 2019 und mögliche SFA-Definitionsänderung (RMSG v1.2); UR ohne Steuerkraft und nur Nettoschuld II; kein Luucy-Export; kein einheitlicher Steuerkraftindex; kleine Fallzahl in B. Siehe Kapitel «Grenzen» im Bericht.

## Tests auf frischer Maschine

GitHub-Actions-Workflow `c1-pipeline-test.yml` (manuell startbar) installiert R, Pakete und Quarto, lädt die Rohdaten neu und führt die Pipeline aus.
