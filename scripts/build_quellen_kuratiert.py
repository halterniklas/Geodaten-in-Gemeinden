#!/usr/bin/env python3
"""Erzeugt data/quellen_kuratiert.json (kuratierte Quellen, Korrekturen, Gemeindeanfragen).

Aufruf: python3 scripts/build_quellen_kuratiert.py data/quellen_kuratiert.json
Alle Einträge sind Rechercheergebnisse; jede URL wird von verify_c_sources.py geprüft.
"""
import json, sys

STAND = "2026-10-14"
DISC = "Automatische Recherche GitHub Actions (Discovery), Fundstelle siehe Spalte Offizielle Fundstelle"
WEB = "Websuche 14.10.2026 (URL im Suchergebnis gefunden)"
SCHEMA = "URL nach dokumentiertem Schema der amtlichen Rechtssammlung gebildet; Identität per Runner geprüft"

def law_ort():
    return []

KT = {"UR": "Uri", "BL": "Basel-Landschaft", "SG": "St. Gallen"}
GEM = {"SEE": ("Seelisberg", "Uri"), "MUE": ("Münchenstein", "Basel-Landschaft"), "WIL": ("Wil", "St. Gallen")}

def src(id, dim, thema, titel, doktyp, rechtsstatus, herausgeber, url, erwartet, bezugsjahr="", relevanz="", kennzahl="",
        methode="", vergleich=None, confidence="Hoch", fundstelle="", datenluecke="", verbindung="", sprint2="",
        pruefnachweis="", hinweis="", herkunft=WEB, weitere_dim="", ort=None, anfrage=None, zustaendig=None,
        dokstatus="Direktes Dokument", veroeffentlicht="", belege=None):
    pre = id.split("-")[0]
    if pre == "CH":
        ebene, kanton, gemeinde = "Bund", "Alle", "Alle"
    elif pre in KT:
        ebene, kanton, gemeinde = "Kanton", KT[pre], "Alle"
    else:
        ebene = "Gemeinde"
        gemeinde, kanton = GEM[pre]
    if vergleich is None:
        vergleich = "Kanton × Grössenklasse" if dim == "C1" else "Kein Peer-Vergleich"
    d = dict(id=id, ebene=ebene, kanton=kanton, gemeinde=gemeinde, dim=dim, thema=thema, titel=titel, doktyp=doktyp,
             dokstatus=dokstatus, rechtsstatus=rechtsstatus, herausgeber=herausgeber, url=url, bezugsjahr=bezugsjahr,
             relevanz=relevanz, kennzahl=kennzahl, methode=methode, vergleich=vergleich, confidence=confidence,
             datenluecke=datenluecke, verbindung=verbindung, sprint2=sprint2, fundstelle=fundstelle,
             pruefnachweis=pruefnachweis, hinweis=hinweis, herkunft=herkunft, weitere_dim=weitere_dim,
             erwartet=erwartet, veroeffentlicht=veroeffentlicht)
    if ort is not None:
        d["ort"] = ort
    if belege:
        d["belege"] = belege
    if anfrage:
        d["anfrage"] = anfrage
    if zustaendig:
        d["zustaendig"] = zustaendig
    return {k: v for k, v in d.items() if v != "" or k in ("erwartet",)}

# ---------------------------------------------------------------- bestehende Zeilen
B = {}
def upd(id, **kw):
    B[id] = kw

upd("CH-C1-01", erwartet=[["Finanzstatistik"]], fundstelle="https://www.efv.admin.ch/")
upd("CH-C1-02", erwartet=[["Finanzstatistik"]])
upd("CH-C2-01", erwartet=[["Zivilgesetzbuch"]], rechtsstatus="Bundesgesetz (verbindlich)", bezugsjahr="SR 210, geltende Fassung")
upd("CH-C3-01", erwartet=[["Bundesverfassung"]], rechtsstatus="Bundesverfassung (verbindlich)", bezugsjahr="SR 101, geltende Fassung", weitere_dim="C5")
upd("CH-C4-01", erwartet=[["öffentliche Beschaffungswesen", "Beschaffungswesen"]], rechtsstatus="Bundesgesetz (verbindlich für Bundesbeschaffungen; Gemeinden: IVöB/kantonales Recht)", bezugsjahr="SR 172.056.1, geltende Fassung")
upd("CH-C5-01", erwartet=[["Bundesverfassung"]], rechtsstatus="Bundesverfassung (verbindlich)", bezugsjahr="SR 101, geltende Fassung", weitere_dim="C3",
    hinweis="Gleiche Quelle wie CH-C3-01; bewusst doppelt geführt (Zuordnung C5 politische Rechte).")
upd("UR-C1-01", erwartet=[["Gemeindefinanzstatistik", "Kennzahlen", "Gemeindefinanz"]])
upd("UR-C1-02", erwartet=[["Steuerstatistik", "Steuer"]])
upd("UR-C2-01", erwartet=[["Geo", "Uri"]], ort=["Uri", "geo.ur"], hinweis="Kartenportal (JavaScript); Inhaltsprüfung nur eingeschränkt möglich. Kein Eigentumsnachweis.")
upd("UR-C3-01", url="https://rechtsbuch.ur.ch/app/de/texts_of_law/1.1111", titel="Gemeindegesetz (GEG) des Kantons Uri, RB 1.1111",
    doktyp="Kantonales Gesetz", rechtsstatus="Kantonales Gesetz (verbindlich)", bezugsjahr="vom 21.5.2017; geltende Fassung",
    erwartet=[["Gemeindegesetz"]], ort=[], herkunft=SCHEMA,
    grund="Startseite der Rechtssammlung durch direkten Erlass ersetzt (Gemeindegesetz, RB 1.1111).")
upd("UR-C4-01", url="https://www.ur.ch/dienstleistungen/8444", titel="Kanton Uri: Submissionsrecht (IVöB 2019, in Kraft seit 1.6.2023)",
    doktyp="Behördeninformation", rechtsstatus="Information zu verbindlichem Recht", erwartet=[["Submission", "Beschaffung", "IVöB"]],
    grund="Allgemeine Startseite ur.ch durch themenspezifische Seite zum Beschaffungsrecht ersetzt.")
upd("UR-C5-01", url="https://rechtsbuch.ur.ch/app/de/texts_of_law/2.1201", titel="Gesetz über die geheimen Wahlen, Abstimmungen und die Volksrechte (WAVG), RB 2.1201",
    doktyp="Kantonales Gesetz", rechtsstatus="Kantonales Gesetz (verbindlich)", bezugsjahr="geltende Fassung; Revision hängig (Synopse 2026)",
    erwartet=[["Wahlen", "Abstimmungen"]], ort=[], herkunft=SCHEMA,
    grund="Startseite der Rechtssammlung durch direkten Erlass ersetzt (WAVG, RB 2.1201).")
upd("BL-C1-01", erwartet=[["Gemeindefinanzen", "Finanzausgleich", "Finanzen"]])
upd("BL-C1-02", erwartet=[["Rechnungslegung", "Excel"]])
upd("BL-C2-01", erwartet=[["GeoView", "Geo"]], ort=["BL", "Basel-Landschaft", "geoview"], hinweis="Kartenportal (JavaScript); kein Eigentumsnachweis.")
upd("BL-C3-01", url="https://bl.clex.ch/app/de/texts_of_law/180", titel="Gemeindegesetz (GemG) Basel-Landschaft, SGS 180",
    doktyp="Kantonales Gesetz", rechtsstatus="Kantonales Gesetz (verbindlich)", bezugsjahr="vom 28.5.1970; geltende Fassung",
    erwartet=[["Gemeinden", "Gemeindegesetz"]], ort=[], herkunft=WEB,
    grund="Startseite der Gesetzessammlung durch direkten Erlass ersetzt (Gemeindegesetz SGS 180).")
upd("BL-C4-01", erwartet=[["Gemeinden"]])
upd("BL-C5-01", url="https://bl.clex.ch/app/de/texts_of_law/120", titel="Gesetz über die politischen Rechte (GpR) Basel-Landschaft, SGS 120",
    doktyp="Kantonales Gesetz", rechtsstatus="Kantonales Gesetz (verbindlich)", bezugsjahr="vom 7.9.1981; geltende Fassung",
    erwartet=[["politischen Rechte"]], ort=[], herkunft=SCHEMA,
    grund="Startseite der Gesetzessammlung durch direkten Erlass ersetzt (GpR SGS 120).")
upd("SG-C1-01", url="https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen/rechnungslegung--rmsg-.html",
    titel="Kanton St. Gallen, Amt für Gemeinden: Rechnungslegung (RMSG) / Gemeindefinanzen", doktyp="Behördeninformation",
    herausgeber="Kanton St. Gallen, Amt für Gemeinden", erwartet=[["Rechnungslegung", "RMSG"]],
    grund="Herausgeber «Kanton St. Gallen» passte nicht zum EFV-Bundeslink (Dublette zu CH-C1-01); durch kantonale Fundstelle ersetzt.")
upd("SG-C2-01", erwartet=[["geoportal"]], ort=[], hinweis="Kartenportal (JavaScript); kein Eigentumsnachweis.")
upd("SG-C3-01", url="https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/151.2", titel="Gemeindegesetz (GG) St. Gallen, sGS 151.2",
    doktyp="Kantonales Gesetz", rechtsstatus="Kantonales Gesetz (verbindlich)", bezugsjahr="vom 21.4.2009; geltende Fassung",
    erwartet=[["Gemeindegesetz", "Gemeinden"]], ort=[], herkunft=SCHEMA, weitere_dim="C1",
    grund="Startseite der Gesetzessammlung durch direkten Erlass ersetzt (Gemeindegesetz sGS 151.2).")
upd("SG-C4-01", erwartet=[["St.Gallen", "St. Gallen"]])
upd("SG-C5-01", url="https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/125.1", titel="Gesetz über Referendum und Initiative (RIG) St. Gallen, sGS 125.1",
    doktyp="Kantonales Gesetz", rechtsstatus="Kantonales Gesetz (verbindlich)", bezugsjahr="geltende Fassung",
    erwartet=[["Referendum"]], ort=[], herkunft=SCHEMA,
    grund="Startseite der Gesetzessammlung durch direkten Erlass ersetzt (RIG sGS 125.1).")
