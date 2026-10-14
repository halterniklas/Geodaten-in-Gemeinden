# Recherchebericht C-Grundlagenkataster

Erzeugt am 14.10.2026 13:28 durch `scripts/verify_c_sources.py` im GitHub-Actions-Lauf [38566709480](https://github.com/halterniklas/Geodaten-in-Gemeinden/actions/runs/38566709480).
Kuratierungsstand der Quellenliste: 2026-10-14.

> Grundsatz: Nachvollziehbarkeit vor scheinbarer Vollständigkeit. HTTP 200 gilt nicht als Verifikation; «Bestätigt» heisst, dass erwartete Schlüsselwörter und Ort im Dokument gefunden wurden. Tragfähigkeit wurde nirgends eingestuft.

## 1 Kennzahlen

| Kennzahl | Anzahl |
|---|---:|
| Katalogzeilen gesamt | 100 |
| Davon ursprüngliche Zeilen | 40 |
| Geprüfte eindeutige URLs (inkl. ersetzter Alt-Links) | 105 |
| Erreichbar ohne Umleitung (Verifiziert) | 60 |
| Erreichbar nach Weiterleitung | 3 |
| Fehler | 37 |
| Nicht prüfbar | 5 |
| Katalogzeilen mit Inhalt «Bestätigt» | 56 |
| … «Teilweise bestätigt» | 2 |
| … «Offen» | 42 |
| Ersetzte Links | 18 |
| Neu aufgenommene Dokumente | 60 |
| Weiterhin offene Quellen (Inhalt nicht bestätigt oder Link nicht OK) | 44 |
| Automatisch gefundene Recherche-Kandidaten | 326 |
| Gemeindeanfragen | 27 |

## 2 Ersetzte Links

| ID | Alt | Neu | Ergebnis Alt | Ergebnis Neu | Grund |
|---|---|---|---|---|---|
| UR-C3-01 | https://rechtsbuch.ur.ch/ | https://rechtsbuch.ur.ch/app/de/texts_of_law/1.1111 | Weiterleitung 200 | Verifiziert / Bestätigt | Startseite der Rechtssammlung durch direkten Erlass ersetzt (Gemeindegesetz, RB 1.1111). |
| UR-C4-01 | https://www.ur.ch/ | https://www.ur.ch/dienstleistungen/8444 | Fehler  | Fehler / Offen | Allgemeine Startseite ur.ch durch themenspezifische Seite zum Beschaffungsrecht ersetzt. |
| UR-C5-01 | https://rechtsbuch.ur.ch/ | https://rechtsbuch.ur.ch/app/de/texts_of_law/2.1201 | Weiterleitung 200 | Verifiziert / Bestätigt | Startseite der Rechtssammlung durch direkten Erlass ersetzt (WAVG, RB 2.1201). |
| BL-C3-01 | https://bl.clex.ch/ | https://bl.clex.ch/app/de/texts_of_law/180 | Weiterleitung 200 | Verifiziert / Bestätigt | Startseite der Gesetzessammlung durch direkten Erlass ersetzt (Gemeindegesetz SGS 180). |
| BL-C5-01 | https://bl.clex.ch/ | https://bl.clex.ch/app/de/texts_of_law/120 | Weiterleitung 200 | Verifiziert / Bestätigt | Startseite der Gesetzessammlung durch direkten Erlass ersetzt (GpR SGS 120). |
| SG-C1-01 | https://www.efv.admin.ch/de/finanzstatistik-daten | https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen/rechnungslegung--rmsg-.html | Verifiziert 200 | Verifiziert / Bestätigt | Herausgeber «Kanton St. Gallen» passte nicht zum EFV-Bundeslink (Dublette zu CH-C1-01); durch kantonale Fundstelle ersetzt. |
| SG-C3-01 | https://www.gesetzessammlung.sg.ch/ | https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/151.2 | Weiterleitung 200 | Verifiziert / Bestätigt | Startseite der Gesetzessammlung durch direkten Erlass ersetzt (Gemeindegesetz sGS 151.2). |
| SG-C5-01 | https://www.gesetzessammlung.sg.ch/ | https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/125.1 | Weiterleitung 200 | Verifiziert / Bestätigt | Startseite der Gesetzessammlung durch direkten Erlass ersetzt (RIG sGS 125.1). |
| SEE-C2-01 | https://www.seelisberg.ch/ | https://www.seelisberg.ch/files/pdf/ERLUTE1.PDF | Verifiziert 200 | Verifiziert / Teilweise bestätigt | Startseite durch direktes Dokument zu Grundeigentum/Baurecht ersetzt. |
| MUE-C1-02 | https://www.muenchenstein.ch/ | https://www.muenchenstein.ch/publikationen/621658 | Fehler  | Fehler / Offen | Startseite durch Publikationsseite der Jahresrechnung 2025 ersetzt. |
| MUE-C2-01 | https://www.muenchenstein.ch/ | https://www.muenchenstein.ch/_docn/1059619/2015.03.16_Ratschlag_Homepage.pdf | Fehler  | Fehler / Offen | Startseite durch direktes Dokument zur Landpolitik ersetzt. |
| MUE-C3-01 | https://www.muenchenstein.ch/ | https://www.muenchenstein.ch/_docn/2430218/20180713_Gemeindeordnung_Stand_01.01.2013_publiziert_sw.pdf | Fehler  | Fehler / Offen | Startseite durch Gemeindeordnung ersetzt. |
| MUE-C4-01 | https://www.muenchenstein.ch/ | https://www.muenchenstein.ch/organisationuorganigramm | Fehler  | Fehler / Offen | Startseite durch Organigrammseite ersetzt. |
| MUE-C5-01 | https://www.muenchenstein.ch/ | https://www.muenchenstein.ch/legislaturziele | Fehler  | Fehler / Offen | Startseite durch Legislaturziele ersetzt. |
| WIL-C2-01 | https://www.stadtwil.ch/political-businesses | https://stadtwil.ch/_doc/4801870 | Verifiziert 200 (HEAD 405) | Fehler / Offen | Geschäftsregister-Startseite durch direktes Dokument zur Bodenpolitik ersetzt. |
| WIL-C3-01 | https://www.stadtwil.ch/political-businesses | https://www.stadtwil.ch/_doc/2079992 | Verifiziert 200 (HEAD 405) | Fehler / Offen | Geschäftsregister-Startseite durch Beteiligungsreglement ersetzt. |
| WIL-C4-01 | https://www.stadtwil.ch/ | https://www.stadtwil.ch/_doc/5663965 | Verifiziert 200 (HEAD 405) | Fehler / Offen | Startseite durch Geschäftsbericht ersetzt. |
| WIL-C5-01 | https://www.stadtwil.ch/political-businesses | https://www.stadtwil.ch/storage/55dcd744fbd978ce5601e42dc48a7b53cdfe1082b7fecb9c647e6dadc8abf9c7 | Verifiziert 200 (HEAD 405) | Verifiziert / Bestätigt | Geschäftsregister-Startseite durch Legislaturplanung ersetzt. |

## 3 Neue Quellen nach Dimension

### C1 (25)

| ID | Ebene | Dokument | Link | Inhaltsprüfung |
|---|---|---|---|---|
| CH-C1-03 | Bund | EFV: FS-Methodenband (Finanzstatistik-Modell, HRM2-Zuordnung) | [Fehler](https://www.efv.admin.ch/dam/efv/en/dokumente/finanzstatistik/methoden/FS-Methodenband.pdf.download.pdf/FS-Methodenband.pdf) | Offen |
| CH-C1-04 | Bund | EFV: Detaillierte Daten FS- und GFS-Modell (Open Government Data) | [Verifiziert](https://opendata.swiss/en/dataset/detaillierte-daten-fs-und-gfs-modell-standardauswertungen) | Bestätigt |
| UR-C1-03 | Uri | Kennzahlen Einwohnergemeinden Uri 2025 (Finanzkontrolle) | [Fehler](https://www.ur.ch/_doc/451636) | Offen |
| UR-C1-04 | Uri | Kennzahlen Einwohnergemeinden Uri 2024 (Finanzkontrolle) | [Fehler](https://www.ur.ch/_doc/420775) | Offen |
| UR-C1-05 | Uri | Reglement über das Rechnungswesen der Einwohnergemeinden (RRE), RB 3.2115 | [Verifiziert](https://rechtsbuch.ur.ch/api/de/versions/776/pdf_file) | Bestätigt |
| UR-C1-06 | Uri | Gesetz über den Finanz- und Lastenausgleich zwischen dem Kanton und den Gemeinden (FiLaG), RB 3.2131 | [Verifiziert](https://rechtsbuch.ur.ch/app/de/texts_of_law/3.2131) | Bestätigt |
| UR-C1-07 | Uri | Finanz- und Lastenausgleich (FiLa) 2025 – Berechnung je Gemeinde | [Fehler](https://www.ur.ch/_docn/426685/Berechnung_FiLa_2025.pdf) | Offen |
| BL-C1-03 | Basel-Landschaft | Kanton BL: Gemeindefinanzen (Rechtsgrundlagen, Finanzausgleich, Rechnungslegung) | [Nicht prüfbar](https://www.baselland.ch/politik-und-behorden/gemeinden/gemeindefinanzen) | Offen |
| BL-C1-04 | Basel-Landschaft | Gemeindefinanzen nach Rechnungsteil, Funktion, Kontenart und Jahr (ab 2014) – OGD Kanton BL | [Verifiziert](https://opendata.swiss/en/dataset/gemeindefinanzen-nach-rechnungsteil-funktion-kontenart-und-jahr-ab-2014/resource/2799cf61-92d5-4e24-8165-1fa67de11eca) | Teilweise bestätigt |
| BL-C1-05 | Basel-Landschaft | Statistisches Amt BL: Webartikel Gemeindefinanzen 2023 (18.9.2024) | [Nicht prüfbar](https://www.baselland.ch/politik-und-behorden/direktionen/finanz-und-kirchendirektion/daten-statistik/abteilung-statistik/publikationen-und-statistiken/finanzen-und-steuern/webartikel-vom-18-09-2024-gemeindefinanzen-2023) | Offen |
| BL-C1-06 | Basel-Landschaft | Finanzausgleichsgesetz (FAG) Basel-Landschaft, SGS 185 | [Verifiziert](https://bl.clex.ch/app/de/texts_of_law/185) | Bestätigt |
| SG-C1-02 | St. Gallen | Finanzausgleichsgesetz St. Gallen, sGS 813.1 | [Verifiziert](https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/813.1) | Bestätigt |
| SG-C1-03 | St. Gallen | Verordnung über den Finanzhaushalt der Gemeinden (FHGV) St. Gallen, sGS 151.53 | [Verifiziert](https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/151.53) | Bestätigt |
| SEE-C1-02 | Seelisberg | Einladung Gemeindeversammlung November 2025: Traktanden und Botschaften (Budget 2026, Finanzplan 2027–2032, Leitbild) | [Verifiziert](https://www.seelisberg.ch/files/pdf/Druckvorlage2_Original_Versammlung-Nov2025_Traktanden-und-Botschaften-gesamt.pdf) | Bestätigt |
| MUE-C1-03 | Münchenstein | Bericht zur Jahresrechnung 2024 der Einwohnergemeinde Münchenstein | [Fehler](https://www.muenchenstein.ch/publikationen/556069) | Offen |
| MUE-C1-04 | Münchenstein | Budget 2025 der Einwohnergemeinde Münchenstein | [Fehler](https://www.muenchenstein.ch/publikationen/523381) | Offen |
| MUE-C1-05 | Münchenstein | Gemeindeversammlung 8.12.2025: Budgetbericht 2026 und Bericht zum Aufgaben- und Finanzplan 2026–2030 | [Fehler](https://www.muenchenstein.ch/sitzung/5729137) | Offen |
| MUE-C1-06 | Münchenstein | Aufgaben- & Finanzplan der Einwohnergemeinde Münchenstein 2023–2027 | [Fehler](https://www.muenchenstein.ch/_docn/4130681/Bericht_Aufgaben__Finanzplan_2023-2027_publiziert.pdf) | Offen |
| WIL-C1-03 | Wil | Jahresrechnung 2023 der Stadt Wil | [Fehler](https://www.stadtwil.ch/_docn/5050942/Jahresrechnung_2023.pdf) | Offen |
| WIL-C1-04 | Wil | Rechnung 2024 Stadt Wil – Kurzfassung mit Bericht und Antrag (Stadtrat 4.3.2025) | [Fehler](https://www.stadtwil.ch/_doc/5592973) | Offen |
| WIL-C1-05 | Wil | Rechnung 2025 Stadt Wil – Finanzbericht, Erfolgsrechnung, Bilanz, Anhang | [Verifiziert](https://www.stadtwil.ch/storage/08902ff399818ccc0d53949607b2d0f6f8bf702c334e295d493c2fd842ba4079) | Bestätigt |
| WIL-C1-06 | Wil | Finanzplan 2026–2030 der Stadt Wil (Stadtrat 23.9.2025) | [Verifiziert](https://www.stadtwil.ch/storage/875d422378d72386aae96efa76356fbfa05e9a0e1e03f208fbbe599dea21021c) | Bestätigt |
| WIL-C1-07 | Wil | Übersicht über die Investitionen 2025–2035 Stadt Wil | [Verifiziert](https://www.stadtwil.ch/storage/68981c34e629883df15ea09baa331530387503f2a8c37c1259512877afe4840f) | Bestätigt |
| WIL-C1-08 | Wil | Budget 2026 Stadt Wil – Bericht und Antrag des Stadtrats | [Verifiziert](https://www.stadtwil.ch/storage/819a3bb87d4ead8a5dc31b37f1d59911eea50dc8005458ebf9ad112a61ce2694) | Bestätigt |
| WIL-C1-09 | Wil | Jahresrechnung 2025 Technische Betriebe Wil (TBW) – Bericht und Antrag | [Verifiziert](https://www.stadtwil.ch/storage/9bf65acd52bfa75c91cc42760759e0ffc3a76d501e7d174c010444c290801cc2) | Bestätigt |

### C2 (13)

| ID | Ebene | Dokument | Link | Inhaltsprüfung |
|---|---|---|---|---|
| CH-C2-02 | Bund | Bundesgesetz über die Raumplanung (RPG), SR 700 | [Verifiziert](https://www.fedlex.admin.ch/eli/cc/1979/1573_1573_1573/de) | Bestätigt |
| UR-C2-02 | Uri | Planungs- und Baugesetz (PBG) des Kantons Uri, RB 40.1111 | [Verifiziert](https://rechtsbuch.ur.ch/app/de/texts_of_law/40.1111) | Bestätigt |
| UR-C2-03 | Uri | Kanton Uri: Baulanddatenbank (unbebaute Bauzonen, Raum+) | [Fehler](https://www.ur.ch/dienstleistungen/4297) | Offen |
| BL-C2-02 | Basel-Landschaft | Raumplanungs- und Baugesetz (RBG) Basel-Landschaft, SGS 400 | [Verifiziert](https://bl.clex.ch/app/de/texts_of_law/400) | Bestätigt |
| SG-C2-02 | St. Gallen | WILWEST: Grundstücksgeschäft Kanton St. Gallen (Verkauf an Kanton Thurgau) – Kantonsratsvorlage | [Verifiziert](https://www.ratsinfo.sg.ch//media/documents/published/signed/8b158b37-2fff-4d5d-b018-ef035f08732e.pdf) | Bestätigt |
| SG-C2-03 | St. Gallen | Planungs- und Baugesetz (PBG) St. Gallen, sGS 731.1 | [Verifiziert](https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/731.1) | Bestätigt |
| SEE-C2-02 | Seelisberg | Bau- und Zonenordnung Seelisberg (BZO) | [Verifiziert](https://www.seelisberg.ch/files/pdf/Bau-und-Zonenordnung-Seelisberg.pdf) | Bestätigt |
| SEE-C2-03 | Seelisberg | Siedlungsleitbild Seelisberg (Genehmigungsexemplar, 5.10.2022) | [Verifiziert](https://www.seelisberg.ch/files/pdf/8_20221005_Bericht_Siedlungsleitbild_Genehmigungsexemplar.pdf) | Bestätigt |
| SEE-C2-04 | Seelisberg | Seelisberg: Teilrevision Nutzungsplanung – Erläuterungsbericht (26.5.2023) | [Verifiziert](https://www.seelisberg.ch/files/pdf/20230526_Erl%C3%A4uterungsbericht.pdf) | Bestätigt |
| MUE-C2-02 | Münchenstein | Zonenreglement Siedlung Münchenstein | [Fehler](https://www.muenchenstein.ch/_docn/1199675/Zonenreglement_Siedlung.pdf) | Offen |
| MUE-C2-03 | Münchenstein | Ratschlag Gemeindeversammlung 12.3.2018 (Baurechtszinsen, Liegenschaftsverkäufe) | [Fehler](https://www.muenchenstein.ch/_docn/1591897/2018.03.12_Ratschlag_GzD.pdf) | Offen |
| WIL-C2-02 | Wil | PO 101 «Für eine neue Bodenpolitik» – Stellungnahme des Stadtrats (Grundsätze Liegenschaftenkonzept) | [Fehler](https://www.stadtwil.ch/_docn/1058128/PO_101_Fuer_eine_neue_Bodenpolitik_Stellungnahme.pdf) | Offen |
| WIL-C2-03 | Wil | Stadt Wil: aktive Bodenpolitik / Boden- und Immobilienstrategie | [Verifiziert](https://www.stadtwil.ch/storage/1e396670eed23bbd41611d92ceaa476797bc97e16fde09c29197453c3b3bc320) | Bestätigt |

### C3 (7)

| ID | Ebene | Dokument | Link | Inhaltsprüfung |
|---|---|---|---|---|
| UR-C3-02 | Uri | Verfassung des Kantons Uri, RB 1.1101 | [Verifiziert](https://rechtsbuch.ur.ch/app/de/texts_of_law/1.1101) | Bestätigt |
| BL-C3-02 | Basel-Landschaft | Medienmitteilung Kanton BL: Birsstadt erhält den Wakkerpreis (Verein Birsstadt, Raumkonzept Birsstadt 2035) | [Nicht prüfbar](https://www.baselland.ch/politik-und-behorden/direktionen/bau-und-umweltschutzdirektion/medienmitteilungen/ausgezeichnete-agglomeration-birsstadt-erhaelt-den-wakkerpreis) | Offen |
| MUE-C3-02 | Münchenstein | Ratschlag Gemeindeversammlung 15.6.2026 (u. a. Leistungsvereinbarung Spitex Birseck, Jahresrechnung 2025) | [Fehler](https://www.muenchenstein.ch/_docn/6998503/Ratschlag_Gemeindeversammlung_Montag,_15._Juni_2026.pdf) | Offen |
| WIL-C3-02 | Wil | Gemeindeordnung der Stadt Wil vom 28.2.2016 (sRS 111.1) | [Fehler](https://stadtwil.ch/_doc/1267121) | Offen |
| WIL-C3-03 | Wil | Reglement Technische Betriebe Wil (TBW) – Erlass 2020 | [Fehler](https://www.stadtwil.ch/_docn/2747618/012_BA_Erlass_neuesTBW-Reglement.pdf) | Offen |
| WIL-C3-04 | Wil | Prüfbericht des Bundes zum Agglomerationsprogramm Wil, 4. Generation (22.2.2023) | [Verifiziert](https://www.are.admin.ch/dam/de/sd-web/1LGAXN34JMxU/Pr%C3%BCfbericht%20Wil4G.pdf) | Bestätigt |
| WIL-C3-05 | Wil | Agglomerationsprogramm Wil 5. Generation – Flyer | [Verifiziert](https://www.sg.ch/content/dam/sgch/bauen/raumentwicklung/agglomerationsprogramme/Wil%20Flyer%205G.pdf) | Bestätigt |

### C4 (7)

| ID | Ebene | Dokument | Link | Inhaltsprüfung |
|---|---|---|---|---|
| CH-C4-02 | Bund | BFS: Regionalporträts – Kennzahlen aller Gemeinden (Datensatz) | [Verifiziert](https://ckan.opendata.swiss/dataset/regionalportrats-2021-kennzahlen-aller-gemeinden) | Bestätigt |
| UR-C4-02 | Uri | Interkantonale Vereinbarung über das öffentliche Beschaffungswesen (IVöB 2019), RB 3.3111 | [Verifiziert](https://rechtsbuch.ur.ch/app/de/texts_of_law/3.3111) | Bestätigt |
| BL-C4-02 | Basel-Landschaft | Verordnung zum Einführungsgesetz zur IVöB (Vo EG IVöB) Basel-Landschaft, SGS 420.11 | [Verifiziert](https://bl.clex.ch/app/de/texts_of_law/420.11) | Bestätigt |
| SG-C4-02 | St. Gallen | Einführungsgesetz zur IVöB St. Gallen, sGS 841.1 | [Verifiziert](https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/841.1) | Bestätigt |
| SEE-C4-02 | Seelisberg | Gemeinde Seelisberg: Personal der Gemeindeverwaltung | [Verifiziert](https://www.seelisberg.ch/personal) | Bestätigt |
| MUE-C4-02 | Münchenstein | Personalreglement der Einwohnergemeinde Münchenstein (Genehmigungsfassung 23.6.2022) | [Fehler](https://www.muenchenstein.ch/_docn/3794018/Bereinigtes_Personalreglement_Genehmigungsfassung_per_23._Juni_2022.pdf) | Offen |
| MUE-C4-03 | Münchenstein | Verwaltungs- und Organisationsreglement der Einwohnergemeinde Münchenstein | [Fehler](https://www.muenchenstein.ch/reglemente/7208) | Offen |

### C5 (8)

| ID | Ebene | Dokument | Link | Inhaltsprüfung |
|---|---|---|---|---|
| SEE-C5-02 | Seelisberg | Gemeinde Seelisberg: Neues Leitbild der Gemeinde (2025) | [Verifiziert](https://www.seelisberg.ch/news/neues-leitbild-der-gemeinde-seelisberg) | Bestätigt |
| SEE-C5-03 | Seelisberg | Beschlussprotokoll Gemeindeversammlung Seelisberg vom 24.11.2023 | [Verifiziert](https://www.seelisberg.ch/files/pdf/Beschlussprotokoll_GV_24.11.2023.pdf) | Bestätigt |
| MUE-C5-02 | Münchenstein | Protokoll Gemeindeversammlung Münchenstein 13.6.2024 | [Fehler](https://www.muenchenstein.ch/_docn/5478214/Protokoll_Gemeindeversammlung_13._Juni_2024_definitiv.pdf) | Offen |
| MUE-C5-03 | Münchenstein | Beschlüsse der Gemeindeversammlung vom 8.12.2025 (Budget 2026, AFP 2026–2030) | [Fehler](https://www.muenchenstein.ch/politikinformationen/2666993) | Offen |
| MUE-C5-04 | Münchenstein | Quartierplanung Spenglerpark – Mitwirkungsbericht (2019) | [Fehler](https://www.muenchenstein.ch/_docn/2359339/43037_Ber05_Mitwirkungsbericht_VerabschiedungGR_Unterschrieben_20190924_korr.pdf) | Offen |
| MUE-C5-05 | Münchenstein | Gemeindekommission Münchenstein (§ 88 GemG) | [Fehler](https://www.muenchenstein.ch/behoerden/2838) | Offen |
| WIL-C5-02 | Wil | Richtplan Siedlung und Grün-/Freiraum – Planungsbericht inkl. Auszug Stadtentwicklungskonzept (31.3.2026) | [Verifiziert](https://www.stadtwil.ch/storage/533b0557b4e4988a6a4f9af13c0b789fec39837eef83d1e66cd1d3814dbe0acb) | Offen |
| WIL-C5-03 | Wil | Ortsplanungsrevision Wil – Mitwirkung 2025 | [Verifiziert](https://www.stadtwil.ch/storage/5d895f1e33cc1b2c352d7bdeb9d93dd5b2333fbff6a1793cd419f387dd4e1e28) | Offen |

## 4 Abdeckung je Gemeinde und Dimension

Zellen: bestätigte Dokumente / Zeilen gesamt (nur Gemeindeebene).

| Gemeinde | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Seelisberg | 2 / 2 | 3 / 4 | 1 / 1 | 2 / 2 | 3 / 3 |
| Münchenstein | 0 / 6 | 0 / 3 | 0 / 2 | 0 / 3 | 0 / 5 |
| Wil | 7 / 9 | 1 / 3 | 2 / 5 | 0 / 1 | 1 / 3 |

## 5 Offene und problematische Quellen

| ID | Dokument | Linkstatus | Inhalt | Nachweis / Fehler |
|---|---|---|---|---|
| CH-C1-03 | EFV: FS-Methodenband (Finanzstatistik-Modell, HRM2-Zuordnung) | Fehler 502 | Offen | HTTP 502 |
| UR-C1-01 | Gemeindefinanzstatistik Uri | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.ur.ch', port=443): Max retries exceeded with url: /publikationen/6680 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.ur.ch', port=443) at 0x7fcb24d468a0>, 'Co |
| UR-C1-02 | Steuerstatistiken Kanton Uri | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.ur.ch', port=443): Max retries exceeded with url: /finanzen/1588 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.ur.ch', port=443) at 0x7fcb24d451f0>, 'Connect |
| UR-C1-03 | Kennzahlen Einwohnergemeinden Uri 2025 (Finanzkontrolle) | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.ur.ch', port=443): Max retries exceeded with url: /_doc/451636 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.ur.ch', port=443) at 0x7fcb246a4770>, 'Connectio |
| UR-C1-04 | Kennzahlen Einwohnergemeinden Uri 2024 (Finanzkontrolle) | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.ur.ch', port=443): Max retries exceeded with url: /_doc/420775 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.ur.ch', port=443) at 0x7fcb246a3320>, 'Connectio |
| UR-C1-07 | Finanz- und Lastenausgleich (FiLa) 2025 – Berechnung je Gemeinde | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.ur.ch', port=443): Max retries exceeded with url: /_docn/426685/Berechnung_FiLa_2025.pdf (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.ur.ch', port=443) at 0 |
| UR-C2-03 | Kanton Uri: Baulanddatenbank (unbebaute Bauzonen, Raum+) | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.ur.ch', port=443): Max retries exceeded with url: /dienstleistungen/4297 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.ur.ch', port=443) at 0x7fcb246a33b0>,  |
| UR-C4-01 | Kanton Uri: Submissionsrecht (IVöB 2019, in Kraft seit 1.6.2023) | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.ur.ch', port=443): Max retries exceeded with url: /dienstleistungen/8444 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.ur.ch', port=443) at 0x7fcb24d47bf0>,  |
| BL-C1-02 | Gemeindefinanzen BL: Rechnungslegung und Excel-Vorlagen | Nicht prüfbar 403 | Offen | Zugriff verweigert/gedrosselt (HTTP 403); keine Umgehung versucht |
| BL-C1-03 | Kanton BL: Gemeindefinanzen (Rechtsgrundlagen, Finanzausgleich, Rechnungslegung) | Nicht prüfbar 403 | Offen | Zugriff verweigert/gedrosselt (HTTP 403); keine Umgehung versucht |
| BL-C1-04 | Gemeindefinanzen nach Rechnungsteil, Funktion, Kontenart und Jahr (ab 2014) – OGD Kanton BL | Verifiziert 200 | Teilweise bestätigt | Schlüsselwörter 0/1 gefunden; fehlend: Gemeindefinanzen; Ort/Zuständigkeit: BL |
| BL-C1-05 | Statistisches Amt BL: Webartikel Gemeindefinanzen 2023 (18.9.2024) | Nicht prüfbar 403 | Offen | Zugriff verweigert/gedrosselt (HTTP 403); keine Umgehung versucht |
| BL-C3-02 | Medienmitteilung Kanton BL: Birsstadt erhält den Wakkerpreis (Verein Birsstadt, Raumkonzept Birsstadt 2035) | Nicht prüfbar 403 | Offen | Zugriff verweigert/gedrosselt (HTTP 403); keine Umgehung versucht |
| BL-C4-01 | Kanton Basel-Landschaft: Gemeindefachstellen | Nicht prüfbar 403 | Offen | Zugriff verweigert/gedrosselt (HTTP 403); keine Umgehung versucht |
| SEE-C2-01 | Teilrevision Nutzungsplanung und Quartiergestaltungsplan «Sonnenberg» – Erläuterungsbericht (Erwerb Parzelle 775, Baurecht) | Verifiziert 200 | Teilweise bestätigt | Schlüsselwörter 1/2 gefunden (Sonnenberg); fehlend: Baurecht; Ort/Zuständigkeit: Seelisberg |
| MUE-C1-01 | Aufgaben- und Finanzplan 2025–2029 Münchenstein | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /publikationen/523378 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) |
| MUE-C1-02 | Bericht zur Jahresrechnung 2025 der Einwohnergemeinde Münchenstein | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /publikationen/621658 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) |
| MUE-C1-03 | Bericht zur Jahresrechnung 2024 der Einwohnergemeinde Münchenstein | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /publikationen/556069 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) |
| MUE-C1-04 | Budget 2025 der Einwohnergemeinde Münchenstein | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /publikationen/523381 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) |
| MUE-C1-05 | Gemeindeversammlung 8.12.2025: Budgetbericht 2026 und Bericht zum Aufgaben- und Finanzplan 2026–2030 | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /sitzung/5729137 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0 |
| MUE-C1-06 | Aufgaben- & Finanzplan der Einwohnergemeinde Münchenstein 2023–2027 | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /_docn/4130681/Bericht_Aufgaben__Finanzplan_2023-2027_publiziert.pdf (Caused by ConnectTimeoutError(<HTTPSCo |
| MUE-C2-01 | Ratschlag Gemeindeversammlung 16.3.2015 (Landverkauf Parzelle 799; Grundsätze aktive Landpolitik / Baurecht) | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /_docn/1059619/2015.03.16_Ratschlag_Homepage.pdf (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.m |
| MUE-C2-02 | Zonenreglement Siedlung Münchenstein | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /_docn/1199675/Zonenreglement_Siedlung.pdf (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenche |
| MUE-C2-03 | Ratschlag Gemeindeversammlung 12.3.2018 (Baurechtszinsen, Liegenschaftsverkäufe) | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /_docn/1591897/2018.03.12_Ratschlag_GzD.pdf (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muench |
| MUE-C3-01 | Gemeindeordnung der Einwohnergemeinde Münchenstein (Stand 1.1.2013) | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /_docn/2430218/20180713_Gemeindeordnung_Stand_01.01.2013_publiziert_sw.pdf (Caused by ConnectTimeoutError(<H |
| MUE-C3-02 | Ratschlag Gemeindeversammlung 15.6.2026 (u. a. Leistungsvereinbarung Spitex Birseck, Jahresrechnung 2025) | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /_docn/6998503/Ratschlag_Gemeindeversammlung_Montag,_15._Juni_2026.pdf (Caused by ConnectTimeoutError(<HTTPS |
| MUE-C4-01 | Gemeinde Münchenstein: Organisation und Organigramm der Verwaltung | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /organisationuorganigramm (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port= |
| MUE-C4-02 | Personalreglement der Einwohnergemeinde Münchenstein (Genehmigungsfassung 23.6.2022) | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /_docn/3794018/Bereinigtes_Personalreglement_Genehmigungsfassung_per_23._Juni_2022.pdf (Caused by ConnectTim |
| MUE-C4-03 | Verwaltungs- und Organisationsreglement der Einwohnergemeinde Münchenstein | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /reglemente/7208 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0 |
| MUE-C5-01 | Legislaturziele 2024–2028 des Gemeinderats Münchenstein | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /legislaturziele (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0 |
| MUE-C5-02 | Protokoll Gemeindeversammlung Münchenstein 13.6.2024 | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /_docn/5478214/Protokoll_Gemeindeversammlung_13._Juni_2024_definitiv.pdf (Caused by ConnectTimeoutError(<HTT |
| MUE-C5-03 | Beschlüsse der Gemeindeversammlung vom 8.12.2025 (Budget 2026, AFP 2026–2030) | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /politikinformationen/2666993 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', p |
| MUE-C5-04 | Quartierplanung Spenglerpark – Mitwirkungsbericht (2019) | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /_docn/2359339/43037_Ber05_Mitwirkungsbericht_VerabschiedungGR_Unterschrieben_20190924_korr.pdf (Caused by C |
| MUE-C5-05 | Gemeindekommission Münchenstein (§ 88 GemG) | Fehler  | Offen | GET: ConnectTimeout: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /behoerden/2838 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0x |
| WIL-C1-03 | Jahresrechnung 2023 der Stadt Wil | Fehler 404 | Offen | HTTP 404 |
| WIL-C1-04 | Rechnung 2024 Stadt Wil – Kurzfassung mit Bericht und Antrag (Stadtrat 4.3.2025) | Fehler 404 | Offen | HTTP 404 |
| WIL-C2-01 | Nachtrag IV zur Gemeindeordnung: Finanzbefugnisse für Liegenschaftsgeschäfte im Finanzvermögen (Bericht Stadtrat 24.10.2023) | Fehler 404 | Offen | HTTP 404 |
| WIL-C2-02 | PO 101 «Für eine neue Bodenpolitik» – Stellungnahme des Stadtrats (Grundsätze Liegenschaftenkonzept) | Fehler 404 | Offen | HTTP 404 |
| WIL-C3-01 | Reglement über die Steuerung und Beaufsichtigung von Organisationen mit städtischer Beteiligung (Beteiligungsreglement) | Fehler 404 | Offen | HTTP 404 |
| WIL-C3-02 | Gemeindeordnung der Stadt Wil vom 28.2.2016 (sRS 111.1) | Fehler 404 | Offen | HTTP 404 |
| WIL-C3-03 | Reglement Technische Betriebe Wil (TBW) – Erlass 2020 | Fehler 404 | Offen | HTTP 404 |
| WIL-C4-01 | Geschäftsbericht der Stadt Wil 2024 | Fehler 404 | Offen | HTTP 404 |
| WIL-C5-02 | Richtplan Siedlung und Grün-/Freiraum – Planungsbericht inkl. Auszug Stadtentwicklungskonzept (31.3.2026) | Verifiziert 200 | Offen | Kein auswertbarer Text (z. B. JavaScript-Seite oder Scan) |
| WIL-C5-03 | Ortsplanungsrevision Wil – Mitwirkung 2025 | Verifiziert 200 | Offen | Kein auswertbarer Text (z. B. JavaScript-Seite oder Scan) |

## 6 Datenlücken und Gemeindeanfragen je Gemeinde

### Seelisberg

| ID | Dim. | Priorität | Quellenstatus | Lieferung |
|---|---|---|---|---|
| A-SEE-01 | C1 | Hoch | Nur über Gemeindeanfrage erhältlich | Jahresrechnungen der letzten 5 Jahre inkl. Bilanz, Investitionsrechnung und Finanzkennzahlen |
| A-SEE-02 | C1 | Hoch | Nur über Gemeindeanfrage erhältlich | Mehrjähriger Finanz- und Investitionsplan; Eventualverpflichtungen |
| A-SEE-03 | C2 | Hoch | Nicht öffentlich auffindbar | Kommunales Grundstücks- und Liegenschaftsverzeichnis mit Parzellen-IDs |
| A-SEE-04 | C2 | Hoch | Nur über Gemeindeanfrage erhältlich | Baurechts-, Dienstbarkeits- und relevante Eigentumsverträge |
| A-SEE-09 | C2, C3 | Hoch | Nur über Gemeindeanfrage erhältlich | Vertragsstand Projekt Sonnenberg (Planungs- und Infrastrukturvertrag, Baurechtsvertrag Parzelle 775) |
| A-SEE-05 | C3 | Hoch | Nicht öffentlich auffindbar | Organigramm Zuständigkeiten; Kooperationen und Leistungsvereinbarungen |
| A-SEE-06 | C4 | Hoch | Nur über Gemeindeanfrage erhältlich | Stellenplan, Projektportfolio, externe Mandate, Beschaffungsprozesse |
| A-SEE-07 | C5 | Mittel | Öffentlich verfügbar und verifiziert | Politische Leitbilder, relevante Beschlüsse und Mitwirkungsberichte |
| A-SEE-08 | C5 | Mittel | Nur über Gemeindeanfrage erhältlich | Akteursübersicht mit bekannten Positionen und Einfluss |

### Münchenstein

| ID | Dim. | Priorität | Quellenstatus | Lieferung |
|---|---|---|---|---|
| A-MUE-01 | C1 | Hoch | Nicht zugänglich / nicht prüfbar | Jahresrechnungen der letzten 5 Jahre inkl. Bilanz, Investitionsrechnung und Finanzkennzahlen |
| A-MUE-02 | C1 | Hoch | Nicht zugänglich / nicht prüfbar | Mehrjähriger Finanz- und Investitionsplan; Eventualverpflichtungen |
| A-MUE-03 | C2 | Hoch | Nicht öffentlich auffindbar | Kommunales Grundstücks- und Liegenschaftsverzeichnis mit Parzellen-IDs |
| A-MUE-04 | C2 | Hoch | Nur über Gemeindeanfrage erhältlich | Baurechts-, Dienstbarkeits- und relevante Eigentumsverträge |
| A-MUE-09 | C2 | Mittel | Nicht öffentlich auffindbar | Liegenschafts- bzw. Bodenstrategie (falls vorhanden) und Grundsätze zu Verkauf vs. Baurecht |
| A-MUE-05 | C3 | Hoch | Nicht öffentlich auffindbar | Organigramm Zuständigkeiten; Kooperationen und Leistungsvereinbarungen |
| A-MUE-06 | C4 | Hoch | Nur über Gemeindeanfrage erhältlich | Stellenplan, Projektportfolio, externe Mandate, Beschaffungsprozesse |
| A-MUE-07 | C5 | Mittel | Nicht zugänglich / nicht prüfbar | Politische Leitbilder, relevante Beschlüsse und Mitwirkungsberichte |
| A-MUE-08 | C5 | Mittel | Nicht öffentlich auffindbar | Akteursübersicht mit bekannten Positionen und Einfluss |

### Wil

| ID | Dim. | Priorität | Quellenstatus | Lieferung |
|---|---|---|---|---|
| A-WIL-01 | C1 | Hoch | Öffentlich verfügbar und verifiziert | Jahresrechnungen der letzten 5 Jahre inkl. Bilanz, Investitionsrechnung und Finanzkennzahlen |
| A-WIL-02 | C1 | Hoch | Öffentlich verfügbar und verifiziert | Mehrjähriger Finanz- und Investitionsplan; Eventualverpflichtungen |
| A-WIL-03 | C2 | Hoch | Nicht öffentlich auffindbar | Kommunales Grundstücks- und Liegenschaftsverzeichnis mit Parzellen-IDs |
| A-WIL-04 | C2 | Hoch | Nur über Gemeindeanfrage erhältlich | Baurechts-, Dienstbarkeits- und relevante Eigentumsverträge |
| A-WIL-09 | C2 | Mittel | Öffentlich verfügbar und verifiziert | Aktuelle Boden- und Immobilienstrategie; Stand Nachtrag IV Gemeindeordnung (Finanzbefugnisse Liegenschaften) |
| A-WIL-05 | C3 | Hoch | Nicht zugänglich / nicht prüfbar | Organigramm Zuständigkeiten; Kooperationen und Leistungsvereinbarungen |
| A-WIL-06 | C4 | Hoch | Nicht öffentlich auffindbar | Stellenplan, Projektportfolio, externe Mandate, Beschaffungsprozesse |
| A-WIL-07 | C5 | Mittel | Öffentlich verfügbar und verifiziert | Politische Leitbilder, relevante Beschlüsse und Mitwirkungsberichte |
| A-WIL-08 | C5 | Mittel | Nur über Gemeindeanfrage erhältlich | Akteursübersicht mit bekannten Positionen und Einfluss |

## 7 Fachliche Unsicherheiten

- Inhaltsprüfung ist ein automatischer Schlüsselwort-Abgleich (Titel/erste Seiten). Sie belegt die Dokumentidentität, nicht die fachliche Eignung oder Vollständigkeit.
- Hash-Links der Stadt Wil (/storage/…) wurden über Suchmaschinen-Zusammenfassungen zugeordnet; massgeblich ist allein die Inhaltsprüfung des Runners.
- Kantonale Rechtssammlungen (LexWork: rechtsbuch.ur.ch, bl.clex.ch, gesetzessammlung.sg.ch) und Fedlex sind JavaScript-Anwendungen; die Identität wird über deren Daten-Schnittstellen geprüft. Fehlt diese, bleibt die Inhaltsprüfung «Offen».
- Planerische Flächenverfügbarkeit (Zonen, Bauland-Datenbanken) ist kein Nachweis kommunalen Grundeigentums. C2 bleibt ohne Liegenschaftsverzeichnisse der Gemeinden unbelegt.
- Organigramme und Reglemente belegen Strukturen, nicht Verwaltungskompetenz oder Kapazität (C4).
- Leitbilder, Mitwirkungsverfahren und Beschlüsse belegen keine politische Akzeptanz (C5); dazu sind Abstimmungsresultate und qualitative Befunde nötig.
- Seelisberg: Projekt Sonnenberg wird in Quellen als Halter-AG-Projekt genannt – mögliche Interessenbindung bei der Auswertung offenlegen.
- Tragfähigkeit wurde bewusst nirgends eingestuft; die Schwellen in der Bewertungslogik sind noch nicht validiert.

## 8 Empfehlungen für weitere Recherchen

- Gemeindeanfragen mit Priorität «Hoch» zuerst versenden (C1-Zeitreihen, C2-Liegenschaftsverzeichnisse, C4-Stellenpläne).
- Blatt «Recherche-Kandidaten» sichten: direkte PDF-Links hinter Publikations- und Sitzungsseiten übernehmen (v. a. Münchenstein /publikationen/, Seelisberg Beschlussprotokolle 2025).
- C1: Kennzahlen (Selbstfinanzierungsgrad, Nettoschuld je Einwohner, Investitionsanteil) aus den bestätigten Jahresrechnungen extrahieren und Peer-Gruppe Kanton × Grössenklasse bilden (BFS-Regionalporträts).
- Kantonale Finanzstatistik St. Gallen (Finanzstatistik der politischen Gemeinden) als direkten Download ermitteln.
- Gemeindeordnung Seelisberg (2009) und Regio-Wil-Statuten bei den Gemeinden anfordern, da online nicht auffindbar.
- Optional Secret BRAVE_SEARCH_API_KEY hinterlegen, um die automatische Recherche um eine Such-API zu erweitern.

## 9 Protokoll der automatischen Recherche

```
Prüfe 105 URLs mit 6 Threads …
  [Verifiziert] 200 Bestätigt https://www.efv.admin.ch/de/finanzstatistik-daten
  [Verifiziert] 200 Bestätigt https://www.efv.admin.ch/de/was-ist-die-finanzstatistik
  [Verifiziert] 200 Bestätigt https://www.fedlex.admin.ch/eli/cc/1999/404/de
  [Verifiziert] 200 Bestätigt https://www.fedlex.admin.ch/eli/cc/2020/126/de
  [Verifiziert] 200 Bestätigt https://geo.ur.ch/
  [Verifiziert] 200 Bestätigt https://www.fedlex.admin.ch/eli/cc/24/233_245_233/de
  [Verifiziert] 200 Bestätigt https://rechtsbuch.ur.ch/app/de/texts_of_law/1.1111
  [Weiterleitung] 200 Offen https://rechtsbuch.ur.ch/
  [Verifiziert] 200 Bestätigt https://statistik.bl.ch/web_portal/18_5
  [Nicht prüfbar] 403 Offen https://www.baselland.ch/politik-und-behorden/gemeinden/gemeindefinanzen/rechnungslegung-einwohnergemeinden/excel-vorlagen
  [Verifiziert] 200 Bestätigt https://rechtsbuch.ur.ch/app/de/texts_of_law/2.1201
  [Verifiziert] 200 Bestätigt https://geoview.bl.ch/
  [Verifiziert] 200 Bestätigt https://bl.clex.ch/app/de/texts_of_law/180
  [Nicht prüfbar] 403 Offen https://www.baselland.ch/politik-und-behorden/gemeinden
  [Weiterleitung] 200 Offen https://bl.clex.ch/
  [Verifiziert] 200 Bestätigt https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen/rechnungslegung--rmsg-.html
  [Verifiziert] 200 Bestätigt https://bl.clex.ch/app/de/texts_of_law/120
  [Verifiziert] 200 Bestätigt https://www.geoportal.ch/
  [Weiterleitung] 200 Offen https://www.gesetzessammlung.sg.ch/
  [Verifiziert] 200 Bestätigt https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/151.2
  [Verifiziert] 200 Bestätigt https://www.sg.ch/
  [Verifiziert] 200 Bestätigt https://www.seelisberg.ch/politik/gemeindeversammlung
  [Verifiziert] 200 Bestätigt https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/125.1
  [Verifiziert] 200 Teilweise bestätigt https://www.seelisberg.ch/files/pdf/ERLUTE1.PDF
  [Verifiziert] 200 Teilweise bestätigt https://www.seelisberg.ch/
  [Verifiziert] 200 Bestätigt https://www.seelisberg.ch/politik/beh%C3%B6rden-kommissionen
  [Fehler]  Offen https://www.ur.ch/publikationen/6680
  [Fehler]  Offen https://www.ur.ch/finanzen/1588
  [Fehler]  Offen https://www.ur.ch/dienstleistungen/8444
  [Fehler]  Offen https://www.ur.ch/
  [Fehler]  Offen https://www.muenchenstein.ch/publikationen/523378
  [Fehler]  Offen https://www.muenchenstein.ch/publikationen/621658
  [Verifiziert] 200 (HEAD 405) Bestätigt https://www.stadtwil.ch/topics/stadt-politik-und-recht/finanzen
  [Verifiziert] 200 (HEAD 405) Bestätigt https://www.stadtwil.ch/political-business/28da2d58a16b4b85b0504eeaa7e396dc
  [Fehler] 404 Offen https://stadtwil.ch/_doc/4801870
  [Verifiziert] 200 (HEAD 405) Teilweise bestätigt https://www.stadtwil.ch/political-businesses
  [Fehler] 404 Offen https://www.stadtwil.ch/_doc/2079992
  [Fehler] 404 Offen https://www.stadtwil.ch/_doc/5663965
  [Verifiziert] 200 (HEAD 405) Teilweise bestätigt https://www.stadtwil.ch/
  [Verifiziert] 200 Bestätigt https://www.stadtwil.ch/storage/55dcd744fbd978ce5601e42dc48a7b53cdfe1082b7fecb9c647e6dadc8abf9c7
  [Fehler] 502 Offen https://www.efv.admin.ch/dam/efv/en/dokumente/finanzstatistik/methoden/FS-Methodenband.pdf.download.pdf/FS-Methodenband.pdf
  [Verifiziert] 200 Bestätigt https://opendata.swiss/en/dataset/detaillierte-daten-fs-und-gfs-modell-standardauswertungen
  [Verifiziert] 200 Bestätigt https://www.fedlex.admin.ch/eli/cc/1979/1573_1573_1573/de
  [Verifiziert] 200 Bestätigt https://ckan.opendata.swiss/dataset/regionalportrats-2021-kennzahlen-aller-gemeinden
  [Fehler]  Offen https://www.muenchenstein.ch/
  [Fehler]  Offen https://www.muenchenstein.ch/_docn/1059619/2015.03.16_Ratschlag_Homepage.pdf
  [Verifiziert] 200 Bestätigt https://rechtsbuch.ur.ch/api/de/versions/776/pdf_file
  [Fehler]  Offen https://www.muenchenstein.ch/_docn/2430218/20180713_Gemeindeordnung_Stand_01.01.2013_publiziert_sw.pdf
  [Fehler]  Offen https://www.muenchenstein.ch/organisationuorganigramm
  [Verifiziert] 200 Bestätigt https://rechtsbuch.ur.ch/app/de/texts_of_law/3.2131
  [Verifiziert] 200 Bestätigt https://rechtsbuch.ur.ch/app/de/texts_of_law/40.1111
  [Verifiziert] 200 Bestätigt https://rechtsbuch.ur.ch/app/de/texts_of_law/1.1101
  [Verifiziert] 200 Bestätigt https://rechtsbuch.ur.ch/app/de/texts_of_law/3.3111
  [Nicht prüfbar] 403 Offen https://www.baselland.ch/politik-und-behorden/gemeinden/gemeindefinanzen
  [Verifiziert] 200 Teilweise bestätigt https://opendata.swiss/en/dataset/gemeindefinanzen-nach-rechnungsteil-funktion-kontenart-und-jahr-ab-2014/resource/2799cf61-92d5-4e24-8165-1fa67de11eca
  [Nicht prüfbar] 403 Offen https://www.baselland.ch/politik-und-behorden/direktionen/finanz-und-kirchendirektion/daten-statistik/abteilung-statistik/publikationen-und-statistiken/finanzen-und-steuern/webartikel-vom-18-09-2024-gemeindefinanzen-2023
  [Verifiziert] 200 Bestätigt https://bl.clex.ch/app/de/texts_of_law/185
  [Verifiziert] 200 Bestätigt https://bl.clex.ch/app/de/texts_of_law/400
  [Verifiziert] 200 Bestätigt https://bl.clex.ch/app/de/texts_of_law/420.11
  [Nicht prüfbar] 403 Offen https://www.baselland.ch/politik-und-behorden/direktionen/bau-und-umweltschutzdirektion/medienmitteilungen/ausgezeichnete-agglomeration-birsstadt-erhaelt-den-wakkerpreis
  [Fehler]  Offen https://www.muenchenstein.ch/legislaturziele
  [Verifiziert] 200 Bestätigt https://www.seelisberg.ch/files/pdf/Druckvorlage2_Original_Versammlung-Nov2025_Traktanden-und-Botschaften-gesamt.pdf
  [Verifiziert] 200 Bestätigt https://www.seelisberg.ch/files/pdf/Bau-und-Zonenordnung-Seelisberg.pdf
  [Verifiziert] 200 Bestätigt https://www.seelisberg.ch/files/pdf/8_20221005_Bericht_Siedlungsleitbild_Genehmigungsexemplar.pdf
  [Verifiziert] 200 Bestätigt https://www.seelisberg.ch/files/pdf/20230526_Erl%C3%A4uterungsbericht.pdf
  [Verifiziert] 200 Bestätigt https://www.seelisberg.ch/personal
  [Verifiziert] 200 Bestätigt https://www.seelisberg.ch/news/neues-leitbild-der-gemeinde-seelisberg
  [Verifiziert] 200 Bestätigt https://www.seelisberg.ch/files/pdf/Beschlussprotokoll_GV_24.11.2023.pdf
  [Fehler]  Offen https://www.ur.ch/_doc/451636
  [Fehler]  Offen https://www.ur.ch/_doc/420775
  [Fehler]  Offen https://www.ur.ch/_docn/426685/Berechnung_FiLa_2025.pdf
  [Fehler]  Offen https://www.ur.ch/dienstleistungen/4297
  [Fehler]  Offen https://www.muenchenstein.ch/publikationen/556069
  [Fehler]  Offen https://www.muenchenstein.ch/publikationen/523381
  [Fehler]  Offen https://www.muenchenstein.ch/sitzung/5729137
  [Fehler]  Offen https://www.muenchenstein.ch/_docn/4130681/Bericht_Aufgaben__Finanzplan_2023-2027_publiziert.pdf
  [Fehler]  Offen https://www.muenchenstein.ch/_docn/1199675/Zonenreglement_Siedlung.pdf
  [Fehler]  Offen https://www.muenchenstein.ch/_docn/1591897/2018.03.12_Ratschlag_GzD.pdf
  [Fehler]  Offen https://www.muenchenstein.ch/_docn/6998503/Ratschlag_Gemeindeversammlung_Montag,_15._Juni_2026.pdf
  [Fehler]  Offen https://www.muenchenstein.ch/_docn/3794018/Bereinigtes_Personalreglement_Genehmigungsfassung_per_23._Juni_2022.pdf
  [Fehler] 404 Offen https://www.stadtwil.ch/_docn/5050942/Jahresrechnung_2023.pdf
  [Fehler] 404 Offen https://www.stadtwil.ch/_doc/5592973
  [Verifiziert] 200 Bestätigt https://www.stadtwil.ch/storage/08902ff399818ccc0d53949607b2d0f6f8bf702c334e295d493c2fd842ba4079
  [Verifiziert] 200 Bestätigt https://www.stadtwil.ch/storage/875d422378d72386aae96efa76356fbfa05e9a0e1e03f208fbbe599dea21021c
  [Verifiziert] 200 Bestätigt https://www.stadtwil.ch/storage/68981c34e629883df15ea09baa331530387503f2a8c37c1259512877afe4840f
  [Verifiziert] 200 Bestätigt https://www.stadtwil.ch/storage/819a3bb87d4ead8a5dc31b37f1d59911eea50dc8005458ebf9ad112a61ce2694
  [Verifiziert] 200 Bestätigt https://www.stadtwil.ch/storage/9bf65acd52bfa75c91cc42760759e0ffc3a76d501e7d174c010444c290801cc2
  [Fehler] 404 Offen https://www.stadtwil.ch/_docn/1058128/PO_101_Fuer_eine_neue_Bodenpolitik_Stellungnahme.pdf
  [Verifiziert] 200 Bestätigt https://www.stadtwil.ch/storage/1e396670eed23bbd41611d92ceaa476797bc97e16fde09c29197453c3b3bc320
  [Verifiziert] 200 Bestätigt https://www.ratsinfo.sg.ch//media/documents/published/signed/8b158b37-2fff-4d5d-b018-ef035f08732e.pdf
  [Verifiziert] 200 Bestätigt https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/731.1
  [Fehler]  Offen https://www.muenchenstein.ch/reglemente/7208
  [Verifiziert] 200 Bestätigt https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/813.1
  [Verifiziert] 200 Bestätigt https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/151.53
  [Fehler] 404 Offen https://stadtwil.ch/_doc/1267121
  [Verifiziert] 200 Bestätigt https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/841.1
  [Verifiziert] 200 Bestätigt https://www.are.admin.ch/dam/de/sd-web/1LGAXN34JMxU/Pr%C3%BCfbericht%20Wil4G.pdf
  [Fehler] 404 Offen https://www.stadtwil.ch/_docn/2747618/012_BA_Erlass_neuesTBW-Reglement.pdf
  [Verifiziert] 200 Bestätigt https://www.sg.ch/content/dam/sgch/bauen/raumentwicklung/agglomerationsprogramme/Wil%20Flyer%205G.pdf
  [Verifiziert] 200 Offen https://www.stadtwil.ch/storage/533b0557b4e4988a6a4f9af13c0b789fec39837eef83d1e66cd1d3814dbe0acb
  [Verifiziert] 200 Offen https://www.stadtwil.ch/storage/5d895f1e33cc1b2c352d7bdeb9d93dd5b2333fbff6a1793cd419f387dd4e1e28
  [Fehler]  Offen https://www.muenchenstein.ch/_docn/5478214/Protokoll_Gemeindeversammlung_13._Juni_2024_definitiv.pdf
  [Fehler]  Offen https://www.muenchenstein.ch/politikinformationen/2666993
  [Fehler]  Offen https://www.muenchenstein.ch/_docn/2359339/43037_Ber05_Mitwirkungsbericht_VerabschiedungGR_Unterschrieben_20190924_korr.pdf
  [Fehler]  Offen https://www.muenchenstein.ch/behoerden/2838
Automatische Recherche (Discovery) …
  Discovery https://www.seelisberg.ch/politik/gemeindeversammlung: 22 Kandidaten
  Discovery https://www.seelisberg.ch/: 21 Kandidaten
  Discovery https://www.seelisberg.ch/ueber-seelisberg/leitbild: 0 Kandidaten
  Discovery-Fehler https://www.ur.ch/publikationen/6680: HTTPSConnectionPool(host='www.ur.ch', port=443): Max retries exceeded with url: /publikationen/6680 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.ur.ch', port=443) at 0x7fcb341b52e0>, 'Connection to www.ur.ch timed out. (connect timeout=25)'))
  Discovery-Fehler https://www.muenchenstein.ch/publikationen/621658: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /publikationen/621658 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0x7fcb341b4350>, 'Connection to www.muenchenstein.ch timed out. (connect timeout=25)'))
  Discovery-Fehler https://www.muenchenstein.ch/publikationen/556069: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /publikationen/556069 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0x7fcb341b4230>, 'Connection to www.muenchenstein.ch timed out. (connect timeout=25)'))
  Discovery-Fehler https://www.muenchenstein.ch/publikationen/523378: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /publikationen/523378 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0x7fcb341b4d10>, 'Connection to www.muenchenstein.ch timed out. (connect timeout=25)'))
  Discovery-Fehler https://www.muenchenstein.ch/publikationen/523381: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /publikationen/523381 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0x7fcb341b5df0>, 'Connection to www.muenchenstein.ch timed out. (connect timeout=25)'))
  Discovery-Fehler https://www.muenchenstein.ch/sitzung/5729137: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /sitzung/5729137 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0x7fcb341b62a0>, 'Connection to www.muenchenstein.ch timed out. (connect timeout=25)'))
  Discovery-Fehler https://www.muenchenstein.ch/sitzung/5729125: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /sitzung/5729125 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0x7fcb341b4fe0>, 'Connection to www.muenchenstein.ch timed out. (connect timeout=25)'))
  Discovery-Fehler https://www.muenchenstein.ch/reglemente/7208: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /reglemente/7208 (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0x7fcb341b55b0>, 'Connection to www.muenchenstein.ch timed out. (connect timeout=25)'))
  Discovery-Fehler https://www.muenchenstein.ch/legislaturziele: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /legislaturziele (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0x7fcb341b5b20>, 'Connection to www.muenchenstein.ch timed out. (connect timeout=25)'))
  Discovery-Fehler https://www.muenchenstein.ch/finanzensteuern: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /finanzensteuern (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0x7fcb341b5610>, 'Connection to www.muenchenstein.ch timed out. (connect timeout=25)'))
  Discovery-Fehler https://www.muenchenstein.ch/organisationuorganigramm: HTTPSConnectionPool(host='www.muenchenstein.ch', port=443): Max retries exceeded with url: /organisationuorganigramm (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.muenchenstein.ch', port=443) at 0x7fcb341b6990>, 'Connection to www.muenchenstein.ch timed out. (connect timeout=25)'))
  Discovery https://www.stadtwil.ch/topics/stadt-politik-und-recht/finanzen: 213 Kandidaten
  Discovery https://www.stadtwil.ch/political-business/28da2d58a16b4b85b0504eeaa7e396dc: 4 Kandidaten
  Discovery https://www.stadtwil.ch/publikationen/90704: HTTP 404
  Discovery https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen/rechnungslegung--rmsg-.html: 63 Kandidaten
  Discovery https://www.baselland.ch/politik-und-behorden/gemeinden/gemeindefinanzen: HTTP 403
  Sitemap https://www.seelisberg.ch: 3 Kandidaten aus 15 Sitemap-Dateien
  Sitemap https://www.muenchenstein.ch: 0 Kandidaten aus 1 Sitemap-Dateien
  Sitemap https://www.stadtwil.ch: 0 Kandidaten aus 1 Sitemap-Dateien
  Keine Such-API konfiguriert (BRAVE_SEARCH_API_KEY fehlt) – Fallback: Einstiegsseiten und Sitemaps
Discovery: 326 Kandidaten
```

## 10 Methode

- Linkprüfung: Syntax → DNS → HEAD (Fallback GET) → GET mit max. 30 MB; 3 Versuche mit Backoff bei Verbindungsfehlern, 429 und 5xx; max. 6 parallele Anfragen, mind. 1.5 s Abstand pro Host; ehrlicher User-Agent; keine Umgehung von Sperren, CAPTCHAs oder Logins.
- Inhaltsprüfung: PDF-Metadaten und Text der ersten 6 Seiten (pypdf) bzw. HTML-Titel/H1/Text; Abgleich mit hinterlegten Schlüsselwörtern und Ortsnamen. Bundesrecht über den Fedlex-SPARQL-Endpunkt, kantonales Recht über die LexWork-JSON-Schnittstelle (falls verfügbar).
- Discovery: offizielle Einstiegsseiten (1–2 Ebenen, robots.txt beachtet) und XML-Sitemaps; optional Brave Search API über Secret `BRAVE_SEARCH_API_KEY`.
