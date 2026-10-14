# Prüfbericht Assignment 01 (Niklas) – IST Q und C

Stand 14.10.2026 · Grundlage: Aufgabenprofile.docx (Niklas – Assignment 01) und Grundlagendokument Dimensionsraster und RAG, Version 8 (Kap. 04, 05, 06, 11, 12, 16, M1).

Geprüfte Dateien:
- `Q-Rahmen_Uebersicht_V1.xlsx` (Q-Katalog, Q-Restriktionsprofile)
- `C_Grundlagenkataster_verifiziert.xlsx` (C-Katalog, C-Profil)

Legende: ✅ erfüllt · 🟡 teilweise · ❌ fehlt

## 1. Outputs des Assignments

| Output | Stand | Wo | Bemerkung |
| --- | --- | --- | --- |
| Q-Restriktionsprofil (x3) | ✅ | Q-Rahmen, Blätter 11–13 | 27 Restriktionen je Gemeinde, Einordnung nach Regeln (Blatt 10), Gegeninteressen benannt. FFF, Naturgefahren (BL/SG), Gewässerraum und Hitze sind noch «offen». |
| C-Profil mit Tragfähigkeit (x3) | 🟡 | C-Kataster, Blatt «C-Profil» | C1–C5 mit Tragfähigkeit hoch/mittel/gering und Gesamt. Münchenstein C1 nicht bewertet (Kennzahlen nicht extrahiert); C2–C5 vorläufig. |
| Akteurskarte (x3) | ❌ | – | Nicht erstellt. Nur Gemeindeanfragen A-*-08 vorhanden. |
| Notiz Peer-Gruppen | 🟡 | Q: Blatt 10 · C: Blatt «C-Methodik» | Hypothese begründet bestätigt (Q keine, C1 Kanton × Grösse + Richtwerte, C2–C5 keine). Peer-Werte nur für Uri (Kantonsmittel), nicht als Median/P25/P75 je Kanton × Grösse. |
| Recherchevorgehen dokumentiert | ✅ | Q: Blatt 15 · C: Blatt «C-Methodik» | Wiederholbar über drei GitHub-Runner (Linkprüfung, GIS-Betroffenheit, Recherche Q/C), mit Verlässlichkeit je Schritt. |
| Liste Daten der Gemeinde | 🟡 | Q: Blatt 14 · C: Blatt «Gemeindeanfragen» | Inhaltlich vorhanden, aber auf zwei Dateien verteilt; noch keine gemeinsame Vorlage je Gemeinde. |

## 2. Aufgaben und Grundsätze

| Punkt | Stand | Befund |
| --- | --- | --- |
| Q1–Q5 erfassen (Richtplan, FFF, Schutzgebiete, Energie, Naturgefahren, Hitze, ISOS) | 🟡 | Richtplan, Schutzgebiete, Energie, ISOS erfasst und per GIS belegt. FFF, kantonale Naturgefahren (BL, SG) und Hitze ohne Daten. |
| Einordnung Ausschluss / Interessenabwägung / unkritisch | ✅ | Regeltabelle mit Rechtsgrundlage (Blatt 10), Einordnung je Perimeter. |
| Gegenüberstehende Interessen benennen | ✅ | Je Restriktion in den Profilen. |
| Abwägung nicht in LP01 | ✅ | Ausdrücklich so vermerkt. |
| C1–C5 erfassen, Kennzahlen/Reifegrade festlegen und begründen | ✅ | Blatt «C-Skalen» mit HRM2-Richtwerten und Reifegrad-Stufen 1–3. |
| C2 Näherung über ÖBA-Zonen, Bilanz, Baurechte, Parzellenstruktur | 🟡 | Baurechte/Landgeschäfte aus Dokumenten; ÖBA-Zonen, Parzellenstruktur (Luucy) und Liegenschaften im Finanzvermögen (Bilanz) noch nicht ausgewertet. |
| Je Angabe Quelle, Aktualität, Confidence | ✅ | In beiden Katalogen und Profilen. |
| Lücken dokumentieren, als Lieferung der Gemeinde annehmen | ✅ | Q-Datenanfrage und Gemeindeanfragen C. |
| A-/B-Daten übernehmen (Lias, Nikolaos) | ❌ | Bevölkerung, Steuerkraft, Grössenklassen (Lias) und Luucy-Daten (Nikolaos) sind noch nicht eingebunden; Q-Lücken (FFF, Bauzonenreserven) sollten aus Luucy kommen. |

## 3. Abgleich mit dem Grundlagendokument

