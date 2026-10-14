# Geodaten in Gemeinden

Arbeitsrepository für die drei Pilotgemeinden **Seelisberg (UR)**, **Münchenstein (BL)** und **Wil (SG)**.

| Bereich | Dateien | Workflow |
|---|---|---|
| C-Grundlagenkataster (institutionelle Ausgangslage, C1–C5) | `data/`, `scripts/verify_c_sources.py`, `C_Grundlagenkataster_verifiziert.xlsx`, `reports/` | `.github/workflows/verify-c-sources.yml` |
| GIS-Betroffenheit (Bundes-Geodaten) | `gis_betroffenheit.py`, `Geodaten_mit_Nummerierung.md` u. a. | `.github/workflows/betroffenheit.yml` |

## C-Grundlagenkataster

### Dateien

| Datei | Inhalt |
|---|---|
| `data/C_Grundlagenkataster_Schweiz_Kantone_Gemeinden.xlsx` | Ausgangsdatei (unverändert, verbindliche Basis) |
| `data/quellen_kuratiert.json` | Kuratierte Korrekturen bestehender Zeilen (nach ID), neue Quellen mit erwarteten Schlüsselwörtern, präzisierte Gemeindeanfragen, Textbausteine für den Bericht |
| `data/discovery_seeds.json` | Offizielle Einstiegsseiten, Sitemaps und optionale Suchanfragen für die automatische Recherche |
| `scripts/verify_c_sources.py` | Prüf- und Erzeugungsskript |
| `C_Grundlagenkataster_verifiziert.xlsx` | Ergebnis: verifizierter Kataster |
| `reports/link_validation.csv` | Ein Eintrag pro Katalogzeile: ID, ursprüngliche URL, geprüfte URL, finale URL, HTTP-Status, Ergebnis, Inhaltsprüfung, Prüfdatum (Trennzeichen `;`, UTF-8 mit BOM für Excel) |
| `reports/link_validation.json` | Rohdaten aller Prüfungen (auch Cache für `--offline`) |
| `reports/discovery_kandidaten.csv` | Alle automatisch gefundenen, ungeprüften Dokumentkandidaten |
| `reports/recherchebericht.md` | Recherchebericht (Kennzahlen, ersetzte Links, neue Quellen nach C1–C5, Datenlücken, Unsicherheiten, Empfehlungen) |
| `reports/lauf.log` | Protokoll des letzten Runner-Laufs |

### Was das Skript macht

1. Liest die Ausgangsdatei und vergibt jeder Zeile der Gesamtübersicht eine stabile ID (`CH-`, `UR-`, `BL-`, `SG-`, `SEE-`, `MUE-`, `WIL-` + Dimension + Nummer).
2. Spielt die kuratierten Korrekturen und neuen Quellen ein. Ersetzte Links werden in der Spalte «Änderungsprotokoll» mit alter URL und Grund festgehalten; die alte URL wird ebenfalls geprüft.
3. Prüft jede URL: Syntax → DNS → HEAD (Fallback GET, da manche Behördenserver HEAD blockieren) → GET (max. 30 MB) mit Weiterleitungsauflösung, Dateityp-Erkennung, Titel- und Textextraktion (HTML, PDF via `pypdf`). Bundesrecht wird über den Fedlex-SPARQL-Endpunkt, kantonales Recht über die JSON-Schnittstelle der LexWork-Sammlungen identifiziert, weil diese Seiten JavaScript-Anwendungen sind.
4. Gleicht Titel/Text mit den erwarteten Schlüsselwörtern und dem Ort ab → «Bestätigt», «Teilweise bestätigt» oder «Offen». **HTTP 200 allein gilt nicht als Verifikation.** Fehlerseiten mit Status 200 (Soft-404) werden als Fehler erkannt.
5. Automatische Recherche: Einstiegsseiten (1–2 Ebenen, `robots.txt` wird beachtet) und XML-Sitemaps der Gemeinden werden nach Dokumentlinks durchsucht, die Stichworten zu C1–C5 entsprechen. Optional zusätzlich die Brave Search API. Funde landen **ungeprüft** im Blatt «Recherche-Kandidaten» und in `reports/discovery_kandidaten.csv`; übernommen werden sie erst nach Sichtung über `data/quellen_kuratiert.json`.
6. Schreibt die Exceldatei und die Berichte.

Netzwerkverhalten: Timeout 25 s, 3 Versuche mit exponentiellem Backoff (Verbindungsfehler, 429, 5xx, `Retry-After` wird beachtet), max. 6 parallele Anfragen, mindestens 1,5 s Abstand pro Host, ehrlicher User-Agent. Zugriffssperren (401/403/451), CAPTCHAs und Logins werden nicht umgangen, sondern als «Nicht prüfbar» markiert.

