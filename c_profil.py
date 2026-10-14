#!/usr/bin/env python3
"""C-Profil mit Tragfähigkeit der drei Pilotgemeinden (Assignment 01, Aufgabe 2).

Ergänzt C_Grundlagenkataster_verifiziert.xlsx um:
  C-Skalen       Kennzahlen (C1) und Reifegrad-Skalen (C2–C5) mit Schwellen und Begründung
  C-Profil       C1–C5 je Gemeinde: IST-Zustand, Wert/Stufe, Tragfähigkeit, Begründung, Confidence,
                 Felder des C-Wirkungsprofils (Grundlagendokument Kap. 04)
  C-Kennzahlen   Finanzkennzahlen C1 mit Quelle (Runner «Recherche Q und C»)
  C-Methodik     Peer-Notiz C, Recherchevorgehen, Befunde zum Katalog
Die Gemeindeblätter und die Gesamtübersicht bleiben unverändert (generierte Ansichten).

Aufruf: python3 c_profil.py C_Grundlagenkataster_verifiziert.xlsx
"""
import sys

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

STAND = "14.10.2026"
DARK, PALE = "FF18324C", "FFF4F8FA"
TF = {"hoch": "FFC6EFCE", "mittel": "FFFFE699", "gering": "FFF4B6B6", "nicht bewertet": "FFE7E6E6"}
STUFE = {"hoch": 3, "mittel": 2, "gering": 1}
THIN = Side(style="thin", color="FFBFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
VAR = "je Strategievariante (Sprint 2)"

SKALEN = [
    ("C1", "Selbstfinanzierungsgrad (Ø 5 Jahre)", "≥ 100 % gut · 80–100 % vertretbar · 50–80 % problematisch · < 50 % ungenügend",
     "HRM2-Kennzahl nach FDK-Fachempfehlung 18; Richtwerte gemäss Finanzhandbuch BL Kap. 16, Finanzkontrolle Uri und Jahresrechnung Wil"),
    ("C1", "Nettoschuld I pro Einwohner (CHF)", "< 0 Nettovermögen · 0–1'000 gering · 1'001–2'500 mittel · 2'501–5'000 hoch · > 5'000 sehr hoch",
     "HRM2-Richtwerte (identisch in BL, SG, UR verwendet)"),
    ("C1", "Nettoverschuldungsquotient", "< 100 % gut · 100–150 % genügend · > 150 % schlecht",
     "HRM2-Kennzahl erster Priorität (Finanzhandbuch BL)"),
    ("C1", "Entwicklung gemäss Finanzplan", "Prognose der Nettoschuld pro Einwohner am Planende", "Gate-Regel Kap. 16: eine Spitze "
     "wird durch einen guten Endwert nicht kompensiert"),
    ("C1", "Regel Tragfähigkeit", "hoch: SFG ≥ 80 % und Nettoschuld ≤ 1'000 CHF/EW, ohne Verschlechterung im Finanzplan · "
     "gering: SFG < 50 % (Ø) oder Nettoschuld > 2'500 CHF/EW (IST oder Finanzplan) oder NVQ > 150 % · sonst mittel",
     "Eigene Festlegung auf Basis der HRM2-Richtwerte; im Pilot zu kalibrieren (Grundlagendokument M1.2)"),
    ("C2", "Reifegrad Boden", "3 hoch: Boden-/Liegenschaftsstrategie beschlossen, Finanzkompetenz für Landgeschäfte und belegtes "
     "Eigentum oder Baurechte in Entwicklungsgebieten · 2 mittel: Instrumente oder Praxis vorhanden (Landgeschäfte, Baurechte), "
     "Strategie oder Eigentum in Entwicklungsgebieten unklar · 1 gering: keine Bodenpolitik dokumentiert, kein relevantes Eigentum bekannt",
     "Grundlagendokument Kap. 04 (Bodensicherung, -mobilisierung, -vergabe); ÖBA-Zonen gelten nicht als Eigentumsnachweis"),
    ("C3", "Reifegrad Governance", "3 hoch: Zuständigkeiten geregelt, institutionalisierte überkommunale Kooperation (Region/Agglomeration) "
     "und Trägerschaftsmodelle für Projekte · 2 mittel: Zuständigkeiten geregelt, Kooperation punktuell (Leistungsvereinbarungen, "
     "Verbände) · 1 gering: Zuständigkeiten oder Kooperationen nicht belegt",
     "Grundlagendokument Kap. 04 (Kooperationsstrukturen, klare Verantwortungsträgerschaft)"),
    ("C4", "Reifegrad Verwaltung", "3 hoch: eigene Fachstelle Planung/Stadtentwicklung, Projektorganisation, geregelte Beschaffung · "
     "2 mittel: Bauverwaltung mit Fachpersonal, Grossprojekte mit externen Mandaten · 1 gering: Kleinverwaltung bzw. Milizbehörde, "
     "Planung vollständig extern",
     "Grundlagendokument Kap. 04 und Q6 (Bestellerkompetenz, Principal-Agent)"),
    ("C5", "Reifegrad Politik", "3 hoch: Leitbild/Strategie politisch verabschiedet, etablierte Mitwirkung und belegte Mehrheiten für "
     "Entwicklungsvorhaben · 2 mittel: Leitbild oder Mitwirkung vorhanden, Mehrheitsfähigkeit für Entwicklung nicht belegt · "
     "1 gering: keine Grundlagen oder belegte Blockaden",
     "Grundlagendokument Kap. 04 (Mitwirkung, Mehrheitsfähigkeit)"),
    ("Gesamt", "Regel Gesamt-Tragfähigkeit", "Mittelwert der bewerteten Dimensionen (hoch = 3, mittel = 2, gering = 1), gerundet; "
     "C1 «gering» begrenzt das Gesamt auf «gering» (Gate)",
     "Gate-Regel Kap. 16; Bewertung vorläufig, solange Confidence tief"),
]

# Gemeinde, Dimension, IST-Zustand, Kennzahl/Kriterium, Wert/Stufe, Massstab, Tragfähigkeit, Begründung,
# Confidence, Quelle, Lücke/Anfrage, Fähigkeitslücke
PROFIL = [
    ("Seelisberg", "C1 Finanzen", "Kleiner Haushalt (724 EW), seit Jahren Nettovermögen; Steuerfuss 110 % (2026 unverändert); "
     "Budget 2026 mit kleinem Aufwandüberschuss (CHF 42'000)",
     "Selbstfinanzierungsgrad; Nettoschuld I und II pro EW; NVQ",
     "SFG 2021–2025: 406 / 100 / 335 / 100 / 116 %; Nettoschuld I 2024: −5'985 CHF/EW; Nettoschuld II 2025: −7'421 CHF/EW; "
     "NVQ 2024: −215 %",
     "HRM2-Richtwerte; Kanton UR 2025: SFG 148 %, Nettoguthaben 555 CHF/EW", "hoch",
     "Nettovermögen weit über dem Kantonsmittel, Selbstfinanzierung > 100 %. Wegen des kleinen Haushalts kann jedoch "
     "schon ein grösseres Infrastrukturprojekt (z. B. Erschliessung Sonnenberg) die Kapazität übersteigen.",
     "hoch", "SEE-C1-03 (Jahresrechnung 2024), UR-C1-03 (Kennzahlen 2025), SEE-C1-02 (Budget 2026)", "A-SEE-01, A-SEE-02",
     "Mehrjähriger Investitionsplan nicht öffentlich"),
    ("Seelisberg", "C2 Boden", "Planungsverfahren Sonnenberg und Siedlungsleitbild 2022 öffentlich; kein Liegenschaftsverzeichnis, "
     "keine Baurechte oder Landgeschäfte belegt", "Reifegrad Boden", "Stufe 1", "Reifegrad-Skala C2", "gering",
     "Keine dokumentierte Bodenpolitik; Rolle der Gemeinde beim Projekt Sonnenberg unklar. Vorläufig, bis Eigentum geklärt ist.",
     "tief", "SEE-C2-01, SEE-C2-03, SEE-C2-04", "A-SEE-03, A-SEE-04, A-SEE-09", "Eigentum und Verfügungsrechte unbekannt"),
    ("Seelisberg", "C3 Governance", "Gemeindeordnung und Behördenstruktur öffentlich; Zweckverbände und Kooperationen nicht belegt",
     "Reifegrad Governance", "Stufe 1", "Reifegrad-Skala C3", "gering",
     "Zuständigkeiten geregelt, überkommunale Kooperationen und Trägerschaften öffentlich nicht nachweisbar. Vorläufig.",
     "tief", "SEE-C3-01, SEE-C3-02", "A-SEE-05", "Kooperationen/Verträge unbekannt"),
    ("Seelisberg", "C4 Verwaltung", "Kleinverwaltung; Personalseite ohne Pensen; Restrukturierung der Verwaltung im Budget 2026 erwähnt",
     "Reifegrad Verwaltung", "Stufe 1", "Reifegrad-Skala C4", "gering",
     "Für grössere Entwicklungsvorhaben ist externe Projektleitung und Bestellerkompetenz nötig.",
     "mittel", "SEE-C4-01 bis SEE-C4-04", "A-SEE-06", "Stellenplan und Projektressourcen unbekannt"),
    ("Seelisberg", "C5 Politik", "Neues Leitbild 2025 mit Workshop und Umfrage; Gemeindeversammlung beschliesst Budget und Leitbild; "
     "Urnenabstimmung 8.3.2026", "Reifegrad Politik", "Stufe 2", "Reifegrad-Skala C5", "mittel",
     "Strategische Grundlage und Mitwirkung vorhanden; Mehrheitsfähigkeit konkreter Entwicklungsvorhaben nicht belegt.",
     "mittel", "SEE-C5-01 bis SEE-C5-08", "A-SEE-07, A-SEE-08", "Umfrageauswertung, Akteurspositionen"),
    ("Münchenstein", "C1 Finanzen", "Jahresrechnungen 2024/2025 und AFP 2026–2030 öffentlich; Baurechtszinsen und Landverkäufe als "
     "Ertragsquellen dokumentiert", "Selbstfinanzierungsgrad; Nettoschuld I pro EW; NVQ",
     "nicht extrahiert (Gemeindewebsite im Runner nicht erreichbar bzw. ohne direkte PDF-Links)",
     "HRM2-Richtwerte; Peer Kanton BL × Grösse (Statistik BL, 403 für Bots)", "nicht bewertet",
     "Kennzahlen müssen aus der Jahresrechnung 2025 (MUE-C1-02) und dem AFP übernommen werden.",
     "tief", "MUE-C1-01 bis MUE-C1-06", "A-MUE-01, A-MUE-02", "Kennzahlenreihe 2021–2025"),
    ("Münchenstein", "C2 Boden", "Landverkäufe und Baurechte praktiziert (Ratschläge 2015 und 2018, Baurechtszinsen); "
     "Mehrwertabgabe im Zonenreglement; keine aktuelle Bodenstrategie gefunden", "Reifegrad Boden", "Stufe 2",
     "Reifegrad-Skala C2", "mittel", "Instrumente und Praxis vorhanden, Strategie und Eigentum in Entwicklungsgebieten offen.",
     "mittel", "MUE-C2-01 bis MUE-C2-03", "A-MUE-03, A-MUE-04, A-MUE-09", "Liegenschaftsverzeichnis, Baurechtsverträge"),
    ("Münchenstein", "C3 Governance", "Mitglied der Birsstadt (Verein, Wakkerpreis), Agglomeration Basel; interkommunale "
     "Leistungsvereinbarungen; Gemeindeordnung Stand 2013", "Reifegrad Governance", "Stufe 2", "Reifegrad-Skala C3", "mittel",
     "Regionale Kooperation institutionalisiert, Trägerschaftsmodelle für Projekte nicht belegt.",
     "mittel", "MUE-C3-01, MUE-C3-02, BL-C3-02", "A-MUE-05", "Übersicht Zweckverbände und Verträge"),
    ("Münchenstein", "C4 Verwaltung", "Organigramm und Personalreglement öffentlich; Verwaltungs- und Organisationsreglement Stand "
     "2000; Quartierplanungen (u. a. Spenglerpark) umgesetzt", "Reifegrad Verwaltung", "Stufe 2", "Reifegrad-Skala C4", "mittel",
     "Bauverwaltung mit Fachpersonal; Kapazität für grössere Arealentwicklungen nicht belegt.",
     "mittel", "MUE-C4-01 bis MUE-C4-03", "A-MUE-06", "Pensen Bauverwaltung, Projektorganisation"),
    ("Münchenstein", "C5 Politik", "Gemeindeversammlung und Gemeindekommission; Legislaturziele 2024–2028; Mitwirkungsbericht "
     "Spenglerpark 2019", "Reifegrad Politik", "Stufe 2", "Reifegrad-Skala C5", "mittel",
     "Ziele und Mitwirkungspraxis vorhanden; Mehrheiten für Entwicklung nicht systematisch belegt.",
     "mittel", "MUE-C5-01 bis MUE-C5-05", "A-MUE-07, A-MUE-08", "Akteurspositionen, Diskussion Einwohnerrat"),
    ("Wil", "C1 Finanzen", "2024 Defizit und hohe Investitionen; Steuerkraft 2'997 CHF/EW (Vorjahr 3'226); Finanzplan 2026–2030 "
     "mit Steuerfusserhöhung", "Selbstfinanzierungsgrad; Nettoschuld pro EW; NVQ; Finanzplan",
     "SFG 2024: 15 %; Nettoschuld/EW 2020–2024: 1'173 / 1'003 / 764 / 829 / 1'459 CHF; NVQ 2024: 42 %; Finanzplan: "
     "Pro-Kopf-Verschuldung verdoppelt sich, Nettoschuld steigt auf rund CHF 105 Mio.",
     "HRM2-Richtwerte; Peer Kanton SG × Grösse (Statistik SG, nicht abgerufen)", "mittel",
     "IST mittlere Verschuldung und guter NVQ, aber sehr tiefe Selbstfinanzierung 2024 und gemäss Finanzplan Übergang zu hoher "
     "Verschuldung (> 2'500 CHF/EW) – Gate-Risiko in der Investitionsphase. Tendenz Richtung «gering».",
     "mittel", "WIL-C1-04 (Jahresrechnung 2024), WIL-C1-06 (Finanzplan 2026–2030)", "A-WIL-01, A-WIL-02",
     "SFG-Reihe 2021–2025; Rechnung 2025 der Stadt (WIL-C1-05 verweist auf TBW-Bericht)"),
    ("Wil", "C2 Boden", "Dokument «aktive Bodenpolitik / Boden- und Immobilienstrategie»; Nachtrag IV zur Gemeindeordnung "
     "(Finanzbefugnisse Liegenschaften, 2024)", "Reifegrad Boden", "Stufe 2", "Reifegrad-Skala C2", "mittel",
     "Strategie und Kompetenzordnung vorhanden; Eigentum und Baurechte in Entwicklungsgebieten nicht belegt, Geltung Nachtrag IV offen.",
     "mittel", "WIL-C2-01, WIL-C2-03", "A-WIL-03, A-WIL-04, A-WIL-09", "Liegenschaftsverzeichnis"),
    ("Wil", "C3 Governance", "Regio Wil und Agglomerationsprogramm Wil (Prüfbericht Bund 4. Generation, 5. Generation in "
     "Arbeit); Beteiligungen (Technische Betriebe Wil); Rechtssammlung online", "Reifegrad Governance", "Stufe 3",
     "Reifegrad-Skala C3", "hoch", "Institutionalisierte regionale Kooperation und eigene Trägerschaften (TBW) belegt.",
     "mittel", "WIL-C3-01, WIL-C3-04, WIL-C3-05, WIL-C1-09", "A-WIL-05", "Eignerstrategien, Statuten Regio Wil"),
    ("Wil", "C4 Verwaltung", "Stadtverwaltung mit Departementen und Stadtplanung; Geschäftsbericht 2025; Reglement über Ausgaben- "
     "und Vertragskompetenzen (SRS 1.6-4)", "Reifegrad Verwaltung", "Stufe 3", "Reifegrad-Skala C4", "hoch",
     "Fachstellen und geregelte Kompetenzen vorhanden; Kapazität (Stellenplan) nicht belegt.",
     "mittel", "WIL-C4-01", "A-WIL-06", "Organigramm, Stellenplan Bau/Stadtentwicklung"),
    ("Wil", "C5 Politik", "Stadtparlament; Legislaturplanung 2025–2028; Mitwirkung Ortsplanungsrevision 2025; Planungsbericht "
     "Richtplan Siedlung 2026", "Reifegrad Politik", "Stufe 2", "Reifegrad-Skala C5", "mittel",
     "Strategie und Mitwirkung vorhanden; Ergebnisse der Mitwirkung und Mehrheiten für Entwicklung nicht belegt.",
     "mittel", "WIL-C5-01 bis WIL-C5-03", "A-WIL-07, A-WIL-08", "Mitwirkungsberichte, Akteurspositionen"),
]

KENNZAHLEN = [
    ("Seelisberg", "Selbstfinanzierungsgrad", "2021–2025", "405.9 / 100.0 / 334.9 / 100.0 / 115.9 %",
     "Finanzkontrolle UR, Kennzahlen 2025, S. 22", "https://www.ur.ch/_docn/451636/Gemeindekennzahlen_2025_signiert.pdf"),
    ("Seelisberg", "Nettoschuld II pro Kopf", "2020–2025", "−3'396 / −3'960 / −5'062 / −5'951 / −6'707 / −7'421 CHF",
     "Finanzkontrolle UR, Kennzahlen 2025, S. 23", "https://www.ur.ch/_docn/451636/Gemeindekennzahlen_2025_signiert.pdf"),
    ("Seelisberg", "Nettoschuld I pro Einwohner", "2019–2024", "−2'562 / −2'487 / −3'224 / −4'318 / −5'204 / −5'985 CHF",
     "Jahresrechnung 2024, S. 19", "https://www.seelisberg.ch/files/pdf/JR2024_Gde-Seelisberg.pdf"),
    ("Seelisberg", "Nettoverschuldungsquotient", "2024", "−214.7 %", "Jahresrechnung 2024, S. 18",
     "https://www.seelisberg.ch/files/pdf/JR2024_Gde-Seelisberg.pdf"),
    ("Kanton UR (alle Gemeinden)", "Selbstfinanzierungsgrad / Nettoguthaben pro Kopf", "2025", "148.2 % / 555 CHF",
     "Finanzkontrolle UR, Kennzahlen 2025, S. 3", "https://www.ur.ch/_docn/451636/Gemeindekennzahlen_2025_signiert.pdf"),
    ("Wil", "Selbstfinanzierungsgrad", "2024", "15 %", "Jahresrechnung 2024, S. 3 und 13",
     "https://www.stadtwil.ch/storage/0f0d7ad95464bf91a72506e63d2aae1d5c18327f9bff4bf34b8400c36999b277"),
    ("Wil", "Nettoschuld pro Einwohner", "2020–2024", "1'173 / 1'003 / 764 / 829 / 1'459 CHF", "Jahresrechnung 2024, S. 30",
     "https://www.stadtwil.ch/storage/0f0d7ad95464bf91a72506e63d2aae1d5c18327f9bff4bf34b8400c36999b277"),
    ("Wil", "Nettoverschuldungsquotient", "2020–2024", "34 / 30 / 22 / 22 / 42 %", "Jahresrechnung 2024, S. 30",
     "https://www.stadtwil.ch/storage/0f0d7ad95464bf91a72506e63d2aae1d5c18327f9bff4bf34b8400c36999b277"),
    ("Wil", "Nettoschuld (Finanzplan)", "2026–2030", "Verdoppelung auf rund CHF 105 Mio.; pro Kopf «hohe Verschuldung»",
     "Finanzplan 2026–2030, S. 12",
     "https://www.stadtwil.ch/storage/875d422378d72386aae96efa76356fbfa05e9a0e1e03f208fbbe599dea21021c"),
    ("Münchenstein", "Kennzahlen HRM2", "2021–2025", "nicht extrahiert", "Jahresrechnung 2025 (MUE-C1-02)",
     "https://www.muenchenstein.ch/publikationen/621658"),
]

METHODIK = [
    ("Peer-Gruppen C", "Ausgangshypothese bestätigt: C1 Kanton × Grössenklasse plus HRM2-Richtwerte; C2–C5 ohne Peers. "
     "Begründung: Finanzkennzahlen werden kantonal einheitlich nach HRM2 erhoben und sind nur innerhalb eines Kantons "
     "(Aufgabenteilung, Finanzausgleich) vergleichbar; die Richtwerte liefern einen kantonsunabhängigen Massstab. Für Uri "
     "liegt die Kennzahlentabelle aller Gemeinden vor (Peer direkt bildbar); für BL und SG sind die kantonalen Statistiken "
     "öffentlich, aber im Runner nicht abrufbar gewesen. C2–C5 sind qualitative Reifegrade ohne vergleichbare Erhebung."),
    ("Recherchevorgehen C", "1. Kataster C1–C5 je Ebene aufbauen und Links prüfen (scripts/verify_c_sources.py). "
     "2. Finanzkennzahlen automatisiert aus Jahresrechnungen und kantonalen Kennzahlenberichten (PDF) extrahieren "
     "(recherche_qc.py). 3. C2–C5 anhand der Katalogbelege der Reifegrad-Skala zuordnen; fehlende Belege führen zu Stufe 1 "
     "mit tiefer Confidence. 4. Lücken in «Gemeindeanfragen» führen. 5. Bewertung mit Gemeinde validieren."),
    ("Verlässlichkeit", "C1 hoch, wo amtliche Kennzahlen vorliegen (Seelisberg, Wil); C2–C5 vorläufig, weil öffentliche "
     "Dokumente Strukturen belegen, nicht aber Kapazität, Eigentum oder Mehrheiten."),
    ("Befund Katalog", "WIL-C1-05 («Rechnung 2025 Stadt Wil – Finanzbericht») verweist inhaltlich auf den Geschäftsbericht der "
     "Technischen Betriebe Wil (Eigenkapital Elektrizitätsversorgung, Beteiligungen), nicht auf die Rechnung der Stadt. "
     "Link ersetzen oder Bezeichnung anpassen."),
    ("Mehrperiodik", "Das IST-Profil ist der Startpunkt 2025 der mehrperiodischen C-Prüfung (Kap. 16: 2025/2030/2035/2040/2045). "
     "Die übrigen Felder des C-Wirkungsprofils werden je Strategievariante in Sprint 2 befüllt."),
]


def hdr(row):
    for c in row:
        c.font = Font(name="Aptos", size=10, bold=True, color="FFFFFFFF")
        c.fill = PatternFill("solid", fgColor=DARK)
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = BORDER


def body(ws, first, last, ncol):
    for r in range(first, last + 1):
        for c in range(1, ncol + 1):
            cell = ws.cell(r, c)
            cell.font = Font(name="Aptos", size=10, color="FF0563C1", underline="single") if cell.hyperlink \
                else Font(name="Aptos", size=10)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = BORDER


def sheet(wb, name):
    if name in wb.sheetnames:
        del wb[name]
    return wb.create_sheet(name)


def main():
    path = sys.argv[1]
    wb = openpyxl.load_workbook(path)

    ws = sheet(wb, "C-Skalen")
    ws.append(["Dimension", "Kennzahl / Kriterium", "Schwellen bzw. Stufen", "Begründung / Quelle"])
    hdr(ws[1])
    for s in SKALEN:
        ws.append(list(s))
    body(ws, 2, ws.max_row, 4)
    for col, w in zip("ABCD", (12, 34, 90, 60)):
        ws.column_dimensions[col].width = w

    ws = sheet(wb, "C-Profil")
    cols = ["Gemeinde", "Dimension", "Institutioneller IST-Zustand", "Kennzahl / Kriterium", "Wert / Stufe", "Massstab",
            "Tragfähigkeit", "Begründung", "Confidence", "Quelle (Katalog-ID)", "Gemeindeanfrage",
            "Fähigkeits-/Umsetzungslücke (IST)", "Kausal notwendige Ausrichtung", "Institutionelle Folgewirkung",
            "Massnahme und Verantwortlichkeit", "Zeitpunkt und Abhängigkeit", "Kennzahl und Zielkorridor"]
    ws.append(cols)
    hdr(ws[1])
    gesamt = {}
    for p in PROFIL:
        g, dim, ist, kz, wert, mass, tf, beg, conf, quelle, anfrage, luecke = p
        ws.append([g, dim, ist, kz, wert, mass, tf, beg, conf, quelle, anfrage, luecke, VAR, VAR, VAR, VAR,
                   f"{kz}; Zielkorridor {VAR}"])
        ws.cell(ws.max_row, 7).fill = PatternFill("solid", fgColor=TF[tf])
        gesamt.setdefault(g, []).append((dim[:2], tf))
    for g, vals in gesamt.items():
        bew = [STUFE[t] for _, t in vals if t in STUFE]
        c1 = dict(vals).get("C1")
        mean = sum(bew) / len(bew)
        tf = {3: "hoch", 2: "mittel", 1: "gering"}[int(mean + 0.5)]
        note = f"Mittelwert {mean:.1f} aus {len(bew)} bewerteten Dimensionen"
        if c1 == "gering":
            tf, note = "gering", note + "; C1-Gate greift"
        if c1 == "nicht bewertet":
            note += "; ohne C1 (Kennzahlen fehlen) – vorläufig"
        ws.append([g, "Gesamt", "Zusammenfassung C1–C5", "Regel Gesamt-Tragfähigkeit (Blatt C-Skalen)",
                   " / ".join(f"{d}: {t}" for d, t in vals), "–", tf, note,
                   "tief" if any(t == "nicht bewertet" for _, t in vals) else "mittel", "–", "–", "–", VAR, VAR, VAR,
                   VAR, VAR])
        ws.cell(ws.max_row, 7).fill = PatternFill("solid", fgColor=TF[tf])
        for c in range(1, len(cols) + 1):
            ws.cell(ws.max_row, c).font = Font(name="Aptos", size=10, bold=True)
    body(ws, 2, ws.max_row, len(cols))
    for r in range(ws.max_row - 2, ws.max_row + 1):
        for c in range(1, len(cols) + 1):
            ws.cell(r, c).font = Font(name="Aptos", size=10, bold=True)
            if c != 7:
                ws.cell(r, c).fill = PatternFill("solid", fgColor=PALE)
    for col, w in zip("ABCDEFGHIJKLMNOPQ", (14, 14, 46, 26, 40, 30, 14, 50, 11, 30, 18, 30, 22, 22, 22, 22, 26)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:Q{ws.max_row}"

    ws = sheet(wb, "C-Kennzahlen")
    ws.append(["Gemeinde", "Kennzahl", "Zeitraum", "Werte", "Fundstelle", "Link"])
    hdr(ws[1])
    for k in KENNZAHLEN:
        ws.append(list(k))
        ws.cell(ws.max_row, 6).hyperlink = k[5]
    body(ws, 2, ws.max_row, 6)
    for col, w in zip("ABCDEF", (24, 34, 12, 60, 36, 60)):
        ws.column_dimensions[col].width = w

    ws = sheet(wb, "C-Methodik")
    ws.append(["Thema", "Inhalt"])
    hdr(ws[1])
    for m in METHODIK:
        ws.append(list(m))
    body(ws, 2, ws.max_row, 2)
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 140

    # Hinweise und Bewertungslogik nachführen
    h = wb["Hinweise"]
    for row in h.iter_rows():
        if row[0].value == "Tragfähigkeit":
            row[1].value = ("Vorläufig bewertet im Blatt «C-Profil» (Stand " + STAND + ") nach den Skalen im Blatt "
                            "«C-Skalen»; Katalogzeilen bleiben «Noch nicht bewertet», weil ein Dokument allein keine "
                            "Tragfähigkeit belegt.")
    bl = wb["Bewertungslogik"]
    for row in bl.iter_rows(min_row=2):
        if row[0].value in ("C1", "C2", "C3", "C4", "C5"):
            row[6].value = "Festgelegt " + STAND + " (Blatt C-Skalen); im Pilot zu kalibrieren"
            row[7].value = "Angewendet im Blatt C-Profil" + (
                " (Münchenstein: Kennzahlen noch nicht extrahiert)" if row[0].value == "C1" else " (vorläufig)")
    order = ["Hinweise", "C-Profil", "C-Skalen", "C-Kennzahlen", "C-Methodik"]
    wb._sheets = [wb[n] for n in order] + [s for s in wb._sheets if s.title not in order]
    wb.active = 0
    wb.save(path)
    print("ok")


if __name__ == "__main__":
    main()