| Anforderung | Stand | Befund |
| --- | --- | --- |
| Kap. 05: Q1–Q6 als verbindlicher Rahmen; Q6 als Prozessqualität | ✅ | Q6 im Katalog, im Restriktionsprofil bewusst nicht als räumliche Restriktion (Abgrenzung zu C3/C4). |
| Kap. 05: Vorrangregel, keine Doppelbewertung | ✅ | In Blatt 10 übernommen. |
| Kap. 11: Q als Ausgangslage, nicht als Benchmark | ✅ | Keine Peers für Q. |
| Kap. 11: C-Messgrössen (Selbstfinanzierungsgrad, Nettoschuld/EW) | 🟡 | Seelisberg und Wil belegt, Münchenstein offen. |
| Kap. 11: Bodenanteil/Mobilisierungsquote, Verfahrensdauer/Digitalisierung, Verwaltungskosten/EW | ❌ | Nicht quantifiziert (Verwaltungskosten/EW wäre aus Jahresrechnungen ableitbar). |
| Kap. 11: Vergleich mit P25/Median | ❌ | Noch keine Peer-Verteilung für C1. |
| Kap. 04: C-Wirkungsprofil (7 Felder) | ✅ (IST) | Struktur vollständig; nur IST-Felder befüllt, die übrigen sind «je Strategievariante (Sprint 2)» – für LP01-IST korrekt. |
| Kap. 12: IST-Synthese «wesentliche Q-Restriktionen», «institutionelle Fähigkeit» | ✅ | Synthese je Gemeinde in den Q-Profilen und Gesamtzeile im C-Profil. |
| Kap. 16: mehrperiodische C-Prüfung | ✅ (Start) | IST = Startpunkt 2025, dokumentiert. |
| Kap. 06 / M1: Indikatorrolle P/E/M/Proxy/n. v., Datenqualität Q-A/Q-B/Q-C | ❌ | Nicht gekennzeichnet; heute nur Confidence hoch/mittel/tief. |

## 4. Was gut ist

- **Q-Katalog Mappe 1 ist vollständig und geprüft.** Alle Links stimmen mit Bezeichnung und Referenz überein; kantonale Ausführungserlasse, IVHB und Zonenplan Münchenstein sind ergänzt.
- **Belegte räumliche Betroffenheit:** Alle Bundesinventare sind per GIS-Abfrage je Gemeinde ausgewertet, mit Objektnamen (z. B. Moorlandschaft Oberbauen/Scheidegg, Thurauen, TWW Brüglingen).
- **Transparente Einordnung:** Jede Restriktion hat eine Regel mit Rechtsgrundlage; die Profile sind regelbasiert erzeugt (`q_restriktionsprofil.py`) und damit wiederholbar.
- **Harte C1-Werte für zwei Gemeinden:** Seelisberg (Nettovermögen 7'421 CHF/EW, SFG 116 %) und Wil (Nettoschuld 1'459 CHF/EW, SFG 15 %, Finanzplan mit Verdoppelung der Schulden) direkt aus amtlichen Berichten.
- **Automatisierung:** Drei Runner decken Linkprüfung, GIS-Betroffenheit und Dokumentrecherche ab; neue Gemeinden lassen sich mit wenig Aufwand ergänzen.
- **Ehrliche Unsicherheit:** Vorläufige Einstufungen sind als solche markiert; Lücken stehen konkret in den Datenanfragen.

## 5. Was noch fehlt (Vorschlag für den nächsten Schritt)

1. **Akteurskarte x3** erstellen (Politik, Verwaltung, Kanton, Region, Grundeigentum, Wirtschaft, Zivilgesellschaft, Infrastruktur; je Rolle, Einfluss, Dimensionen, Interessen, Haltung).
2. **Münchenstein C1:** Kennzahlen aus Jahresrechnung 2025 und AFP 2026–2030 übernehmen (Website war für den Runner nicht erreichbar).
3. **C1-Peers:** Kantonsstatistiken BL und SG beschaffen und Median/P25/P75 je Kanton × Grösse berechnen; für Uri aus der vorhandenen Kennzahlentabelle.
4. **Luucy-Daten von Nikolaos** einbinden: FFF, Bauzonenreserven, ÖBA-Zonen, Parzellenstruktur (schliesst die meisten «offen» im Q-Profil und stützt C2).
5. **Kantonale Q-Daten:** Gefahrenkarten BL/SG, Gewässerraum/Grundwasserschutz, Klimaanalysen BL/SG.
6. **Daten von Lias** (Bevölkerung, Steuerkraft, Grössenklassen) für Pro-Kopf-Werte und Grössenklasse übernehmen.
7. **Gemeinsame Datenanfrage je Gemeinde** aus Q- und C-Listen zusammenführen.
8. **Indikatorrollen** (P/E/M/Proxy/n. v.) und Datenqualität Q-A/Q-B/Q-C ergänzen; Verwaltungskosten/EW berechnen.
9. **Katalogkorrektur C:** WIL-C1-05 verweist auf den TBW-Geschäftsbericht statt auf die Rechnung der Stadt.
10. **Wil BLN:** Abweichung GIS-Abfrage («ja») gegenüber manueller Sichtung («nein») im Viewer klären.