upd("SEE-C1-01", erwartet=[["Gemeindeversammlung"]], fundstelle="https://www.seelisberg.ch/", hinweis="Direkte Dokumente: SEE-C1-02 bis SEE-C1-05.")
upd("SEE-C2-01", url="https://www.seelisberg.ch/files/pdf/ERLUTE1.PDF",
    titel="Teilrevision Nutzungsplanung und Quartiergestaltungsplanung «Sonnenberg» – Erläuterungsbericht nach Art. 47 RPV (öffentliche Auflage)",
    doktyp="Planungsbericht", dokstatus="Direktes Dokument", rechtsstatus="Planungsbericht (orientierend)",
    relevanz="Planungsgrundlage für das Entwicklungsgebiet Sonnenberg. Kein Nachweis kommunalen Grundeigentums oder eines Baurechts: «Baurecht», «775» und «Erwerb» kommen im Dokumenttext nicht vor (automatische Volltextsuche).",
    erwartet=[["Sonnenberg"], ["Nutzungsplanung"]], belege=["Baurecht", "775", "Erwerb", "Halter", "Grundeigentümer"], confidence="Niedrig", fundstelle="https://www.seelisberg.ch/",
    pruefnachweis="Belegt das Planungsverfahren Sonnenberg (Teilrevision NUP/QGP); belegt kein kommunales Grundeigentum.",
    hinweis="Eine Suchmaschinen-Zusammenfassung nannte einen Erwerb von Parzelle 775 mit Baurecht – im Dokument nicht bestätigt, daher nicht übernommen. Ebenso unbestätigter Sekundärhinweis auf eine Projektbeteiligung der Halter AG: Belegstellen prüfen; allfällige Interessenbindung bei der Auswertung offenlegen. Kein Liegenschaftsverzeichnis öffentlich.",
    grund="Startseite durch direktes Dokument zu Grundeigentum/Baurecht ersetzt.")
upd("SEE-C3-01", erwartet=[["Kommission", "Behörden"]])
upd("SEE-C4-01", erwartet=[["Kommission", "Behörden"]])
upd("SEE-C5-01", erwartet=[["Gemeindeversammlung"]])
upd("MUE-C1-01", erwartet=[["Finanzplan"]])
upd("MUE-C1-02", url="https://www.muenchenstein.ch/publikationen/621658", titel="Bericht zur Jahresrechnung 2025 der Einwohnergemeinde Münchenstein",
    doktyp="Jahresrechnung", dokstatus="Publikationsseite mit PDF", rechtsstatus="Beschlossene Jahresrechnung (Gemeindeversammlung 15.6.2026)",
    bezugsjahr="2025", erwartet=[["Jahresrechnung 2025"]], confidence="Mittel",
    grund="Startseite durch Publikationsseite der Jahresrechnung 2025 ersetzt.")
upd("MUE-C2-01", url="https://www.muenchenstein.ch/_docn/1059619/2015.03.16_Ratschlag_Homepage.pdf",
    titel="Ratschlag Gemeindeversammlung 16.3.2015 (Landverkauf Parzelle 799; Grundsätze aktive Landpolitik / Baurecht)",
    doktyp="Ratschlag / Vorlage", dokstatus="Direktes Dokument", rechtsstatus="Beschlussvorlage (historisch)", bezugsjahr="2015",
    relevanz="Dokumentiert Grundsätze der kommunalen Landpolitik (Verkauf vs. Baurecht); historische Grundlage",
    erwartet=[["Ratschlag"], ["Baurecht"]], belege=["Baurecht", "Landpolitik"], confidence="Mittel",
    hinweis="Historisches Dokument (2015); aktuelle Liegenschaftsstrategie nicht öffentlich gefunden.",
    grund="Startseite durch direktes Dokument zur Landpolitik ersetzt.")
upd("MUE-C3-01", url="https://www.muenchenstein.ch/_docn/2430218/20180713_Gemeindeordnung_Stand_01.01.2013_publiziert_sw.pdf",
    titel="Gemeindeordnung der Einwohnergemeinde Münchenstein (Stand 1.1.2013)", doktyp="Gemeindeordnung", dokstatus="Direktes Dokument",
    rechtsstatus="Kommunales Recht (verbindlich)", bezugsjahr="vom 13.9.1999, Stand 1.1.2013", weitere_dim="C5",
    erwartet=[["Gemeindeordnung"], ["Gemeindekommission", "Gemeinderat"]], confidence="Hoch",
    fundstelle="https://www.muenchenstein.ch/reglemente/7140",
    hinweis="Prüfen, ob neuere Fassung existiert (Einwohnerrat-Diskussion).",
    grund="Startseite durch Gemeindeordnung ersetzt.")
upd("MUE-C4-01", url="https://www.muenchenstein.ch/organisationuorganigramm", titel="Gemeinde Münchenstein: Organisation und Organigramm der Verwaltung",
    doktyp="Organigramm / Webseite", dokstatus="Webseite", rechtsstatus="Information", erwartet=[["Organigramm", "Organisation"]],
    confidence="Mittel", grund="Startseite durch Organigrammseite ersetzt.")
upd("MUE-C5-01", url="https://www.muenchenstein.ch/legislaturziele", titel="Legislaturziele 2024–2028 des Gemeinderats Münchenstein",
    doktyp="Legislaturprogramm", dokstatus="Webseite", rechtsstatus="Politische Zielsetzung (behördenverbindlich, nicht rechtsverbindlich)",
    bezugsjahr="2024–2028", erwartet=[["Legislatur"]], confidence="Mittel",
    grund="Startseite durch Legislaturziele ersetzt.")
upd("WIL-C1-01", erwartet=[["Finanzen"]])
upd("WIL-C1-02", erwartet=[["Jahresrechnung", "Rechnung"]])
upd("WIL-C2-01", url="https://www.stadtwil.ch/topics/stadt-politik-und-recht/abstimmungen-und-wahlen/vergangene-abstimmungen/2024-vergangene-abstimmungen-und-wahlen/24-11-2024-eidgenoessische-kantonale-und-kommunale-abstimmungen-sowie-2-wahlgang-kommunale-erneuerungswahlen/nachtrag-iv-zur-gemeindeordnung",
    titel="Nachtrag IV zur Gemeindeordnung (Finanzbefugnisse Liegenschaftsgeschäfte im Finanzvermögen) – kommunale Abstimmung 24.11.2024",
    doktyp="Abstimmungsseite / Resultat", dokstatus="Webseite", rechtsstatus="Volksentscheid (Ergebnis auf Seite prüfen)", bezugsjahr="2024",
    relevanz="Kompetenzordnung für aktive Bodenpolitik (Kauf/Verkauf im Finanzvermögen) und Volksentscheid dazu", erwartet=[["Nachtrag IV"]],
    confidence="Mittel", herkunft=DISC, weitere_dim="C5",
    fundstelle="https://www.stadtwil.ch/topics/stadt-politik-und-recht/abstimmungen-und-wahlen/vorlagen/kommunale-vorlagen/22-11-2024-nachtrag-iv-zur-gemeindeordnung",
    hinweis="Zuerst gefundener Bericht (stadtwil.ch/_doc/4801870) liefert HTTP 404 (CMS-Umstellung).",
    grund="Geschäftsregister-Startseite durch direktes Dokument zur Bodenpolitik ersetzt.")
upd("WIL-C3-01", url="https://www.stadtwil.ch/topics/stadt-politik-und-recht/rechtssammlung-1", titel="Stadt Wil: Rechtssammlung (Gemeindeordnung, Beteiligungsreglement, TBW-Reglement u. a.)",
    doktyp="Rechtssammlung", dokstatus="Übersichtsseite", rechtsstatus="Kommunales Recht (Sammlung)", erwartet=[["Rechtssammlung"]], confidence="Mittel", herkunft=DISC,
    hinweis="Direktlinks zu Einzelerlassen siehe weitere C3-Zeilen; Suchtreffer /_doc/… liefern HTTP 404.",
    grund="Geschäftsregister-Startseite durch Rechtssammlung der Stadt ersetzt.")
upd("WIL-C4-01", url="https://www.stadtwil.ch/storage/ee8bae2cd080dda0bc77e69f99046109dc3e161b3498b17df7581cfe441bc612", titel="Geschäftsbericht der Stadt Wil 2025",
    doktyp="Geschäftsbericht", dokstatus="Direktes Dokument", rechtsstatus="Rechenschaftsbericht", bezugsjahr="2025", weitere_dim="C3, C5",
    erwartet=[["Geschäftsbericht"], ["2025"]], confidence="Hoch", herkunft=DISC, fundstelle="https://www.stadtwil.ch/topics/stadt-politik-und-recht/geschaeftsberichte",
    belege=["Organigramm", "Stellen", "Personal"], hinweis="Geschäftsberichte 2008–2024 auf der Fundstelle (Zeitreihe).",
    grund="Startseite durch aktuellen Geschäftsbericht ersetzt.")
upd("WIL-C5-01", url="https://www.stadtwil.ch/storage/55dcd744fbd978ce5601e42dc48a7b53cdfe1082b7fecb9c647e6dadc8abf9c7",
    titel="Legislaturplanung 2025–2028 «wil sind wir» – Bericht an das Stadtparlament", doktyp="Legislaturprogramm", dokstatus="Direktes Dokument",
    rechtsstatus="Politische Zielsetzung", bezugsjahr="2025–2028", erwartet=[["Legislatur"]], confidence="Mittel",
    grund="Geschäftsregister-Startseite durch Legislaturplanung ersetzt.")

# ---------------------------------------------------------------- neue Quellen
N = []
a = N.append
# Bund
a(src("CH-C1-03", "C1", "Finanzstatistik Methode", "EFV: Methoden der Finanzstatistik (FS-Modell, HRM2-Zuordnung)", "Methodik", "Methodische Grundlage",
      "Eidgenössische Finanzverwaltung (EFV)", "https://www.efv.admin.ch/de/methoden-finanzstatistik",
      [["Methode"], ["Finanzstatistik"]], dokstatus="Webseite", herkunft=DISC, fundstelle="https://www.efv.admin.ch/de/finanzstatistik-daten",
      hinweis="Früherer PDF-Link zum FS-Methodenband (efv.admin.ch/dam/…) liefert HTTP 502 (Website-Umbau); Methodenseite über EFV-Finanzstatistik ermittelt.", relevanz="Definitionen der Kennzahlen und HRM2-Abbildung für Vergleichbarkeit",
      kennzahl="Kennzahlendefinitionen", verbindung="C1", sprint2="Vergleichsregeln C1"))