### Excel-Struktur

- **Gesamtübersicht** ist die zentrale Tabelle. Spalten A–Y der Ausgangsdatei bleiben in Bezeichnung und Reihenfolge erhalten (um eine Position nach rechts verschoben); vorne steht neu die **ID**, hinten folgen die Prüf- und Metadatenfelder (Linkstatus, HTTP-Status, Finale URL, Dateityp, Inhaltsprüfung mit Nachweis, Linkstabilität, Quellenverfügbarkeit, Prüfnachweis, Bewertungsbegründung, Gemeindeanfrage erforderlich, Zuständige Stelle, Bearbeitungsstatus, Recherchehinweis, Gleiche Quelle wie, Änderungsprotokoll).
- **Seelisberg / Münchenstein / Wil** sind generierte Ansichten (Bund + eigener Kanton + eigene Gemeinde). Die Spalte «Abgleich mit Gesamtübersicht» meldet per Formel, wenn eine Zeile von der Gesamtübersicht abweicht; im Blatt «Hinweise» prüft je eine Formel die Zeilenzahl (Soll/Ist).
- **Gemeindeanfragen**: bestehende Anfragen bleiben erhalten (Spalten B–G), ergänzt um Anfrage-ID, Quellenstatus, Recherchebefund, Bezug zur Katalog-ID, präzisierte Frage und zuständige Stelle.
- **Recherche-Kandidaten**: automatische Funde, ungeprüft.
- **Bewertungslogik**: unverändert, ergänzt um die Spalte «Anwendung im verifizierten Stand».
- **Legende**: Definition aller Statuswerte.
- Dropdowns für Ebene, C-Dimension, Tragfähigkeit, Confidence, Prüfstatus, Linkstatus, Inhaltsprüfung, Quellenverfügbarkeit, Gemeindeanfrage, Bearbeitungsstatus; bedingte Formatierung für Link- und Inhaltsstatus; Filter, fixierte Kopfzeile, klickbare Links.
- Tragfähigkeit bleibt «Noch nicht bewertet». Das Skript bricht ab, wenn eine Einstufung ohne Bewertungsbegründung eingetragen wird.

### Lokal ausführen

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/verify_c_sources.py                 # vollständiger Lauf (Internet nötig)
python3 scripts/verify_c_sources.py --no-discovery  # nur Linkprüfung + Excel
python3 scripts/verify_c_sources.py --offline       # ohne Netz, Prüfergebnisse aus reports/link_validation.json
```

Nach manueller Bearbeitung der Gesamtübersicht die Gemeindeblätter neu erzeugen:

```bash
python3 scripts/verify_c_sources.py --sync-only C_Grundlagenkataster_verifiziert.xlsx
```

Dauerhafte Änderungen gehören in `data/quellen_kuratiert.json` (sonst überschreibt der nächste Lauf sie).

### GitHub Actions

Workflow **«C-Grundlagenkataster prüfen»** (`.github/workflows/verify-c-sources.yml`):

- manuell: *Actions → C-Grundlagenkataster prüfen → Run workflow* (Optionen: automatische Recherche, Ergebnisse committen);
- automatisch bei Push auf `claude/**`-Branches, wenn sich Skript, `data/`, `requirements.txt` oder der Workflow ändern.

Der Lauf (Ubuntu, Python 3.12) installiert `requirements.txt`, führt das Skript aus, schreibt eine Kurzfassung in die Job-Zusammenfassung, lädt Exceldatei und `reports/` als Artifact `c-grundlagenkataster-<Laufnummer>` hoch (90 Tage) und committet die Ergebnisse in den Branch zurück.

### Secrets

| Secret | Pflicht | Zweck |
|---|---|---|
| `BRAVE_SEARCH_API_KEY` | nein | Ergänzt die automatische Recherche um die Brave Search API. Ohne Secret läuft die kostenfreie Recherche über Einstiegsseiten und Sitemaps. |

`GITHUB_TOKEN` wird automatisch bereitgestellt (Schreibrecht für den Ergebnis-Commit).

### Reproduzierbarkeit

- Abhängigkeiten sind in `requirements.txt` versioniert.
- Eingaben sind versioniert (`data/`); die Ausgangsdatei wird nie überschrieben.
- IDs sind deterministisch; Prüfdatum und Laufnummer stehen in Excel und Bericht.
- Webinhalte ändern sich: Ein neuer Lauf kann andere Ergebnisse liefern. Massgeblich ist der Stand im jeweiligen Artifact bzw. Commit.