a(src("CH-C1-04", "C1", "Finanzdaten Gemeinden", "EFV: Detaillierte Daten FS- und GFS-Modell (Open Government Data)", "Datensatz", "Datengrundlage",
      "EFV / opendata.swiss", "https://opendata.swiss/en/dataset/detaillierte-daten-fs-und-gfs-modell-standardauswertungen",
      [["FS"], ["GFS"]], relevanz="Maschinenlesbare Finanzdaten für Peer-Vergleich", kennzahl="Einnahmen, Ausgaben, Schulden", confidence="Mittel"))
a(src("CH-C2-02", "C2", "Raumplanung / Baulandmobilisierung", "Bundesgesetz über die Raumplanung (RPG), SR 700", "Bundesgesetz", "Bundesgesetz (verbindlich)",
      "Bund", "https://www.fedlex.admin.ch/eli/cc/1979/1573_1573_1573/de", [["Raumplanung"]], bezugsjahr="SR 700, geltende Fassung",
      relevanz="Art. 15a RPG: Förderung der Verfügbarkeit von Bauland; Mehrwertausgleich Art. 5", kennzahl="Bauverpflichtung, Mehrwertabgabe",
      herkunft="ELI-Permalink Fedlex; Identität per Fedlex-SPARQL geprüft", verbindung="B; Q1"))
a(src("CH-C4-02", "C4", "Gemeindekennzahlen", "BFS: Regionalporträts – Kennzahlen aller Gemeinden (Datensatz)", "Datensatz", "Datengrundlage", "Bundesamt für Statistik (BFS)",
      "https://ckan.opendata.swiss/dataset/regionalportrats-2021-kennzahlen-aller-gemeinden", [["Regionalporträts", "Regionalportraits", "Portraits régionaux"]],
      bezugsjahr="2021 (neuere Ausgabe prüfen)", relevanz="Strukturdaten (Einwohner, Fläche) zur Bildung der Grössenklassen", vergleich="Grössenklasse",
      confidence="Mittel", hinweis="Ausgabe 2021; aktuelle Ausgabe beim BFS prüfen.", weitere_dim="C1"))
# Uri
a(src("UR-C1-03", "C1", "Finanzkennzahlen Gemeinden", "Kennzahlen Einwohnergemeinden Uri 2025 (Finanzkontrolle)", "Statistik / Bericht", "Datengrundlage",
      "Kanton Uri, Finanzkontrolle", "https://www.ur.ch/_doc/451636", [["Kennzahlen"], ["Seelisberg"]], bezugsjahr="Rechnungsjahr 2025 (publ. 2026)",
      relevanz="Kennzahlen je Urner Gemeinde inkl. Seelisberg (Selbstfinanzierung, Kapitaldienst)", kennzahl="Selbstfinanzierungsanteil, Kapitaldienstanteil, Steuern/Kopf",
      fundstelle="https://www.ur.ch/publikationen/6680", verbindung="A1; C1", sprint2="Finanztragfähigkeit Seelisberg im Kantonsvergleich"))
a(src("UR-C1-04", "C1", "Finanzkennzahlen Gemeinden", "Kennzahlen Einwohnergemeinden Uri 2024 (Finanzkontrolle)", "Statistik / Bericht", "Datengrundlage",
      "Kanton Uri, Finanzkontrolle", "https://www.ur.ch/_doc/420775", [["Kennzahlen"], ["Seelisberg"]], bezugsjahr="Rechnungsjahr 2024",
      relevanz="Vorjahreswerte für Zeitreihe", kennzahl="wie UR-C1-03", fundstelle="https://www.ur.ch/publikationen/6680"))
a(src("UR-C1-05", "C1", "Rechnungslegung Gemeinden", "Reglement über das Rechnungswesen der Einwohnergemeinden (RRE), RB 3.2115", "Kantonales Reglement",
      "Kantonales Recht (verbindlich)", "Regierungsrat Uri", "https://rechtsbuch.ur.ch/api/de/versions/776/pdf_file", [["Rechnungswesen"], ["Einwohnergemeinden"]],
      bezugsjahr="Version 776 (Stand prüfen)", relevanz="Rechtsgrundlage HRM2 und kantonale Finanzaufsicht über Gemeinden (Uri kennt kein separates FHGG)",
      fundstelle="https://www.ur.ch/dienstleistungen/3150", ort=[], hinweis="Versions-PDF: prüfen, ob dies die geltende Fassung ist."))
a(src("UR-C1-06", "C1", "Finanzausgleich", "Gesetz über den Finanz- und Lastenausgleich zwischen dem Kanton und den Gemeinden (FiLaG), RB 3.2131",
      "Kantonales Gesetz", "Kantonales Recht (verbindlich)", "Kanton Uri", "https://rechtsbuch.ur.ch/app/de/texts_of_law/3.2131", [["Lastenausgleich"]],
      bezugsjahr="geltende Fassung", relevanz="Art. 22: Sonderbeitrag an Seelisberg (Abgeschiedenheit); Ressourcen- und Lastenausgleich", ort=[], herkunft=SCHEMA,
      kennzahl="Ausgleichszahlungen"))
a(src("UR-C1-07", "C1", "Finanzausgleich", "Finanz- und Lastenausgleich (FiLa) 2025 – Berechnung je Gemeinde", "Berechnungstabelle", "Datengrundlage",
      "Kanton Uri, Finanzdirektion", "https://www.ur.ch/_docn/426685/Berechnung_FiLa_2025.pdf", [["2025"], ["Seelisberg"]], bezugsjahr="2025",
      relevanz="Höhe der Ausgleichszahlungen an Seelisberg", kennzahl="Ressourcenausgleich, Lastenausgleich CHF"))
a(src("UR-C2-02", "C2", "Raumplanung / Baulandmobilisierung", "Planungs- und Baugesetz (PBG) des Kantons Uri, RB 40.1111", "Kantonales Gesetz", "Kantonales Recht (verbindlich)",
      "Kanton Uri", "https://rechtsbuch.ur.ch/app/de/texts_of_law/40.1111", [["Planungs", "Baugesetz"]], bezugsjahr="geltende Fassung",
      relevanz="Bauverpflichtung/Baulandmobilisierung, Mehrwertausgleich", ort=[], verbindung="B; Q1"))
a(src("UR-C2-03", "C2", "Bauland", "Kanton Uri: Baulanddatenbank (unbebaute Bauzonen, Raum+)", "Datenbank / Webseite", "Information", "Kanton Uri, Amt für Raumentwicklung",
      "https://www.ur.ch/dienstleistungen/4297", [["Bauland"]], confidence="Mittel", dokstatus="Webseite",
      relevanz="Unüberbaute Bauzonenreserven; kein Nachweis kommunalen Eigentums"))
a(src("UR-C3-02", "C3", "Kantonsverfassung", "Verfassung des Kantons Uri, RB 1.1101", "Kantonsverfassung", "Kantonales Recht (verbindlich)", "Kanton Uri",
      "https://rechtsbuch.ur.ch/app/de/texts_of_law/1.1101", [["Verfassung"]], bezugsjahr="vom 28.10.1984; geltende Fassung",
      relevanz="Gemeindeautonomie; Art. 58 Finanzplanung der Gemeinden; Art. 110 Rechtsetzung Gemeinden", ort=[], herkunft=SCHEMA, weitere_dim="C1, C5"))
a(src("UR-C4-02", "C4", "Beschaffung", "Interkantonale Vereinbarung über das öffentliche Beschaffungswesen (IVöB 2019), RB 3.3111", "Interkantonales Recht",
      "Interkantonales Recht (verbindlich)", "Kanton Uri", "https://rechtsbuch.ur.ch/app/de/texts_of_law/3.3111", [["Beschaffungswesen"]],
      relevanz="Beschaffungsrecht für Gemeinden (Schwellenwerte, Verfahren)", ort=[], herkunft=SCHEMA))
# Basel-Landschaft
a(src("BL-C1-03", "C1", "Rechnungslegung Gemeinden", "Kanton BL: Gemeindefinanzen (Rechtsgrundlagen, Finanzausgleich, Rechnungslegung)", "Behördeninformation", "Information",
      "Kanton Basel-Landschaft, Finanz- und Kirchendirektion", "https://www.baselland.ch/politik-und-behorden/gemeinden/gemeindefinanzen", [["Gemeindefinanzen"]],
      confidence="Mittel", dokstatus="Webseite", relevanz="Einstieg zu Finanzhandbuch, Rechtsgrundlagen und Finanzausgleich"))
a(src("BL-C1-05", "C1", "Finanzstatistik Gemeinden", "Statistisches Amt BL: Webartikel Gemeindefinanzen 2023 (18.9.2024)", "Statistischer Bericht", "Information",
      "Statistisches Amt Basel-Landschaft", "https://www.baselland.ch/politik-und-behorden/direktionen/finanz-und-kirchendirektion/daten-statistik/abteilung-statistik/publikationen-und-statistiken/finanzen-und-steuern/webartikel-vom-18-09-2024-gemeindefinanzen-2023",
      [["Gemeindefinanzen"], ["2023"]], bezugsjahr="2023", relevanz="Kantonaler Überblick Ergebnis/Eigenkapital der Gemeinden", confidence="Mittel", dokstatus="Webseite"))
a(src("BL-C1-06", "C1", "Finanzausgleich", "Finanzausgleichsgesetz (FAG) Basel-Landschaft, SGS 185", "Kantonales Gesetz", "Kantonales Recht (verbindlich)", "Kanton Basel-Landschaft",
      "https://bl.clex.ch/app/de/texts_of_law/185", [["Finanzausgleich"]], relevanz="Ressourcen- und Lastenausgleich; Münchenstein als Geber/Nehmer prüfen", ort=[], herkunft=SCHEMA))
a(src("BL-C2-02", "C2", "Raumplanung / Baulandmobilisierung", "Raumplanungs- und Baugesetz (RBG) Basel-Landschaft, SGS 400", "Kantonales Gesetz", "Kantonales Recht (verbindlich)",
      "Kanton Basel-Landschaft", "https://bl.clex.ch/app/de/texts_of_law/400", [["Raumplanungs", "Baugesetz"]], bezugsjahr="vom 8.1.1998; geltende Fassung",
      relevanz="Mehrwertabgabe, Quartierplanung, Mitwirkung § 7 RBG", ort=[], verbindung="B; Q1", weitere_dim="C5"))
a(src("BL-C4-02", "C4", "Beschaffung", "Verordnung zum Einführungsgesetz zur IVöB (Vo EG IVöB) Basel-Landschaft, SGS 420.11", "Kantonale Verordnung",
      "Kantonales Recht (verbindlich)", "Kanton Basel-Landschaft", "https://bl.clex.ch/app/de/texts_of_law/420.11", [["Beschaffung"]], ort=[], herkunft=SCHEMA,
      relevanz="Beschaffungsrecht für Gemeinden ab 1.1.2024"))
a(src("BL-C3-02", "C3", "Regionale Kooperation", "Medienmitteilung Kanton BL: Birsstadt erhält den Wakkerpreis (Verein Birsstadt, Raumkonzept Birsstadt 2035)", "Medienmitteilung", "Information",
      "Kanton Basel-Landschaft, Bau- und Umweltschutzdirektion", "https://www.baselland.ch/politik-und-behorden/direktionen/bau-und-umweltschutzdirektion/medienmitteilungen/ausgezeichnete-agglomeration-birsstadt-erhaelt-den-wakkerpreis",
      [["Birsstadt"]], ort=["Münchenstein", "Birsstadt"], confidence="Mittel", relevanz="Belegt interkommunale Kooperation Birsstadt (10 Gemeinden inkl. Münchenstein)", dokstatus="Webseite"))
# Seelisberg
a(src("SEE-C1-02", "C1", "Budget / Finanzplan", "Einladung Gemeindeversammlung November 2025: Traktanden und Botschaften (Budget 2026, Finanzplan 2027–2032, Leitbild)",
      "Botschaft / Vorlage", "Beschlussvorlage", "Gemeinde Seelisberg", "https://www.seelisberg.ch/files/pdf/Druckvorlage2_Original_Versammlung-Nov2025_Traktanden-und-Botschaften-gesamt.pdf",
      [["Budget"], ["2026"]], bezugsjahr="Budget 2026; Finanzplan 2027–2032", fundstelle="https://www.seelisberg.ch/politik/gemeindeversammlung",
      relevanz="Budget 2026, Nettoinvestitionen, Steuerfuss, Finanzplan; Grundlage C1", belege=["Steuerfuss", "Finanzplan", "Nettoinvestition"], kennzahl="Aufwand/Ertrag, Nettoinvestitionen, Steuerfuss", weitere_dim="C5",
      verbindung="A1; C1", sprint2="Finanztragfähigkeit"))
a(src("SEE-C2-02", "C2", "Bau- und Zonenordnung", "Bau- und Zonenordnung Seelisberg (BZO)", "Kommunales Reglement", "Kommunales Recht (verbindlich)", "Gemeinde Seelisberg",
      "https://www.seelisberg.ch/files/pdf/Bau-und-Zonenordnung-Seelisberg.pdf", [["Zonenordnung", "Bau- und Zonen"]], relevanz="Zonen und Bauvorschriften; Q-Bezug; kein Eigentumsnachweis",
      verbindung="B; Q1"))
a(src("SEE-C2-03", "C2", "Siedlungsentwicklung", "Siedlungsleitbild Seelisberg (Genehmigungsexemplar, 5.10.2022)", "Leitbild / Bericht", "Behördenverbindliche Planung",
      "Gemeinderat Seelisberg", "https://www.seelisberg.ch/files/pdf/8_20221005_Bericht_Siedlungsleitbild_Genehmigungsexemplar.pdf", [["Siedlungsleitbild"]],
      bezugsjahr="2022", relevanz="Strategische Entwicklungsgebiete (Sonnenberg, Chilendorf); Bodenpolitik-Absichten", weitere_dim="C5", verbindung="B"))
a(src("SEE-C2-04", "C2", "Nutzungsplanung", "Seelisberg: Teilrevision Nutzungsplanung – Erläuterungsbericht (26.5.2023)", "Planungsbericht", "Planungsbericht",
      "Gemeinde Seelisberg", "https://www.seelisberg.ch/files/pdf/20230526_Erl%C3%A4uterungsbericht.pdf", [["Nutzungsplanung"]], bezugsjahr="2023",
      relevanz="Planerische Flächenverfügbarkeit (≠ Eigentum)", verbindung="B", confidence="Mittel"))
a(src("SEE-C3-02", "C3", "Gemeindeordnung", "Gemeindeordnung der Einwohnergemeinde Seelisberg", "Gemeindeordnung", "Kommunales Recht (verbindlich)", "Gemeinde Seelisberg",
      "https://www.seelisberg.ch/files/pdf/Gemeindeordnung.pdf", [["Gemeindeordnung"]], fundstelle="https://www.seelisberg.ch/politik/rechtssammlung", herkunft=DISC,
      weitere_dim="C1, C5", relevanz="Zuständigkeiten Gemeindeversammlung/Gemeinderat, Finanzkompetenzen, Zusammenarbeit", belege=["Zweckverband", "Zusammenarbeit", "Finanzbefugnis", "Kredit"],
      hinweis="Fassungsdatum im Dokument prüfen (zitiert als 27.11.2009)."))
a(src("SEE-C5-08", "C5", "Verfahren Gemeindeversammlung", "Verordnung über das Verfahren an der Gemeindeversammlung Seelisberg", "Kommunale Verordnung", "Kommunales Recht (verbindlich)",
      "Gemeinde Seelisberg", "https://www.seelisberg.ch/files/pdf/Verordnung_%C3%BCber_das_Verfahren_an_der_Gemeindeversammlung.pdf", [["Gemeindeversammlung"], ["Verfahren"]],
      fundstelle="https://www.seelisberg.ch/politik/rechtssammlung", herkunft=DISC, relevanz="Entscheidungsverfahren, Antragsrechte der Stimmberechtigten"))
a(src("SEE-C4-03", "C4", "Personal", "Verordnung über das Personal der Gemeinde Seelisberg", "Kommunale Verordnung", "Kommunales Recht (verbindlich)", "Gemeinde Seelisberg",
      "https://www.seelisberg.ch/files/pdf/Verordnung_%C3%BCber_das_Personal.pdf", [["Personal"]], fundstelle="https://www.seelisberg.ch/politik/rechtssammlung", herkunft=DISC,
      relevanz="Anstellungsrahmen und Zuständigkeiten im Personalwesen (keine Aussage zu Kapazität)"))
a(src("SEE-C4-04", "C4", "Behördenorganisation", "Verordnung über das Verfahren in den Behörden der Gemeinde Seelisberg", "Kommunale Verordnung", "Kommunales Recht (verbindlich)", "Gemeinde Seelisberg",
      "https://www.seelisberg.ch/files/pdf/Verordnung_%C3%BCber_das_Verfahren_in_den_Beh%C3%B6rden.pdf", [["Verfahren"], ["Behörde"]], fundstelle="https://www.seelisberg.ch/politik/rechtssammlung", herkunft=DISC,
      weitere_dim="C3", relevanz="Arbeitsweise und Beschlussfassung von Gemeinderat und Kommissionen"))
a(src("SEE-C4-02", "C4", "Verwaltungsorganisation", "Gemeinde Seelisberg: Personal der Gemeindeverwaltung", "Webseite", "Information", "Gemeinde Seelisberg",
      "https://www.seelisberg.ch/personal", [["Personal", "Verwaltung"]], dokstatus="Webseite", confidence="Mittel",
      relevanz="Übersicht Verwaltungspersonal (Kapazitätsindikator, kein Kompetenznachweis)", anfrage="Ja"))
a(src("SEE-C5-02", "C5", "Leitbild", "Gemeinde Seelisberg: Neues Leitbild der Gemeinde (2025)", "Leitbild / Mitteilung", "Politische Zielsetzung", "Gemeinde Seelisberg",
      "https://www.seelisberg.ch/news/neues-leitbild-der-gemeinde-seelisberg", [["Leitbild"]], bezugsjahr="2025", dokstatus="Webseite", confidence="Mittel",
      relevanz="Mitwirkungsprozess (Workshop, Umfrage) und Themen; belegt keine Akzeptanz", fundstelle="https://www.seelisberg.ch/ueber-seelisberg/leitbild"))
a(src("SEE-C5-03", "C5", "Beschlussprotokoll", "Beschlussprotokoll Gemeindeversammlung Seelisberg vom 24.11.2023", "Protokoll", "Beschluss (verbindlich)", "Gemeinde Seelisberg",
      "https://www.seelisberg.ch/files/pdf/Beschlussprotokoll_GV_24.11.2023.pdf", [["Beschlussprotokoll", "Beschluss"]], bezugsjahr="2023",
      fundstelle="https://www.seelisberg.ch/politik/gemeindeversammlung", relevanz="Dokumentierte Beschlüsse/Wahlen", hinweis="Neuere Protokolle (28.5.2025, 28.11.2025) auf der Fundstelle gelistet; direkter Link per Discovery suchen."))
a(src("SEE-C1-03", "C1", "Jahresrechnung", "Jahresrechnung 2024 der Einwohnergemeinde Seelisberg", "Jahresrechnung", "Beschlossene Jahresrechnung (GV 28.5.2025)",
      "Gemeinde Seelisberg", "https://www.seelisberg.ch/files/pdf/JR2024_Gde-Seelisberg.pdf", [["Rechnung"], ["2024"]], bezugsjahr="2024", fundstelle="https://www.seelisberg.ch/politik/budget-rechnung", herkunft=DISC,
      relevanz="Erfolgsrechnung, Investitionsrechnung, Bilanz 2024", kennzahl="Selbstfinanzierungsgrad, Nettoinvestitionen, Nettoschuld", verbindung="A1; C1", sprint2="Finanztragfähigkeit",
      hinweis="Jahresrechnung 2025 (GV 29.5.2026) auf der Fundstelle nicht als PDF gefunden."))
a(src("SEE-C1-04", "C1", "Jahresrechnung", "Jahresrechnung 2023 der Einwohnergemeinde Seelisberg", "Jahresrechnung", "Beschlossene Jahresrechnung", "Gemeinde Seelisberg",
      "https://www.seelisberg.ch/files/pdf/Jahresrechnung_Gde-Seelisberg_2023.pdf", [["Rechnung"], ["2023"]], bezugsjahr="2023", fundstelle="https://www.seelisberg.ch/politik/budget-rechnung", herkunft=DISC,
      relevanz="Zeitreihe", confidence="Hoch"))
a(src("SEE-C1-05", "C1", "Budget", "Budget 2026 der Einwohnergemeinde Seelisberg (Erfolgsrechnung, Gesamtauflage)", "Budget", "Beschlossenes Budget (GV 28.11.2025)", "Gemeinde Seelisberg",
      "https://www.seelisberg.ch/files/pdf/Budget-ER-2026_Gesamtauflage_ohne-Bemerkungen_%C3%B6ffentlich.pdf", [["Budget"], ["2026"]], bezugsjahr="2026", fundstelle="https://www.seelisberg.ch/politik/budget-rechnung", herkunft=DISC))
a(src("SEE-C5-04", "C5", "Beschlussprotokoll", "Beschlussprotokoll Gemeindeversammlung Seelisberg vom 28.11.2025", "Protokoll", "Beschluss (verbindlich)", "Gemeinde Seelisberg",
      "https://www.seelisberg.ch/files/pdf/Beschlussprotokoll_GV_28.11.2025.pdf", [["Beschluss"]], bezugsjahr="2025", fundstelle="https://www.seelisberg.ch/politik/gemeindeversammlung", herkunft=DISC,
      relevanz="Beschlüsse Budget 2026, Leitbild, Verordnungen", weitere_dim="C1"))
a(src("SEE-C5-05", "C5", "Beschlussprotokoll", "Beschlussprotokoll Gemeindeversammlung Seelisberg vom 28.5.2025", "Protokoll", "Beschluss (verbindlich)", "Gemeinde Seelisberg",
      "https://www.seelisberg.ch/files/pdf/Beschlussprotokoll-GV-Mai-2025.pdf", [["Beschluss"], ["28. Mai 2025", "28.Mai2025"]], ort=["Seelisberg", "Seeusberg"], bezugsjahr="2025", fundstelle="https://www.seelisberg.ch/politik/gemeindeversammlung", herkunft=DISC,
      relevanz="Beschluss Jahresrechnung 2024 (44 Stimmberechtigte anwesend)", weitere_dim="C1",
      hinweis="Textextraktion liest den Kopf als «GEMEINDESEEUSBERG» (Schriftbild); Ortsabgleich toleriert diese Lesart."))
a(src("SEE-C5-06", "C5", "Leitbild", "Leitbild Seelisberg 2025 (Dokument)", "Leitbild", "Politische Zielsetzung", "Gemeinde Seelisberg",
      "https://www.seelisberg.ch/files/pdf/ORIGINAL-Leitbild-Seelisberg-2025-f%C3%BCr-Webseite.pdf", [["Leitbild"]], bezugsjahr="2025",
      fundstelle="https://www.seelisberg.ch/ueber-seelisberg/leitbild", herkunft=DISC, relevanz="Strategische Ziele (Wohnen, Tourismus, Finanzen); belegt keine Akzeptanz"))
a(src("SEE-C5-07", "C5", "Abstimmung", "Kommunale Abstimmung Seelisberg vom 8.3.2026 (Unterlage)", "Abstimmungsunterlage", "Information", "Gemeinde Seelisberg",
      "https://www.seelisberg.ch/files/pdf/kommunale-Abstimmung-Seelisberg_260308.pdf", [["Abstimmung"]], bezugsjahr="2026",
      fundstelle="https://www.seelisberg.ch/politik/abstimmungen-wahlen", herkunft=DISC, confidence="Mittel", relevanz="Kommunale Urnenentscheide (Legitimation)"))
# Münchenstein
a(src("MUE-C1-03", "C1", "Jahresrechnung", "Bericht zur Jahresrechnung 2024 der Einwohnergemeinde Münchenstein", "Jahresrechnung", "Beschlossene Jahresrechnung",
      "Gemeinde Münchenstein", "https://www.muenchenstein.ch/publikationen/556069", [["Jahresrechnung 2024"]], bezugsjahr="2024", dokstatus="Publikationsseite mit PDF",
      confidence="Mittel", relevanz="Ergebnis, Investitionen, Bilanz 2024 (Zeitreihe)"))
a(src("MUE-C1-04", "C1", "Budget", "Budget 2025 der Einwohnergemeinde Münchenstein", "Budget", "Beschlossenes Budget", "Gemeinde Münchenstein",
      "https://www.muenchenstein.ch/publikationen/523381", [["Budget 2025"]], bezugsjahr="2025", dokstatus="Publikationsseite mit PDF", confidence="Mittel"))
a(src("MUE-C1-05", "C1", "Budget / Finanzplan", "Gemeindeversammlung 8.12.2025: Budgetbericht 2026 und Bericht zum Aufgaben- und Finanzplan 2026–2030", "Sitzungsseite mit Unterlagen",
      "Beschlussvorlage", "Gemeinde Münchenstein", "https://www.muenchenstein.ch/sitzung/5729137", [["Budget"], ["2026"]], bezugsjahr="2026 / 2026–2030",
      dokstatus="Sitzungsseite mit PDF", confidence="Mittel", relevanz="Aktuellstes Budget und AFP inkl. Investitionsplanung", weitere_dim="C5"))
a(src("MUE-C1-06", "C1", "Finanzplanung", "Aufgaben- & Finanzplan der Einwohnergemeinde Münchenstein 2023–2027", "Finanzplan", "Planungsinstrument (Kenntnisnahme)",
      "Gemeinde Münchenstein", "https://www.muenchenstein.ch/_docn/4130681/Bericht_Aufgaben__Finanzplan_2023-2027_publiziert.pdf", [["Finanzplan"], ["2023"]],
      bezugsjahr="2023–2027 (historisch)", hinweis="Ältere Fassung; aktuelle AFP 2026–2030 siehe MUE-C1-05.", relevanz="Baurechtszinsen, Investitionen, Bilanzüberschuss-Prognose", belege=["Baurechtszins"]))
a(src("MUE-C2-02", "C2", "Zonenvorschriften / Mehrwertabgabe", "Zonenreglement Siedlung Münchenstein", "Kommunales Reglement", "Kommunales Recht (verbindlich)",
      "Gemeinde Münchenstein", "https://www.muenchenstein.ch/_docn/1199675/Zonenreglement_Siedlung.pdf", [["Zonenreglement", "Zonenvorschriften"]],
      fundstelle="https://www.muenchenstein.ch/reglemente/10743", relevanz="Mehrwertabgabe und Zonenordnung; kein Eigentumsnachweis", verbindung="B; Q1"))
a(src("MUE-C2-03", "C2", "Liegenschaftsverkäufe / Baurecht", "Ratschlag Gemeindeversammlung 12.3.2018 (Baurechtszinsen, Liegenschaftsverkäufe)", "Ratschlag / Vorlage",
      "Beschlussvorlage (historisch)", "Gemeinde Münchenstein", "https://www.muenchenstein.ch/_docn/1591897/2018.03.12_Ratschlag_GzD.pdf", [["Ratschlag"]],
      bezugsjahr="2018", confidence="Mittel", relevanz="Bedeutung von Baurechtszinsen und Landverkäufen für den Haushalt", weitere_dim="C1"))
a(src("MUE-C3-02", "C3", "Leistungsvereinbarung / Kooperation", "Ratschlag Gemeindeversammlung 15.6.2026 (u. a. Leistungsvereinbarung Spitex Birseck, Jahresrechnung 2025)",
      "Ratschlag / Vorlage", "Beschlussvorlage", "Gemeinde Münchenstein", "https://www.muenchenstein.ch/_docn/6998503/Ratschlag_Gemeindeversammlung_Montag,_15._Juni_2026.pdf",
      [["Ratschlag"], ["Spitex"]], bezugsjahr="2026", relevanz="Interkommunale Leistungsvereinbarung und Kostenteiler", weitere_dim="C1, C5"))
a(src("MUE-C4-02", "C4", "Personal", "Personalreglement der Einwohnergemeinde Münchenstein (Genehmigungsfassung 23.6.2022)", "Kommunales Reglement", "Kommunales Recht (verbindlich)",
      "Gemeinde Münchenstein", "https://www.muenchenstein.ch/_docn/3794018/Bereinigtes_Personalreglement_Genehmigungsfassung_per_23._Juni_2022.pdf", [["Personalreglement"]],
      bezugsjahr="in Kraft 1.1.2023", fundstelle="https://www.muenchenstein.ch/reglemente/402889"))
a(src("MUE-C4-03", "C4", "Verwaltungsorganisation", "Verwaltungs- und Organisationsreglement der Einwohnergemeinde Münchenstein", "Kommunales Reglement", "Kommunales Recht (verbindlich)",
      "Gemeinde Münchenstein", "https://www.muenchenstein.ch/reglemente/7208", [["Organisationsreglement", "Verwaltungs- und Organisation"]], bezugsjahr="Stand 1.1.2000",
      dokstatus="Reglementsseite mit PDF", confidence="Mittel", weitere_dim="C3"))
a(src("MUE-C5-02", "C5", "Protokoll", "Protokoll Gemeindeversammlung Münchenstein 13.6.2024", "Protokoll", "Beschluss (verbindlich)", "Gemeinde Münchenstein",
      "https://www.muenchenstein.ch/_docn/5478214/Protokoll_Gemeindeversammlung_13._Juni_2024_definitiv.pdf", [["Protokoll"], ["Gemeindeversammlung"]], bezugsjahr="2024",
      relevanz="Beschlüsse, Stimmverhalten, Bericht Legislaturziele 2020–2024"))
a(src("MUE-C5-03", "C5", "Beschlüsse", "Beschlüsse der Gemeindeversammlung vom 8.12.2025 (Budget 2026, AFP 2026–2030)", "Beschlussmitteilung", "Beschluss (verbindlich)", "Gemeinde Münchenstein",
      "https://www.muenchenstein.ch/politikinformationen/2666993", [["Gemeindeversammlung"], ["Budget"]], bezugsjahr="2025", dokstatus="Webseite", confidence="Mittel",
      relevanz="Beschlussstand, Teilnehmerzahl (Legitimationsindikator)", weitere_dim="C1"))
a(src("MUE-C5-04", "C5", "Mitwirkung", "Quartierplanung Spenglerpark – Mitwirkungsbericht (2019)", "Mitwirkungsbericht", "Bericht", "Gemeinde Münchenstein",
      "https://www.muenchenstein.ch/_docn/2359339/43037_Ber05_Mitwirkungsbericht_VerabschiedungGR_Unterschrieben_20190924_korr.pdf", [["Mitwirkung"], ["Spenglerpark"]],
      bezugsjahr="2019", relevanz="Mitwirkungspraxis und Einwendungen bei Arealentwicklung", weitere_dim="C2"))
a(src("MUE-C5-05", "C5", "Politische Gremien", "Gemeindekommission Münchenstein (§ 88 GemG)", "Behördenseite", "Information", "Gemeinde Münchenstein",
      "https://www.muenchenstein.ch/behoerden/2838", [["Gemeindekommission"]], dokstatus="Webseite", confidence="Mittel", weitere_dim="C3"))
# Wil
a(src("WIL-C1-03", "C1", "Jahresrechnung", "Jahresrechnung 2023 der Stadt Wil", "Jahresrechnung", "Beschlossene Jahresrechnung", "Stadt Wil",
      "https://www.stadtwil.ch/storage/46c11db85e782dc122cd9a61cc291529509f659681277125f8b019bce5a31b9c", [["Rechnung", "Jahresrechnung"], ["2023"]], bezugsjahr="2023",
      fundstelle="https://www.stadtwil.ch/topics/stadt-politik-und-recht/finanzen", herkunft=DISC, hinweis="Frühere Adresse /_docn/5050942/… liefert HTTP 404 (CMS-Umstellung); Link über Finanzseite der Stadt ermittelt."))
a(src("WIL-C1-04", "C1", "Jahresrechnung", "Jahresrechnung 2024 der Stadt Wil", "Jahresrechnung", "Beschlussvorlage",
      "Stadt Wil", "https://www.stadtwil.ch/storage/0f0d7ad95464bf91a72506e63d2aae1d5c18327f9bff4bf34b8400c36999b277", [["Rechnung", "Jahresrechnung"], ["2024"]], bezugsjahr="2024",
      fundstelle="https://www.stadtwil.ch/topics/stadt-politik-und-recht/finanzen", herkunft=DISC, hinweis="Frühere Adresse /_doc/5592973 liefert HTTP 404 (CMS-Umstellung); Link über Finanzseite der Stadt ermittelt."))
a(src("WIL-C1-05", "C1", "Jahresrechnung", "Rechnung 2025 Stadt Wil – Finanzbericht, Erfolgsrechnung, Bilanz, Anhang", "Jahresrechnung", "Beschlussvorlage",
      "Stadt Wil", "https://www.stadtwil.ch/storage/08902ff399818ccc0d53949607b2d0f6f8bf702c334e295d493c2fd842ba4079", [["2025"], ["Bilanz"]], bezugsjahr="2025",
      confidence="Mittel", hinweis="Zuordnung der Hash-URL stammt aus Suchzusammenfassung; nur Inhaltsprüfung belegt Identität."))
a(src("WIL-C1-06", "C1", "Finanzplanung", "Finanzplan 2026–2030 der Stadt Wil (Stadtrat 23.9.2025)", "Finanzplan", "Planungsinstrument", "Stadt Wil",
      "https://www.stadtwil.ch/storage/875d422378d72386aae96efa76356fbfa05e9a0e1e03f208fbbe599dea21021c", [["Finanzplan"], ["2030"]], bezugsjahr="2026–2030",
      fundstelle="https://www.stadtwil.ch/topics/stadt-politik-und-recht/finanzen"))
a(src("WIL-C1-07", "C1", "Investitionen", "Investitionsplan 2026–2030 der Stadt Wil", "Investitionsplan", "Planungsinstrument", "Stadt Wil",
      "https://www.stadtwil.ch/storage/c6097b5ae815fb81f14b4db7630b14d9452e3be1ae3cbddd9f8e28d9d0777c7f", [["Investitionsplan", "Investition"], ["2030"]], bezugsjahr="2026–2030",
      fundstelle="https://www.stadtwil.ch/topics/stadt-politik-und-recht/finanzen", herkunft=DISC, confidence="Hoch"))
a(src("WIL-C1-08", "C1", "Budget", "Budget 2026 der Stadt Wil", "Budget", "Beschlussvorlage", "Stadt Wil",
      "https://www.stadtwil.ch/storage/2ecd9e697734cc2262543c9da23828c2b6ad0129cf1654fcfa47f21ba113bf8a", [["Budget"], ["2026"]], bezugsjahr="2026",
      fundstelle="https://www.stadtwil.ch/topics/stadt-politik-und-recht/finanzen", herkunft=DISC, confidence="Hoch", hinweis="Steuerfuss-Referendum 2026 – Beschlussstand prüfen."))
a(src("WIL-C1-10", "C1", "Budget", "Budget 2027 der Stadt Wil", "Budget", "Vorlage (Beschluss Stadtparlament ausstehend/prüfen)", "Stadt Wil",
      "https://www.stadtwil.ch/storage/86c954451190b5683f4cea602b5746ce096ff6338c9f35fbea68172b58f684d1", [["Budget"], ["2027"]], bezugsjahr="2027",
      fundstelle="https://www.stadtwil.ch/topics/stadt-politik-und-recht/finanzen", herkunft=DISC, relevanz="Aktuellster Planungsstand Erfolgsrechnung/Investitionen", hinweis="Beschlussstand prüfen."))
a(src("WIL-C1-11", "C1", "Finanzplanung", "Finanzplan 2025–2029 der Stadt Wil (Vorjahresplan für Vergleich)", "Finanzplan", "Planungsinstrument", "Stadt Wil",
      "https://www.stadtwil.ch/storage/c7e05a885ee1a6860975358848101c3f21fe558650ccfc5ba12339d34d3232e9", [["Finanzplan"], ["2029"]], bezugsjahr="2025–2029 (historisch)",
      fundstelle="https://www.stadtwil.ch/topics/stadt-politik-und-recht/finanzen", herkunft=DISC, confidence="Mittel", relevanz="Plan-Ist-Vergleich der Planungsgüte"))
a(src("WIL-C1-09", "C1", "Beteiligungen / Rechnung", "Jahresrechnung 2025 Technische Betriebe Wil (TBW) – Bericht und Antrag", "Jahresrechnung Unternehmen", "Beschlussvorlage",
      "Stadt Wil / Technische Betriebe Wil", "https://www.stadtwil.ch/storage/9bf65acd52bfa75c91cc42760759e0ffc3a76d501e7d174c010444c290801cc2", [["Technische Betriebe"], ["2025"]],
      bezugsjahr="2025", confidence="Mittel", weitere_dim="C3", relevanz="Gewinnablieferung und Abgaben der TBW an die Stadt"))
a(src("WIL-C2-03", "C2", "Bodenpolitik", "Stadt Wil: aktive Bodenpolitik / Boden- und Immobilienstrategie", "Strategie / Bericht", "Strategie", "Stadt Wil",
      "https://www.stadtwil.ch/storage/1e396670eed23bbd41611d92ceaa476797bc97e16fde09c29197453c3b3bc320", [["Bodenpolitik", "Immobilien"]], confidence="Niedrig",
      hinweis="Unsichere Zuordnung (Suchzusammenfassung)."))
a(src("SG-C2-02", "C2", "Arealentwicklung", "WILWEST: Grundstücksgeschäft Kanton St. Gallen (Verkauf an Kanton Thurgau) – Kantonsratsvorlage", "Botschaft / Beschluss", "Beschluss (Volksabstimmung 2026)",
      "Kanton St. Gallen", "https://www.ratsinfo.sg.ch//media/documents/published/signed/8b158b37-2fff-4d5d-b018-ef035f08732e.pdf", [["WILWEST", "Wil West"]],
      ort=["Wil", "Münchwilen"], confidence="Mittel", relevanz="Kantonales Grundeigentum im Entwicklungsgebiet WILWEST (nicht städtisches Eigentum)", verbindung="B"))
a(src("SG-C2-03", "C2", "Raumplanung / Baulandmobilisierung", "Planungs- und Baugesetz (PBG) St. Gallen, sGS 731.1", "Kantonales Gesetz", "Kantonales Recht (verbindlich)",
      "Kanton St. Gallen", "https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/731.1", [["Planungs", "Baugesetz"]], ort=[], herkunft=SCHEMA,
      relevanz="Ortsplanungsrevision bis 2027, Bauverpflichtung, Mehrwertabgabe", verbindung="B; Q1"))
a(src("SG-C1-02", "C1", "Finanzausgleich", "Finanzausgleichsgesetz St. Gallen, sGS 813.1", "Kantonales Gesetz", "Kantonales Recht (verbindlich)", "Kanton St. Gallen",
      "https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/813.1", [["Finanzausgleich"]], ort=[], herkunft=SCHEMA))
a(src("SG-C1-03", "C1", "Rechnungslegung Gemeinden", "Verordnung über den Finanzhaushalt der Gemeinden (FHGV) St. Gallen, sGS 151.53", "Kantonale Verordnung", "Kantonales Recht (verbindlich)",
      "Kanton St. Gallen", "https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/151.53", [["Finanzhaushalt"]], ort=[], herkunft=SCHEMA))
a(src("SG-C4-02", "C4", "Beschaffung", "Einführungsgesetz zur IVöB St. Gallen, sGS 841.1", "Kantonales Gesetz", "Kantonales Recht (verbindlich)", "Kanton St. Gallen",
      "https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/841.1", [["Beschaffung"]], ort=[], herkunft=SCHEMA, fundstelle="https://www.sg.ch/recht/beschaffungswesen/neues_beschaffungsrecht_2023/"))
a(src("WIL-C3-04", "C3", "Agglomeration", "Prüfbericht des Bundes zum Agglomerationsprogramm Wil, 4. Generation (22.2.2023)", "Prüfbericht", "Bundesbeurteilung",
      "Bundesamt für Raumentwicklung (ARE)", "https://www.are.admin.ch/dam/de/sd-web/1LGAXN34JMxU/Pr%C3%BCfbericht%20Wil4G.pdf", [["Prüfbericht"], ["Agglomerationsprogramm"]],
      bezugsjahr="2023", relevanz="Regionale Trägerschaft und Umsetzungsreife (Regio Wil)", verbindung="B"))
a(src("WIL-C3-05", "C3", "Agglomeration", "Agglomerationsprogramm Wil 5. Generation – Flyer", "Informationsblatt", "Information", "Kanton St. Gallen / Regio Wil",
      "https://www.sg.ch/content/dam/sgch/bauen/raumentwicklung/agglomerationsprogramme/Wil%20Flyer%205G.pdf", [["Agglomerationsprogramm"]], bezugsjahr="2025", confidence="Mittel"))
a(src("WIL-C5-02", "C5", "Ortsplanung / Mitwirkung", "Richtplan Siedlung und Grün-/Freiraum – Planungsbericht inkl. Auszug Stadtentwicklungskonzept (31.3.2026)", "Planungsbericht",
      "Behördenverbindliche Planung (Entwurf)", "Stadt Wil", "https://www.stadtwil.ch/storage/533b0557b4e4988a6a4f9af13c0b789fec39837eef83d1e66cd1d3814dbe0acb",
      [["Richtplan"]], bezugsjahr="2026", confidence="Mittel", weitere_dim="C2", hinweis="Zuordnung der Hash-URL aus Suchzusammenfassung."))
a(src("WIL-C5-03", "C5", "Mitwirkung", "Ortsplanungsrevision Wil – Mitwirkung 2025", "Mitwirkungsunterlage", "Information", "Stadt Wil",
      "https://www.stadtwil.ch/storage/5d895f1e33cc1b2c352d7bdeb9d93dd5b2333fbff6a1793cd419f387dd4e1e28", [["Mitwirkung"]], bezugsjahr="2025", confidence="Niedrig",
      hinweis="Unsichere Zuordnung (Suchzusammenfassung)."))

# Gemeindeanfragen: präzisierte Fragen zu bestehenden Anfragen
A = {}
def anf(aid, frage, befund, bezug="", quellenstatus="", zust=""):
    A[aid] = {"Präzisierte Frage an die Gemeinde": frage, "Recherchebefund": befund}
    if bezug: A[aid]["Bezug Katalog-ID"] = bezug
    if quellenstatus: A[aid]["Quellenstatus (Recherche)"] = quellenstatus
    if zust: A[aid]["Zuständige Stelle (vermutet)"] = zust
NF, NUR = "Nicht öffentlich auffindbar", "Nur über Gemeindeanfrage erhältlich"
# Seelisberg A-SEE-01..08 (Reihenfolge der Ausgangsdatei)
anf("A-SEE-01", "Bitte stellen Sie die Jahresrechnung 2025 (inkl. Anhang und HRM2-Kennzahlen) zur Verfügung und bestätigen Sie, dass die online publizierten Rechnungen 2021–2024 vollständig sind.",
    "Jahresrechnungen 2020–2024 und Budgets 2020–2026 öffentlich (SEE-C1-03/04/05, weitere im Blatt Recherche-Kandidaten); Jahresrechnung 2025 nicht als PDF gefunden. Kennzahlen bei Finanzkontrolle Uri (UR-C1-03/04, vom Runner nicht erreichbar).", "SEE-C1-03, SEE-C1-04, SEE-C1-05, UR-C1-03", "", "Gemeindeschreiberei / Finanzverwaltung Seelisberg")
anf("A-SEE-02", "Bitte senden Sie den aktuellen Finanzplan 2027–2032 inkl. Investitionsliste und Angaben zu Eventualverpflichtungen (Bürgschaften, Garantien, Baurechtsverpflichtungen).",
    "Finanzplan 2027–2032 in GV-Botschaft Nov. 2025 erwähnt; Investitionsliste und Eventualverpflichtungen nicht öffentlich.", "SEE-C1-02", NUR, "Gemeinderat / Finanzverwaltung")
anf("A-SEE-03", "Welche Grundstücke (Parzellennummern) besitzt die Einwohnergemeinde im Verwaltungs- und Finanzvermögen? Bitte Liste mit Fläche, Zone und Nutzung.",
    "Kein Liegenschaftsverzeichnis öffentlich; kein kommunales Grundstücksgeschäft im Dokumenttext belegt (SEE-C2-01 nur Planungsverfahren Sonnenberg).", "SEE-C2-01", NF, "Gemeindeverwaltung / Bauverwaltung")
anf("A-SEE-04", "Bitte listen Sie bestehende und geplante Baurechte, Dienstbarkeiten und Kaufrechte der Gemeinde auf (Parzelle, Berechtigte, Laufzeit, Zins).",
    "Keine Baurechts- oder Dienstbarkeitsverträge öffentlich; ein in der Websuche erwähntes Baurecht (Parzelle 775) ist im Erläuterungsbericht nicht belegt.", "SEE-C2-01", NUR)
anf("A-SEE-05", "Bitte bestätigen Sie die geltende Fassung der Gemeindeordnung und senden Sie die Verordnung über die Zuständigkeiten im Finanzbereich sowie eine Liste der Zweckverbände/Leistungsvereinbarungen (z. B. ZAKU, Abwasser Uri, Schule).",
    "Gemeindeordnung online (SEE-C3-02, Rechtssammlung der Gemeinde); Mitgliedschaften in Zweckverbänden nicht belegt.", "SEE-C3-02", NF, "Gemeindeschreiberei")
anf("A-SEE-06", "Wie viele Stellenprozente stehen in Verwaltung und Bauverwaltung zur Verfügung? Welche Projekte werden extern (Mandate) gesteuert? Wie läuft eine Beschaffung ab (Zuständigkeit, Schwellen)?",
    "Personalseite (SEE-C4-02) zeigt Personen, keine Pensen; Restrukturierung der Verwaltung im Budget 2026 erwähnt.", "SEE-C4-01, SEE-C4-02, SEE-C4-03", NUR)
anf("A-SEE-07", "Bitte stellen Sie die Auswertung der Leitbild-Umfrage 2025 und Informationen zur Umsetzungsplanung des Leitbilds zur Verfügung.",
    "Leitbild 2025 (SEE-C5-06) und Beschlussprotokolle 2023–2025 (SEE-C5-03/04/05) öffentlich; Umfrageauswertung nicht.", "SEE-C5-04, SEE-C5-05, SEE-C5-06")
anf("A-SEE-08", "Welche Akteure (Korporation, Tourismus, Hotellerie, Grundeigentümer) sind für die Entwicklung massgebend und wie sind ihre Positionen bekannt?",
    "Keine öffentliche Akteursübersicht; nur indirekt aus Planungsberichten ableitbar.", "", NUR)
# Münchenstein A-MUE-01..08
anf("A-MUE-01", "Bitte bestätigen Sie, dass die publizierten Berichte zu den Jahresrechnungen 2021–2025 vollständig sind, und senden Sie die HRM2-Kennzahlen als Excel.",
    "Jahresrechnungen 2024 und 2025 als Publikationsseiten gefunden (MUE-C1-02, MUE-C1-03).", "MUE-C1-02, MUE-C1-03", "", "Abteilung Finanzen Münchenstein")
anf("A-MUE-02", "Bitte senden Sie die Investitionsplanung des AFP 2026–2030 als Excel und eine Liste der Eventualverpflichtungen.",
    "AFP 2026–2030 auf Sitzungsseite GV 8.12.2025 (MUE-C1-05); Eventualverpflichtungen nicht separat publiziert.", "MUE-C1-01, MUE-C1-05", "", "Abteilung Finanzen")
anf("A-MUE-03", "Bitte stellen Sie ein Verzeichnis der Grundstücke im Eigentum der Einwohnergemeinde (Finanz- und Verwaltungsvermögen) mit Parzellen-ID zur Verfügung.",
    "Landverkäufe und Baurechtszinsen in Ratschlägen dokumentiert (MUE-C2-01, MUE-C2-03); kein Verzeichnis öffentlich.", "MUE-C2-01, MUE-C2-03", NF, "Bauverwaltung / Liegenschaften")
anf("A-MUE-04", "Bitte listen Sie die Baurechtsverträge der Gemeinde (Parzelle, Baurechtsnehmer, Ablauf, Zins).",
    "Baurechtszinsen als Ertragsposition erwähnt; Verträge nicht öffentlich.", "MUE-C2-01", NUR)
anf("A-MUE-05", "Bitte senden Sie eine Übersicht der Zweckverbände, Leistungsvereinbarungen und Beteiligungen (u. a. Zweckverband Alter Birsstadt, Spitex Birseck, Verein Birsstadt).",
    "Einzelne Leistungsvereinbarungen in Ratschlägen (MUE-C3-02), Birsstadt-Kooperation (BL-C3-02); keine Gesamtübersicht.", "MUE-C3-01, MUE-C3-02, BL-C3-02", NF)
anf("A-MUE-06", "Wie viele Stellenprozente hat die Bauverwaltung, wie werden Entwicklungsprojekte organisiert (Projektleitung, externe Mandate), und welche Beschaffungsweisungen gelten?",
    "Organigramm (MUE-C4-01) und Personalreglement (MUE-C4-02) öffentlich; Pensen und Projektorganisation nicht.", "MUE-C4-01, MUE-C4-02", NUR)
anf("A-MUE-07", "Bitte bestätigen Sie den Stand der Legislaturziele 2024–2028 und des Leitbilds (2004/2011) und senden Sie Mitwirkungsberichte zur Zonenplanrevision Siedlung.",
    "Legislaturziele (MUE-C5-01) und Mitwirkungsbericht Spenglerpark (MUE-C5-04) gefunden; Leitbild-Volltext nicht.", "MUE-C5-01, MUE-C5-04")
anf("A-MUE-08", "Welche politischen Akteure und Interessengruppen sind für Areal- und Bodenentwicklung massgebend? Wie ist der Stand der Diskussion um einen Einwohnerrat?",
    "Einwohnerrat-Diskussion nur in Sekundärquelle (SRF) erwähnt; Ergebnis nicht gefunden.", "", NF)
# Wil A-WIL-01..08
anf("A-WIL-01", "Bitte bestätigen Sie die Fundstellen der Jahresrechnungen 2021–2025 und senden Sie die HRM2-Kennzahlen als Excel.",
    "Jahresrechnungen 2017–2025, Budgets 2019–2027, Finanz- und Investitionspläne öffentlich (WIL-C1-03/04/05/10/11 u. Recherche-Kandidaten).", "WIL-C1-03, WIL-C1-04, WIL-C1-05", "", "Finanzverwaltung Stadt Wil")
anf("A-WIL-02", "Bitte senden Sie den Investitionsplan 2026–2030 (bzw. 2025–2035) als Excel und eine Liste der Eventualverpflichtungen inkl. Beteiligungen (TBW, Thurcom, WISPAG).",
    "Finanzplan und Investitionsplan 2026–2030 öffentlich (WIL-C1-06/07); Eventualverpflichtungen und Beteiligungsrisiken nicht separat.", "WIL-C1-06, WIL-C1-07")
anf("A-WIL-03", "Bitte stellen Sie das Liegenschaftsverzeichnis der Stadt (Finanz- und Verwaltungsvermögen) mit Parzellen-ID zur Verfügung.",
    "Bodenpolitik-Dokument (WIL-C2-03) und Kompetenzordnung Nachtrag IV (WIL-C2-01) gefunden; kein Verzeichnis.", "WIL-C2-01, WIL-C2-03", NF, "Liegenschaften / Bauverwaltung Stadt Wil")
anf("A-WIL-04", "Bitte listen Sie Baurechte und Kaufrechte der Stadt (Parzelle, Berechtigte, Laufzeit, Zins).", "Nicht öffentlich.", "", NUR)
anf("A-WIL-05", "Bitte senden Sie die aktuellen Eignerstrategien und Leistungsvereinbarungen (TBW, Thurcom AG, WISPAG) sowie Unterlagen zur Regio Wil.",
    "Rechtssammlung der Stadt (WIL-C3-01) und Jahresrechnung TBW (WIL-C1-09) öffentlich; Eignerstrategien und Regio-Wil-Statuten nicht gefunden.", "WIL-C3-01, WIL-C1-09")
anf("A-WIL-06", "Bitte senden Sie das aktuelle Organigramm der Stadtverwaltung, den Stellenplan der Bereiche Bau/Stadtentwicklung und Angaben zur Projektorganisation (z. B. WILWEST, Ortsplanungsrevision).",
    "Geschäftsberichte bis 2025 öffentlich (WIL-C4-01); separates aktuelles Organigramm nicht gefunden.", "WIL-C4-01", NF)
anf("A-WIL-07", "Bitte senden Sie die Legislaturplanung 2025–2028, Mitwirkungsberichte zur Ortsplanungsrevision und den Stand des Budget-2026-Referendums.",
    "Legislaturplanung (WIL-C5-01) und Mitwirkungsunterlagen (WIL-C5-03) gefunden; Ergebnisse Mitwirkung nicht.", "WIL-C5-01, WIL-C5-03")
anf("A-WIL-08", "Welche Fraktionen/Akteure prägen Boden- und Arealfragen (WILWEST, Liegenschaftsgeschäfte), und welche Konflikte sind bekannt?",
    "Nur indirekt über Parlamentsprotokolle erschliessbar.", "", NUR)

NEU = [
    {"Anfrage-ID": "A-SEE-09", "Gemeinde": "Seelisberg", "C-Dimension": "C2, C3", "Benötigte Lieferung": "Rolle der Gemeinde im Projekt Sonnenberg (Grundeigentum, Verträge, Kostenbeteiligung)",
     "Warum nötig": "Einziges dokumentiertes kommunales Bodengeschäft; Trägerschaft und Risiken", "Priorität": "Hoch", "Status": "Offen",
     "Recherchebefund": "Nur Planungsverfahren öffentlich (SEE-C2-01); Eigentums- und Vertragsfragen nicht dokumentiert.", "Bezug Katalog-ID": "SEE-C2-01",
     "Quellenstatus (Recherche)": NUR, "Präzisierte Frage an die Gemeinde": "Besitzt die Gemeinde im Gebiet Sonnenberg Grundstücke oder plant sie Erwerb/Abgabe im Baurecht? Welche Verträge (Planung, Infrastruktur) bestehen, und welche Pflichten und Risiken übernimmt die Gemeinde?"},
    {"Anfrage-ID": "A-MUE-09", "Gemeinde": "Münchenstein", "C-Dimension": "C2", "Benötigte Lieferung": "Liegenschafts- bzw. Bodenstrategie (falls vorhanden) und Grundsätze zu Verkauf vs. Baurecht",
     "Warum nötig": "Steuerungswille Bodenpolitik", "Priorität": "Mittel", "Status": "Offen",
     "Recherchebefund": "Grundsätze nur in Ratschlag 2015 (MUE-C2-01); aktuelle Strategie nicht gefunden.", "Bezug Katalog-ID": "MUE-C2-01",
     "Quellenstatus (Recherche)": NF, "Präzisierte Frage an die Gemeinde": "Gibt es eine aktuelle Liegenschafts- oder Bodenstrategie des Gemeinderats? Gelten die Grundsätze von 2015 noch?"},
    {"Anfrage-ID": "A-WIL-09", "Gemeinde": "Wil", "C-Dimension": "C2", "Benötigte Lieferung": "Aktuelle Boden- und Immobilienstrategie; Stand Nachtrag IV Gemeindeordnung (Finanzbefugnisse Liegenschaften)",
     "Warum nötig": "Handlungsspielraum aktive Bodenpolitik", "Priorität": "Mittel", "Status": "Offen",
     "Recherchebefund": "Strategiedokument (WIL-C2-03) und Abstimmungsseite Nachtrag IV (WIL-C2-01) gefunden; Geltungsstand bestätigen lassen.", "Bezug Katalog-ID": "WIL-C2-01, WIL-C2-03",
     "Präzisierte Frage an die Gemeinde": "Welche Boden-/Immobilienstrategie gilt aktuell (Fassung, Beschlussdatum), und seit wann gilt Nachtrag IV zur Gemeindeordnung?"},
]

BERICHT = {
    "unsicherheiten": [
        "Inhaltsprüfung ist ein automatischer Schlüsselwort-Abgleich (Titel/erste Seiten). Sie belegt die Dokumentidentität, nicht die fachliche Eignung oder Vollständigkeit.",
        "Hash-Links der Stadt Wil (/storage/…) wurden über Suchmaschinen-Zusammenfassungen zugeordnet; massgeblich ist allein die Inhaltsprüfung des Runners.",
        "Kantonale Rechtssammlungen (LexWork: rechtsbuch.ur.ch, bl.clex.ch, gesetzessammlung.sg.ch) und Fedlex sind JavaScript-Anwendungen; die Identität wird über deren Daten-Schnittstellen geprüft. Fehlt diese, bleibt die Inhaltsprüfung «Offen».",
        "Planerische Flächenverfügbarkeit (Zonen, Bauland-Datenbanken) ist kein Nachweis kommunalen Grundeigentums. C2 bleibt ohne Liegenschaftsverzeichnisse der Gemeinden unbelegt.",
        "Organigramme und Reglemente belegen Strukturen, nicht Verwaltungskompetenz oder Kapazität (C4).",
        "Leitbilder, Mitwirkungsverfahren und Beschlüsse belegen keine politische Akzeptanz (C5); dazu sind Abstimmungsresultate und qualitative Befunde nötig.",
        "Seelisberg: Eine Suchmaschinen-Zusammenfassung schrieb dem Erläuterungsbericht Sonnenberg einen Parzellenerwerb mit Baurecht zu; die Volltextsuche fand dies nicht. Solche Aussagen wurden daher nicht übernommen. Ein unbestätigter Sekundärhinweis nennt eine Projektbeteiligung der Halter AG – vor der Auswertung klären und allfällige Interessenbindung offenlegen.",
        "Tragfähigkeit wurde bewusst nirgends eingestuft; die Schwellen in der Bewertungslogik sind noch nicht validiert.",
    ],
    "empfehlungen": [
        "Gemeindeanfragen mit Priorität «Hoch» zuerst versenden (C1-Zeitreihen, C2-Liegenschaftsverzeichnisse, C4-Stellenpläne).",
        "Blatt «Recherche-Kandidaten» sichten: direkte PDF-Links hinter Publikations- und Sitzungsseiten übernehmen (v. a. Münchenstein /publikationen/, Seelisberg Beschlussprotokolle 2025).",
        "C1: Kennzahlen (Selbstfinanzierungsgrad, Nettoschuld je Einwohner, Investitionsanteil) aus den bestätigten Jahresrechnungen extrahieren und Peer-Gruppe Kanton × Grössenklasse bilden (BFS-Regionalporträts).",
        "Kantonale Finanzstatistik St. Gallen (Finanzstatistik der politischen Gemeinden) als direkten Download ermitteln.",
        "Gemeindeordnung Seelisberg (2009) und Regio-Wil-Statuten bei den Gemeinden anfordern, da online nicht auffindbar.",
        "Optional Secret BRAVE_SEARCH_API_KEY hinterlegen, um die automatische Recherche um eine Such-API zu erweitern.",
    ],
}


VERWORFEN = [
    {"titel": "Gemeindefinanzen BL nach Rechnungsteil (opendata.swiss, Ressource und Datensatzseite)", "url": "https://opendata.swiss/en/dataset/gemeindefinanzen-nach-rechnungsteil-funktion-kontenart-und-jahr-ab-2014", "grund": "Lauf 1 und 2: Fehlerseite «Error 403» – Existenz nicht belegbar; BL-C1-01 (statistik.bl.ch) deckt den Inhalt ab."},
    {"titel": "Stadt Wil: PO 101 «Für eine neue Bodenpolitik» – Stellungnahme", "url": "https://www.stadtwil.ch/_docn/1058128/PO_101_Fuer_eine_neue_Bodenpolitik_Stellungnahme.pdf", "grund": "HTTP 404 (CMS-Umstellung); kein Ersatzlink gefunden."},
    {"titel": "Stadt Wil: Gemeindeordnung (alter Link)", "url": "https://stadtwil.ch/_doc/1267121", "grund": "HTTP 404; Ersatz über Rechtssammlung der Stadt (WIL-C3-01 ff.)."},
    {"titel": "Stadt Wil: TBW-Reglement 2020 (alter Link)", "url": "https://www.stadtwil.ch/_docn/2747618/012_BA_Erlass_neuesTBW-Reglement.pdf", "grund": "HTTP 404; Ersatz über Rechtssammlung der Stadt."},
    {"titel": "Stadt Wil: Beteiligungsreglement (alter Link)", "url": "https://www.stadtwil.ch/_doc/2079992", "grund": "HTTP 404; Ersatz über Rechtssammlung der Stadt."},
    {"titel": "Stadt Wil: Geschäftsbericht 2024 (alter Link)", "url": "https://www.stadtwil.ch/_doc/5663965", "grund": "HTTP 404; ersetzt durch Geschäftsbericht 2025 (WIL-C4-01)."},
    {"titel": "Stadt Wil: Nachtrag IV Bericht (alter Link)", "url": "https://stadtwil.ch/_doc/4801870", "grund": "HTTP 404; ersetzt durch Abstimmungsseite (WIL-C2-01)."},
    {"titel": "Stadt Wil: Jahresrechnung 2023 / Rechnung 2024 (alte Links)", "url": "https://www.stadtwil.ch/_docn/5050942/Jahresrechnung_2023.pdf ; https://www.stadtwil.ch/_doc/5592973", "grund": "HTTP 404; ersetzt durch /storage-Links (WIL-C1-03/04)."},
    {"titel": "EFV: FS-Methodenband (PDF)", "url": "https://www.efv.admin.ch/dam/efv/en/dokumente/finanzstatistik/methoden/FS-Methodenband.pdf.download.pdf/FS-Methodenband.pdf", "grund": "HTTP 502; ersetzt durch Methodenseite (CH-C1-03)."},
    {"titel": "Sekundärquellen (Presse: Bote der Urschweiz, SRF)", "url": "–", "grund": "Nicht aufgenommen, da Primärquellen verfügbar (Quellenpriorisierung)."},
]
out = {"stand": STAND, "verworfene_kandidaten": VERWORFEN, "bestehende_zeilen": B, "neue_quellen": N,
       "gemeindeanfragen": {"bestehend": A, "neu": NEU}, "bericht": BERICHT}
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(B), len(N))
