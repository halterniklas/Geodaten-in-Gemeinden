#!/usr/bin/env python3
"""Q-Restriktionsprofil der drei Pilotgemeinden (Assignment 01, Aufgabe 1).

Ergänzt die Q-Rahmen-Übersicht um:
  10_Q_Einordnungslogik   Regeln Ausschluss / Interessenabwägung nötig / unkritisch, Peer-Notiz Q
  11–13_Q_Profil_<Gde>    Restriktionen Q1–Q5 je Gemeinde mit Betroffenheit, Einordnung, Gegeninteressen
  14_Q_Datenanfrage       Daten, die Gemeinde oder Kanton liefern müssen
  15_Recherchevorgehen    wiederholbares, automatisierbares Vorgehen mit Verlässlichkeit

Quellen der Betroffenheit: GIS-Abfrage api3.geo.admin.ch (Runner «GIS-Betroffenheit», Blatt 7),
Q-Katalog (Blätter 1–6) und Runner «Recherche Q und C».

Aufruf: python3 q_restriktionsprofil.py Q-Rahmen_Uebersicht_V1.xlsx
"""
import sys

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

STAND = "14.10.2026"
DARK, LIGHT = "FF1F3A4D", "FFD9E2E8"
FILL = {
    "Ausschluss": "FFF4B6B6",
    "Interessenabwägung nötig": "FFFFE699",
    "unkritisch": "FFC6EFCE",
    "offen": "FFE7E6E6",
}
THIN = Side(style="thin", color="FFBFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
GEMEINDEN = {  # Kürzel -> (Name, Kanton, Zentrum LV95)
    "M": ("Münchenstein", "BL", "2613308,1263110"),
    "W": ("Wil", "SG", "2721138,1258009"),
    "S": ("Seelisberg", "UR", "2687333,1203124"),
}
FEDLEX = "https://www.fedlex.admin.ch/eli/cc/"

# ------------------------------------------------------------------ Einordnungsregeln
REGELN = [
    ("A1", "Ausschluss", "Moore und Moorlandschaften von nationaler Bedeutung",
     "Art. 78 Abs. 5 BV; Art. 23a–23d NHG; Hoch-/Flachmoor-, Moorlandschaftsverordnung",
     "Absoluter Schutz: keine Bauten und Anlagen, die dem Schutzziel widersprechen; keine Interessenabwägung zulässig."),
    ("A2", "Ausschluss", "Biotope von nationaler Bedeutung (Auen, Amphibienlaichgebiete Bereich A, TWW)",
     "Art. 18a NHG; Auen-, Amphibienlaichgebiete-, Trockenwiesenverordnung",
     "Ungeschmälerte Erhaltung; Abweichung nur für standortgebundene Vorhaben von überwiegendem nationalem "
     "Interesse – für Siedlungsentwicklung faktisch ausgeschlossen."),
    ("A3", "Ausschluss", "Wald und Waldreservate",
     "Art. 5 WaG (Rodungsverbot); Art. 17 WaG (Waldabstand)",
     "Rodung nur ausnahmsweise für standortgebundene Werke; Waldabstand im Siedlungsrand ist Interessenabwägung."),
    ("A4", "Ausschluss", "Rote Gefahrenzone, Grundwasserschutzzonen S1/S2, Gewässerraum",
     "Art. 6 WBV / kant. Recht; Anhang 4 GSchV; Art. 41a–41c GSchV",
     "Bauverbot bzw. nur standortgebundene Anlagen im öffentlichen Interesse."),
    ("A5", "Ausschluss", "Neue Zweitwohnungen bei Zweitwohnungsanteil > 20 %",
     "Art. 75b BV; Art. 6 ZWG; Anhang ZWV",
     "Bewilligung neuer Zweitwohnungen unzulässig; Erstwohnungen und touristisch bewirtschaftete Wohnungen möglich."),
    ("I1", "Interessenabwägung nötig", "BLN-Objekte",
     "Art. 6 NHG; VBLN", "Ungeschmälerte Erhaltung als Grundsatz; bei Bundesaufgaben Abweichung nur bei "
     "gleich- oder höherwertigem nationalem Interesse, sonst Berücksichtigung in Richt- und Nutzungsplanung."),
    ("I2", "Interessenabwägung nötig", "ISOS-Ortsbilder und IVS-Verkehrswege von nationaler Bedeutung",
     "Art. 6 NHG; VISOS; VIVS; Berücksichtigungspflicht in der Planung (BGE 135 II 209)",
     "Erhaltungsziele sind in Richt- und Nutzungsplanung zu berücksichtigen und gegen Entwicklungsinteressen abzuwägen."),
    ("I3", "Interessenabwägung nötig", "Fruchtfolgeflächen (FFF)",
     "Art. 30 RPV; Sachplan FFF 2020",
     "Beanspruchung nur für ein auch aus Sicht des Kantons wichtiges Ziel, bei optimaler Nutzung und mit Kompensation."),
    ("I4", "Interessenabwägung nötig", "Siedlungsgebiet und Einzonung (kantonaler Richtplan)",
     "Art. 8a, 15 RPG; kantonaler Richtplan",
     "Innerhalb der rechtskräftigen Bauzone unkritisch; Einzonung nur im Siedlungsgebiet, bei Bedarfsnachweis "
     "(15 Jahre) und Mobilisierung der Reserven."),
    ("I5", "Interessenabwägung nötig", "Wildtierkorridore und Vernetzung (überregional)",
     "Art. 18 NHG; kantonaler Richtplan; Konzept Landschaft Schweiz",
     "Durchlässigkeit sichern; Siedlungserweiterung im Korridor nur mit Abwägung und Ersatz."),
    ("I6", "Interessenabwägung nötig", "Störfallvorsorge (Bahn, Gasleitungen, Betriebe)",
     "Art. 11a StFV; Planungshilfe Koordination Raumplanung und Störfallvorsorge",
     "Verdichtung oder Einzonung im Konsultationsbereich nur mit Risikoermittlung und Abstimmung."),
    ("I7", "Interessenabwägung nötig", "Lärmbelastung",
     "Art. 24 USG; Art. 29–31 LSV",
     "Einzonungen nur bei eingehaltenen Planungswerten; Verdichtung in belasteten Lagen mit Auflagen und Abwägung."),
    ("I8", "Interessenabwägung nötig", "Kantonale und kommunale Schutzobjekte (KGS, Denkmal, Schutzinventare)",
     "Kantonales NHG/Denkmalschutzrecht; kommunale Schutzverordnungen; KGSG",
     "Erhaltung des Objekts und seiner Umgebung gegenüber Veränderungsinteressen abwägen."),
    ("I9", "Interessenabwägung nötig", "Hitzebelastung in Siedlungsgebieten",
     "Art. 3 Abs. 3 RPG (Planungsgrundsätze); kantonale Klimaanalysen; KlG Art. 8 (Anpassung)",
     "Keine Bauverbote; Verdichtung in Wärmeinseln erfordert Abwägung mit Durchlüftung, Grün- und Freiraum."),
    ("U1", "unkritisch", "Auflagen ohne Standortwirkung",
     "SIA 261 (Baugrund), kant. Energiegesetze, Altlastenverordnung (Untersuchungspflicht), Objektschutz",
     "Restriktion wird über Projektauflagen erfüllt; beeinflusst Kosten, nicht die Zulässigkeit eines Standorts."),
    ("U2", "unkritisch", "Restriktion nicht betroffen",
     "–", "Objekt oder Belastung liegt nicht im Gemeindegebiet (GIS-Abfrage negativ)."),
    ("O1", "offen", "Betroffenheit nicht ermittelt",
     "–", "Kantonale Daten oder Rasterlayer ohne Abfrage; Einordnung gilt vorläufig nach der Regel in Spalte «Regel»."),
]


def ml(layer, g):
    return (f"https://map.geo.admin.ch/#/map?lang=de&center={GEMEINDEN[g][2]}&z=9"
            f"&bgLayer=ch.swisstopo.pixelkarte-grau&layers={layer}")


# ------------------------------------------------------------------ Restriktionen je Gemeinde
# (Q, Restriktion, Grundlage, Regel-Standard, Gegeninteressen,
#  {Gde: (Betroffenheit, Befund, Einordnung, Regel, Quelle, Confidence, Lücke/Datenanfrage)})
J, N, O = "ja", "nein", "offen"
AUS, IA, UK, OF = "Ausschluss", "Interessenabwägung nötig", "unkritisch", "offen"
GIS = "GIS-Abfrage api3.geo.admin.ch (Blatt 7)"

R = [
    ("Q1", "Kantonaler Richtplan / Siedlungsgebiet, Bauzonen", "RPG Art. 8a, 15; kant. Richtplan",
     "Siedlungsentwicklung, Wohnraum- und Arbeitsplatzbedarf ↔ haushälterische Bodennutzung, Kulturland, Landschaft",
     {"M": (J, "Rechtskräftige Bauzonen (harmonisiert); Siedlungsgebiet gemäss KRIP BL", IA, "I4",
            ml("ch.are.bauzonen", "M"), "mittel", "Bauzonenreserven und Kapazität aus Luucy (Nikolaos)"),
      "W": (J, "Rechtskräftige Bauzonen; Siedlungsgebiet gemäss Richtplan SG; Ortsplanungsrevision 2025 läuft",
            IA, "I4", ml("ch.are.bauzonen", "W"), "mittel", "Bauzonenreserven aus Luucy; Stand Ortsplanungsrevision"),
      "S": (J, "Rechtskräftige Bauzonen; Teilrevision Nutzungsplanung Sonnenberg (BZO rev. 18.02.2025)", IA, "I4",
            ml("ch.are.bauzonen", "S"), "mittel", "Bauzonenreserven aus Luucy; Dimensionierung gemäss Richtplan UR")}),
    ("Q1", "Zweitwohnungen", "BV Art. 75b; ZWG Art. 6; Anhang ZWV",
     "Tourismus, Zweitwohnungsnachfrage, Bauwirtschaft ↔ Erstwohnraum, Landschaft, Ortsbild",
     {"M": (N, "Gemeinde nicht im Anhang ZWV erwartet (Agglomeration); BL-Teil der Liste noch nicht eingesehen",
            UK, "U2", FEDLEX + "2015/887/de", "mittel", "BL-Teil Anhang ZWV / Wohnungsinventar bestätigen"),
      "W": (N, "In der SG-Liste des Anhangs ZWV nicht aufgeführt", UK, "U2", FEDLEX + "2015/887/de", "hoch", None),
      "S": (J, "Im Anhang ZWV aufgeführt (BFS 1215, Zweitwohnungsanteil > 20 %)", AUS, "A5",
            FEDLEX + "2015/887/de", "hoch", "Aktueller Zweitwohnungsanteil (Wohnungsinventar ARE)")}),
    ("Q2", "Fruchtfolgeflächen (FFF)", "RPV Art. 26–30; Sachplan FFF",
     "Siedlungserweiterung, Infrastruktur ↔ Ernährungssicherheit, Landwirtschaft",
     {"M": (O, "Landwirtschaftsflächen ausserhalb Bauzone (u. a. Brüglinger Ebene); kantonaler FFF-Layer nicht abgefragt",
            OF, "I3", "https://geoview.bl.ch/", "tief", "FFF-Layer BL (geoview) – Nikolaos/Luucy"),
      "W": (O, "Landwirtschaftsflächen am Siedlungsrand; kantonaler FFF-Layer nicht abgefragt", OF, "I3",
            "https://www.geoportal.ch/ktsg", "tief", "FFF-Layer SG (geoportal) – Nikolaos/Luucy"),
      "S": (O, "Berggebiet; FFF wenig wahrscheinlich, kantonaler Layer nicht abgefragt", OF, "I3",
            "https://geo.ur.ch/", "tief", "FFF-Layer UR (geo.ur.ch) – Nikolaos/Luucy")}),
    ("Q2", "BLN-Objekte", "NHG Art. 6; VBLN",
     "Siedlungs-, Tourismus- und Infrastrukturentwicklung ↔ Landschaftsschutz",
     {"M": (J, "BLN Gempenplateau (Randbereich)", IA, "I1", ml("ch.bafu.bundesinventare-bln", "M"), "hoch", None),
      "W": (J, "BLN Thurlandschaft zwischen Lichtensteig und Schwarzenbach (Randlage; manuelle Sichtung ergab "
                "«nein», GIS-Abfrage «ja»)", IA, "I1", ml("ch.bafu.bundesinventare-bln", "W"), "mittel",
            "Lage im Viewer bestätigen"),
      "S": (J, "BLN Vierwaldstättersee mit Kernwald, Bürgenstock und Rigi", IA, "I1",
            ml("ch.bafu.bundesinventare-bln", "S"), "hoch", None)}),
    ("Q2", "Moorlandschaften von besonderer Schönheit", "BV Art. 78 Abs. 5; NHG Art. 23a–23d",
     "Tourismus, Erschliessung, Landwirtschaft ↔ absoluter Moorlandschaftsschutz",
     {"M": (N, "–", UK, "U2", ml("ch.bafu.bundesinventare-moorlandschaften", "M"), "hoch", None),
      "W": (N, "–", UK, "U2", ml("ch.bafu.bundesinventare-moorlandschaften", "W"), "hoch", None),
      "S": (J, "Moorlandschaft Oberbauen/Scheidegg", AUS, "A1",
            ml("ch.bafu.bundesinventare-moorlandschaften", "S"), "hoch", None)}),
    ("Q2", "Hoch- und Flachmoore", "BV Art. 78 Abs. 5; Hochmoor-/Flachmoorverordnung",
     "Siedlungsrand, Erholung, Landwirtschaft ↔ absoluter Moorschutz",
     {"M": (N, "–", UK, "U2", ml("ch.bafu.bundesinventare-flachmoore", "M"), "hoch", None),
      "W": (J, "Flachmoor Gärtensberg/Oberholz", AUS, "A1", ml("ch.bafu.bundesinventare-flachmoore", "W"), "hoch", None),
      "S": (N, "–", UK, "U2", ml("ch.bafu.bundesinventare-flachmoore", "S"), "hoch", None)}),
    ("Q2", "Auengebiete von nationaler Bedeutung", "NHG Art. 18a; Auenverordnung",
     "Hochwasserschutz, Erholung, Siedlungsrand ↔ Auenschutz",
     {"M": (N, "–", UK, "U2", ml("ch.bafu.bundesinventare-auen", "M"), "hoch", None),
      "W": (J, "Aue Thurauen Wil – Weieren", AUS, "A2", ml("ch.bafu.bundesinventare-auen", "W"), "hoch", None),
      "S": (N, "–", UK, "U2", ml("ch.bafu.bundesinventare-auen", "S"), "hoch", None)}),
    ("Q2", "Amphibienlaichgebiete (ortsfest)", "NHG Art. 18a; AlgV",
     "Siedlungs- und Verkehrsentwicklung ↔ Artenschutz",
     {"M": (N, "–", UK, "U2", ml("ch.bafu.bundesinventare-amphibien", "M"), "hoch", None),
      "W": (J, "Hasenlooweiher", AUS, "A2", ml("ch.bafu.bundesinventare-amphibien", "W"), "hoch", None),
      "S": (N, "–", UK, "U2", ml("ch.bafu.bundesinventare-amphibien", "S"), "hoch", None)}),
    ("Q2", "Trockenwiesen und -weiden (TWW)", "NHG Art. 18a; TwwV",
     "Siedlungsrand, Landwirtschaft, Tourismus ↔ Biodiversität",
     {"M": (J, "Brügglingen, Zwölf Jucharte", AUS, "A2",
            ml("ch.bafu.bundesinventare-trockenwiesen_trockenweiden", "M"), "hoch", None),
      "W": (N, "–", UK, "U2", ml("ch.bafu.bundesinventare-trockenwiesen_trockenweiden", "W"), "hoch", None),
      "S": (J, "Bol, Haltenen, Hinter Bergli, Läger, Weid", AUS, "A2",
            ml("ch.bafu.bundesinventare-trockenwiesen_trockenweiden", "S"), "hoch", None)}),
    ("Q2", "Jagdbanngebiete, Wasser- und Zugvogelreservate", "JSG Art. 11; VEJ; WZVV",
     "Erholung, Tourismus ↔ Wildtierschutz",
     {g: (N, "–", UK, "U2", ml("ch.bafu.bundesinventare-jagdbanngebiete", g), "hoch", None) for g in GEMEINDEN}),
    ("Q2", "Wildtierkorridore (überregional)", "NHG Art. 18; kant. Richtplan",
     "Siedlungserweiterung, Verkehr ↔ ökologische Vernetzung",
     {"M": (N, "–", UK, "U2", ml("ch.bafu.fauna-wildtierkorridor_national", "M"), "hoch", None),
      "W": (J, "Wildtierkorridor SG-19", IA, "I5", ml("ch.bafu.fauna-wildtierkorridor_national", "W"), "hoch", None),
      "S": (N, "–", UK, "U2", ml("ch.bafu.fauna-wildtierkorridor_national", "S"), "hoch", None)}),
    ("Q2", "Wald, Waldreservate", "WaG Art. 5, 17",
     "Siedlungsrand, Infrastruktur, Tourismus ↔ Walderhaltung, Schutzfunktion",
     {"M": (J, "Wald; Waldreservate Ermitage – Chilchholz, Rütihard – Rothallen", AUS, "A3",
            ml("ch.bafu.waldreservate", "M"), "hoch", "Kantonale Waldfeststellung an Bauzonengrenzen"),
      "W": (J, "Wald; Waldreservat Thurauen Wil", AUS, "A3", ml("ch.bafu.waldreservate", "W"), "hoch",
            "Kantonale Waldfeststellung an Bauzonengrenzen"),
      "S": (J, "Wald, teils Schutzwald; Waldreservat Rütliwald", AUS, "A3", ml("ch.bafu.waldreservate", "S"), "hoch",
            "Schutzwaldausscheidung UR")}),
    ("Q2", "Gewässerraum, Grundwasserschutzzonen", "GSchG Art. 20, 36a; GSchV Art. 41a–41c, Anhang 4",
     "Siedlungsentwicklung am Wasser, Erschliessung ↔ Gewässer- und Trinkwasserschutz",
     {"M": (O, "Birs und Grundwasserfassungen; kantonale Daten nicht abgefragt", OF, "A4", "https://geoview.bl.ch/",
            "tief", "Gewässerraum- und Grundwasserschutzzonenplan (Gemeinde/Kanton)"),
      "W": (O, "Thur und Nebengewässer; kantonale Daten nicht abgefragt", OF, "A4", "https://www.geoportal.ch/ktsg",
            "tief", "Gewässerraum- und Grundwasserschutzzonenplan (Gemeinde/Kanton)"),
      "S": (O, "Quellfassungen (Wasserversorgung gemäss Verordnung 2020); kantonale Daten nicht abgefragt", OF, "A4",
            "https://geo.ur.ch/", "tief", "Grundwasserschutzzonen der Quellfassungen (Gemeinde)")}),
    ("Q2", "Kantonale und kommunale Natur- und Landschaftsschutzgebiete", "kant. NHG; kommunale Schutzverordnungen",
     "Siedlungsentwicklung, Landwirtschaft ↔ Natur- und Landschaftsschutz",
     {"M": (J, "Inventar geschützter Naturobjekte BL; Schutzfestlegungen der Zonenvorschriften", IA, "I8",
            "https://oereblex.bl.ch/api/attachments/22718", "mittel", "Zonenplan Landschaft (GIS)"),
      "W": (J, "Reglement zur Schutzverordnung mit Schutzplan (Natur- und Landschaftsobjekte)", IA, "I8",
            "https://cms.e-mitwirkung.ch/media/wil/Reglement_221013.pdf", "mittel", "Erlassene Schutzverordnung und Schutzplan (GIS)"),
      "S": (J, "Kantonales Schutzinventar Seelisberg (u. a. Landschaftsschutzgebiete), BZO Art. 20–23", IA, "I8",
            "https://www.ur.ch/_docn/385540/Inventarliste_Seelisberg_Website.pdf", "hoch", "Schutzinventar als GIS-Daten")}),
    ("Q3", "Energie: Wärmeversorgung und Energieplanung", "EnG; kant. Energiegesetze; kommunale Energieplanung",
     "Kostengünstige Wärmeversorgung, freie Systemwahl ↔ Netto-Null-Absenkpfad, Anschlussgebiete",
     {"M": (J, "15 thermische Netze, u. a. Fernwärme Basel Münchenstein, Wärmeverbund Spengler", UK, "U1",
            ml("ch.bfe.thermische-netze", "M"), "hoch", "Kommunale Energieplanung / Anschlussgebiete"),
      "W": (N, "Kein thermisches Netz im Bundesdatensatz; Energiestadt Gold, Klimaprogramm", UK, "U1",
            ml("ch.bfe.thermische-netze", "W"), "mittel", "Energierichtplan / Wärmeplanung Wil"),
      "S": (N, "Kein thermisches Netz im Bundesdatensatz", UK, "U1", ml("ch.bfe.thermische-netze", "S"), "mittel",
            "Kommunale Energievorgaben (falls vorhanden)")}),
    ("Q3", "Klimaziele, Gebäudestandards, Solarpflicht", "KlG; CO₂-Gesetz; kant. Energiegesetze (MuKEn)",
     "Baukosten, Ortsbild (Solaranlagen) ↔ Klimaschutz",
     {g: (J, "Gelten flächendeckend; Solarpotenzial Dächer/Fassaden vorhanden", UK, "U1",
          ml("ch.bfe.solarenergie-eignung-daecher", g), "hoch", None) for g in GEMEINDEN}),
    ("Q4", "Naturgefahren (kantonale Gefahrenkarten)", "WBG; WaG; kant. Recht; Gefahrenzonen in der Nutzungsplanung",
     "Siedlungsentwicklung, Bestandsnutzung ↔ Schutz vor Hochwasser, Rutschung, Steinschlag",
     {"M": (O, "Birs (Hochwasser), Hanglagen; Gefahrenkarte BL nicht ausgewertet", OF, "A4",
            "https://geoview.bl.ch/?map_x=2613308&map_y=1263110&map_zoom=4&baselayer_opacity=100&baselayer_ref=grundkarte_farbig"
            "&tree_group_layers_Naturgefahren=ghk_wassergefahren_ueberschwemmung_wildbach%2Cghk_wassergefahren_ueberschwemmung_talfluesse",
            "tief", "Gefahrenstufen im Siedlungsgebiet (Kanton BL)"),
      "W": (O, "Thur, Oberflächengewässer; Gefahrenkarte SG nicht ausgewertet", OF, "A4",
            "https://www.geoportal.ch/ktsg/map/3502?y=2721138&x=1258009&scale=50000&rotation=0", "tief",
            "Gefahrenstufen im Siedlungsgebiet (Kanton SG)"),
      "S": (J, "Gefahrenzonen in der BZO (Art. 24); Gefahrenkarte UR Stand 22.08.2023", IA, "A4",
            "https://www.seelisberg.ch/files/pdf/Bau-und-Zonenordnung-Seelisberg.pdf", "mittel",
            "Lage roter/blauer Zonen gegenüber Entwicklungsgebieten (Sonnenberg)")}),
    ("Q4", "Oberflächenabfluss (Starkregen)", "GSchG; WBG; kant. Bauvorschriften (Objektschutz)",
     "Verdichtung, Versiegelung ↔ Retention, Objektschutz",
     {g: (O, "Rasterlayer, per Abfrage nicht auswertbar", UK, "U1",
          ml("ch.bafu.gefaehrdungskarte-oberflaechenabfluss", g), "tief",
          "GEP / Starkregengefährdung im Siedlungsgebiet") for g in GEMEINDEN}),
    ("Q4", "Hitzebelastung", "RPG Art. 3; KlG Art. 8; kantonale Klimaanalysen",
     "Innenverdichtung ↔ Hitzevorsorge, Durchlüftung, Grünraum",
     {"M": (O, "Agglomerationsgemeinde in der Birsebene; Klimaanalyse BL nicht ausgewertet", IA, "I9",
            "https://geoview.bl.ch/", "tief", "Klimaanalysekarte BL (Wärmeinseln, Kaltluft)"),
      "W": (O, "Städtisches Zentrum; Klimaanalyse SG nicht ausgewertet", IA, "I9", "https://www.geoportal.ch/ktsg",
            "tief", "Klimaanalysekarte SG"),
      "S": (O, "Ländlich, Höhenlage rund 800 m ü. M.; geringe Hitzebelastung erwartet", UK, "U1", "https://geo.ur.ch/",
            "tief", None)}),
    ("Q4", "Lärmbelastung", "USG Art. 24; LSV Art. 29–31",
     "Wohnen an zentralen, gut erschlossenen Lagen ↔ Gesundheitsschutz",
     {"M": (O, "A18, Bahnlinie Basel–Delémont, Tram; Rasterlayer nicht abfragbar", IA, "I7",
            ml("ch.bafu.laerm-strassenlaerm_tag", "M"), "tief", "Lärmbelastungskataster / ES-Zuteilung"),
      "W": (O, "A1, Bahnknoten Wil; Rasterlayer nicht abfragbar", IA, "I7", ml("ch.bafu.laerm-strassenlaerm_tag", "W"),
            "tief", "Lärmbelastungskataster / ES-Zuteilung"),
      "S": (O, "Keine Hauptverkehrsachse; Rasterlayer nicht abfragbar", UK, "U1",
            ml("ch.bafu.laerm-strassenlaerm_tag", "S"), "tief", None)}),
    ("Q4", "Störfallvorsorge", "StFV Art. 11a",
     "Verdichtung an Bahn- und Leitungskorridoren ↔ Personenrisiko",
     {"M": (J, "Bundesdaten ohne Treffer; Hochdruck-Erdgasleitung mit Konsultationsbereich (Auflage RRB 2017 zur "
                "Ortsplanung)", IA, "I6", "https://oereblex.bl.ch/api/attachments/22718", "mittel",
            "Risikoermittlung Gasleitung, kantonaler Chemie-Risikokataster"),
      "W": (J, "Bahnstrecken nach StFV (Wil–Bronschhofen, Wil–Sirnach u. a.)", IA, "I6",
            ml("ch.bav.lage-stoerfallverordnung_eisenbahnanlagen", "W"), "hoch", "Kantonaler Chemie-Risikokataster"),
      "S": (N, "Keine Treffer in den Bundesdaten", UK, "U2", ml("ch.bav.lage-stoerfallverordnung_eisenbahnanlagen", "S"),
            "mittel", "Kantonaler Chemie-Risikokataster")}),
    ("Q4", "Belastete Standorte", "USG Art. 32c; AltlV",
     "Umnutzung von Arealen ↔ Boden- und Grundwasserschutz",
     {"M": (O, "Bundeskataster ohne Treffer; kantonaler KbS BL nicht abgefragt (Industrieareale)", UK, "U1",
            "https://geoview.bl.ch/", "tief", "Kantonaler Kataster belasteter Standorte BL"),
      "W": (J, "14 Standorte KbS öV, 14 Standorte KbS Militär; kantonaler KbS nicht abgefragt", UK, "U1",
            ml("ch.bav.kataster-belasteter-standorte-oev", "W"), "mittel", "Kantonaler Kataster belasteter Standorte SG"),
      "S": (J, "4 Standorte KbS Militär; kantonaler KbS nicht abgefragt", UK, "U1",
            ml("ch.vbs.kataster-belasteter-standorte-militaer", "S"), "mittel", "Kantonaler Kataster belasteter Standorte UR")}),
    ("Q4", "Erdbeben (Baugrundklassen)", "SIA 261; kant. Vollzug",
     "Baukosten ↔ Erdbebensicherheit",
     {"M": (J, "Baugrundklassen B und E (Birsebene)", UK, "U1", ml("ch.bafu.gefahren-baugrundklassen", "M"), "hoch", None),
      "W": (N, "Keine Baugrundklassen kartiert", UK, "U2", ml("ch.bafu.gefahren-baugrundklassen", "W"), "mittel", None),
      "S": (J, "Baugrundklasse A (Fels)", UK, "U1", ml("ch.bafu.gefahren-baugrundklassen", "S"), "hoch", None)}),
    ("Q5", "ISOS-Ortsbilder von nationaler Bedeutung", "NHG Art. 6; VISOS",
     "Innenentwicklung, Verdichtung, Umnutzung ↔ Ortsbilderhaltung",
     {"M": (J, "Ortsbilder Münchenstein und Brüglingen", IA, "I2",
            ml("ch.bak.bundesinventar-schuetzenswerte-ortsbilder", "M"), "hoch", "Erhaltungsziele je Gebiet auswerten"),
      "W": (J, "Ortsbild Wil (Altstadt)", IA, "I2", ml("ch.bak.bundesinventar-schuetzenswerte-ortsbilder", "W"), "hoch",
            "Erhaltungsziele je Gebiet auswerten"),
      "S": (N, "Kein ISOS-Ortsbild von nationaler Bedeutung", UK, "U2",
            ml("ch.bak.bundesinventar-schuetzenswerte-ortsbilder", "S"), "hoch", None)}),
    ("Q5", "Historische Verkehrswege (IVS national)", "NHG Art. 6; VIVS",
     "Strassenausbau, Erschliessung ↔ Substanzerhaltung",
     {"M": (J, "1 Objekt (Nr. 100820)", IA, "I2", ml("ch.astra.ivs-nat", "M"), "hoch", None),
      "W": (J, "6 Objekte", IA, "I2", ml("ch.astra.ivs-nat", "W"), "hoch", None),
      "S": (J, "24 Objekte", IA, "I2", ml("ch.astra.ivs-nat", "S"), "hoch", None)}),
    ("Q5", "Kulturgüter (KGS-Inventar)", "KGSG; kant. Denkmalschutzrecht",
     "Umnutzung, Erweiterung ↔ Denkmalpflege",
     {"M": (J, "Bruckgut, Villa Merian, Brüglingen (Mühle, Orangerie), Schaulager u. a.", IA, "I8",
            ml("ch.babs.kulturgueter", "M"), "hoch", None),
      "W": (J, "Baronenhaus, Hof, Rudenzburg, Wallfahrtskirche Maria-Hilf, Dreibrunnen", IA, "I8",
            ml("ch.babs.kulturgueter", "W"), "hoch", None),
      "S": (J, "Rütli (Rütlihaus), Schillerstein, Wirtshaus zur Treib u. a.", IA, "I8", ml("ch.babs.kulturgueter", "S"),
            "hoch", None)}),
    ("Q5", "Kantonale und kommunale Ortsbild- und Denkmalschutzfestlegungen", "kant. Denkmalrecht; Nutzungsplanung",
     "Bauliche Entwicklung, Energie (Solar) ↔ Ortsbild, Baukultur",
     {"M": (J, "Inventar der Kulturdenkmäler BL; Schutz- und Schonzonen der Zonenvorschriften", IA, "I8",
            "https://www.geoportal.ch/muenchenstein/map/912?y=2611965.69&x=1263213.43&scale=17500&rotation=0", "mittel", None),
      "W": (J, "Schutzverordnung (Schutzobjekte), Stadtbildkommission", IA, "I8",
            "https://cms.e-mitwirkung.ch/media/wil/Reglement_221013.pdf", "mittel", "Erlassene Schutzverordnung"),
      "S": (J, "Kantonales Schutzinventar 2022; Kernzone Sonnenberg (BZO Art. 8a)", IA, "I8",
            "https://www.ur.ch/_docn/385540/Inventarliste_Seelisberg_Website.pdf", "hoch", None)}),
]

SYNTHESE = {
    "M": ("Ausschluss: TWW Brüglingen/Zwölf Jucharte, Wald inkl. Waldreservate Ermitage und Rütihard. "
          "Interessenabwägung: ISOS Münchenstein und Brüglingen, BLN Gempenplateau, Störfall (Gasleitung), Lärm, Hitze. "
          "Offen: FFF, Naturgefahren (Birs), Gewässerraum. Innenentwicklung ist möglich, aber ortsbild- und "
          "belastungssensibel."),
    "W": ("Ausschluss: Aue Thurauen, Flachmoor Gärtensberg/Oberholz, Amphibienlaichgebiet Hasenlooweiher, Wald. "
          "Interessenabwägung: ISOS Altstadt Wil, Wildtierkorridor SG-19, Störfall Bahn, Lärm, BLN (Randlage). "
          "Offen: FFF, Naturgefahren, Hitze. Restriktionen liegen vor allem am Siedlungsrand (Thur) und im Kern."),
    "S": ("Ausschluss: Moorlandschaft Oberbauen/Scheidegg, fünf TWW-Objekte, Wald/Rütliwald, neue Zweitwohnungen (ZWG). "
          "Interessenabwägung: BLN Vierwaldstättersee, IVS, Kulturgüter (Rütli, Treib), kantonales Schutzinventar, "
          "Naturgefahren (BZO-Gefahrenzonen). Hohe Landschafts- und Schutzdichte; Entwicklung nur innerhalb der "
          "bestehenden Bauzonen realistisch."),
}

DATENANFRAGE = [
    ("Q1", "Bauzonenreserven, Kapazität und Mobilisierbarkeit", "alle", "Nikolaos (Luucy)", "Übernahme, nicht neu erheben", "hoch"),
    ("Q1", "Wohnungsinventar / aktueller Zweitwohnungsanteil", "Seelisberg, Münchenstein", "ARE / Gemeinde", "öffentlich (ARE)", "mittel"),
    ("Q2", "Fruchtfolgeflächen im Gemeindegebiet (GIS)", "alle", "Kanton / Nikolaos (Luucy)", "kantonale Geoportale", "hoch"),
    ("Q2", "Gewässerraum- und Grundwasserschutzzonenplan", "alle", "Gemeinde / Kanton", "Gemeindeanfrage", "hoch"),
    ("Q2", "Schutzplan / Schutzinventar als GIS-Daten", "alle", "Gemeinde", "Gemeindeanfrage", "mittel"),
    ("Q2/Q5", "Erlassene Schutzverordnung Wil (statt Auflageentwurf 2022)", "Wil", "Stadt Wil", "Gemeindeanfrage", "hoch"),
    ("Q4", "Gefahrenkarte: Lage roter und blauer Zonen gegenüber Entwicklungsgebieten", "alle", "Kanton / Gemeinde", "kantonale Geoportale", "hoch"),
    ("Q4", "GEP / Starkregen- und Oberflächenabflussplanung", "alle", "Gemeinde", "Gemeindeanfrage", "mittel"),
    ("Q4", "Klimaanalyse (Wärmeinseln, Kaltluft) im Siedlungsgebiet", "Münchenstein, Wil", "Kanton", "kantonale Geoportale", "mittel"),
    ("Q4", "Lärmbelastungskataster und Empfindlichkeitsstufen", "Münchenstein, Wil", "Kanton / Gemeinde", "Gemeindeanfrage", "mittel"),
    ("Q4", "Kantonaler Kataster belasteter Standorte und Chemie-Risikokataster", "alle", "Kanton", "kantonale Geoportale", "mittel"),
    ("Q4", "Risikoermittlung Hochdruck-Erdgasleitung (Auflage RRB 2017)", "Münchenstein", "Gemeinde / Kanton BL", "Gemeindeanfrage", "mittel"),
    ("Q5", "ISOS-Erhaltungsziele je Gebiet und kommunale Umsetzung", "Münchenstein, Wil", "BAK / Gemeinde", "öffentlich (ISOS-Blätter)", "mittel"),
]

VORGEHEN = [
    ("1", "Katalog aufbauen", "Erlasse und Pläne je Ebene (Bund → Kanton → Gemeinde) und Q-Dimension aus dem "
     "Grundlagenkataster übernehmen und ergänzen (Blätter 1–6).", "Gesetzessammlungen (Fedlex, LexWork), "
     "Gemeindewebsites", "teilweise (Titelverzeichnisse per API)", "hoch"),
    ("2", "Links und Identität prüfen", "Jeden Link abrufen und mit Bezeichnung/Referenz abgleichen: Fedlex per "
     "SPARQL (SR ↔ ELI), LexWork per API, Layer-IDs per layersConfig, PDFs per Titel/Text.",
     "Runner «Linkprüfung Excel» (linkpruefung_excel.py)", "ja", "hoch"),
    ("3", "Räumliche Betroffenheit", "Bundeslayer je Gemeinde per identify abfragen, Treffer mit der um 5 m "
     "gepufferten Gemeindefläche verschneiden.", "Runner «GIS-Betroffenheit» (gis_betroffenheit.py)", "ja",
     "hoch für Vektorlayer; Rasterlayer und kantonale Daten nicht abfragbar"),
    ("4", "Ergänzende Recherche", "Zusätzliche Layer, Finanzkennzahlen und Erlasse automatisiert suchen.",
     "Runner «Recherche Q und C» (recherche_qc.py)", "ja", "mittel (Webseiten teils gesperrt)"),
    ("5", "Einordnen", "Jede Restriktion nach der Regel im Blatt 10 einordnen (Ausschluss / Interessenabwägung nötig "
     "/ unkritisch / offen) und die gegenüberstehenden Interessen benennen.",
     "q_restriktionsprofil.py (Regeltabelle)", "ja (regelbasiert)", "hoch, sofern Betroffenheit belegt"),
    ("6", "Lücken dokumentieren", "Nicht abfragbare oder nicht öffentliche Daten in der Datenanfrage führen "
     "(Blatt 14); Einordnung bis zur Lieferung als vorläufig kennzeichnen.", "Blatt 14", "teilweise", "–"),
    ("7", "Fachliche Prüfung", "Ergebnisse durch GIS (Nikolaos) und Fachperson prüfen lassen; Abweichungen "
     "zwischen Abfrage und Sichtung im Profil vermerken.", "manuell", "nein", "–"),
]


# ------------------------------------------------------------------ Ausgabe
def style_header(row):
    for c in row:
        c.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
        c.fill = PatternFill("solid", fgColor=DARK)
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = BORDER


def style_body(ws, first, last, ncol):
    for r in range(first, last + 1):
        for c in range(1, ncol + 1):
            cell = ws.cell(r, c)
            cell.font = Font(name="Arial", size=9)
            if cell.hyperlink:
                cell.font = Font(name="Arial", size=9, color="FF0563C1", underline="single")
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = BORDER


def title(ws, text, sub):
    ws["A1"] = text
    ws["A1"].font = Font(name="Arial", size=14, bold=True, color=DARK)
    ws["A2"] = sub
    ws["A2"].font = Font(name="Arial", size=9, color="FF595959")


def new_sheet(wb, name):
    if name in wb.sheetnames:
        del wb[name]
    return wb.create_sheet(name)


def main():
    path = sys.argv[1]
    wb = openpyxl.load_workbook(path)

    # 10 Einordnungslogik
    ws = new_sheet(wb, "10_Q_Einordnungslogik")
    title(ws, "10 · Q-Einordnungslogik – Ausschluss / Interessenabwägung nötig / unkritisch",
          f"Assignment 01, Aufgabe 1 · Stand {STAND} · Die Einordnung gilt für den betroffenen Perimeter, nicht für "
          "die ganze Gemeinde. Die Abwägung selbst erfolgt nicht in LP01 (Grundlagendokument Kap. 05 und 11).")
    ws.append([])
    ws.append(["Regel", "Einordnung", "Restriktionstyp", "Rechtsgrundlage", "Begründung / Wirkung"])
    style_header(ws[4])
    for reg in REGELN:
        ws.append(list(reg))
        ws.cell(ws.max_row, 2).fill = PatternFill("solid", fgColor=FILL[reg[1]])
    style_body(ws, 5, ws.max_row, 5)
    r = ws.max_row + 2
    notes = [
        ("Peer-Gruppen Q", "Für Q werden keine Peer-Gruppen gebildet (Ausgangshypothese bestätigt): Q-Restriktionen sind "
         "rechtliche Schwellen am Standort und gelten absolut; ein relativer Vergleich mit anderen Gemeinden ändert die "
         "Zulässigkeit nicht (Grundlagendokument Kap. 11: «Q wird als Ausgangs- und Restriktionslage geführt, nicht als "
         "Benchmark»). Höchstens die Anzahl betroffener Objekte kann später deskriptiv verglichen werden."),
        ("Vorrangregel", "Q nicht erfüllt → Variante ausschliessen oder umgestalten; Q gerade erfüllt → B-Lösung "
         "zulässig; Q übererfüllt → positive Wirkung wird in B ausgewiesen (Kap. 05). Derselbe Messwert wird nur einmal "
         "geführt."),
        ("Confidence", "hoch = amtlicher Datensatz per GIS-Abfrage bzw. amtliches Dokument; mittel = amtliche Quelle, "
         "Lage oder Geltung nicht vollständig geprüft; tief = Annahme oder Daten nicht abgefragt."),
        ("Abgrenzung Q6", "Q6 (Bestellung/Umsetzung) ist Prozessqualität und wird nicht als räumliche Restriktion "
         "eingeordnet; die Fähigkeit dazu wird in C3/C4 bewertet (C-Profil)."),
    ]
    for k, v in notes:
        ws.cell(r, 1, k).font = Font(name="Arial", size=9, bold=True)
        ws.cell(r, 2, v).font = Font(name="Arial", size=9)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
        ws.cell(r, 2).alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = 48
        r += 1
    for col, w in zip("ABCDE", (8, 24, 40, 42, 70)):
        ws.column_dimensions[col].width = w

    # 11–13 Profile
    hdr = ["Nr", "Q", "Restriktion", "Rechtsgrundlage", "Betroffen", "Befund im Gemeindegebiet", "Einordnung",
           "Regel", "Gegenüberstehende Interessen", "Quelle / Link", "Stand", "Confidence", "Lücke / Datenanfrage"]
    for i, (g, (name, kt, _)) in enumerate(GEMEINDEN.items()):
        ws = new_sheet(wb, f"{11 + i}_Q_Profil_{name}")
        title(ws, f"{11 + i} · Q-Restriktionsprofil {name} ({kt})",
              f"Entwurf auf Basis öffentlicher Daten · Stand {STAND} · Einordnung nach Blatt 10 · "
              "Betroffenheit aus GIS-Abfrage (Blatt 7) und Q-Katalog")
        ws.append([])
        ws["A4"] = "Wesentliche Q-Restriktionen"
        ws["A4"].font = Font(name="Arial", size=10, bold=True, color=DARK)
        ws["C4"] = SYNTHESE[g]
        ws.merge_cells("C4:M4")
        ws["C4"].alignment = Alignment(wrap_text=True, vertical="top")
        ws["C4"].font = Font(name="Arial", size=9)
        ws.row_dimensions[4].height = 54
        ws["A5"] = "Anzahl"
        ws["A5"].font = Font(name="Arial", size=9, bold=True)
        for j, cat in enumerate(FILL):
            c = ws.cell(5, 3 + 2 * j, cat)
            c.fill = PatternFill("solid", fgColor=FILL[cat])
            c.font = Font(name="Arial", size=9, bold=True)
            ws.cell(5, 4 + 2 * j, f'=COUNTIF($G$8:$G$200,"{cat}")').font = Font(name="Arial", size=9)
        ws.append([])
        ws.append(hdr)
        style_header(ws[7])
        for n, (q, rest, grund, interessen, per) in enumerate(R, start=1):
            bet, befund, einord, regel, link, conf, luecke = per[g]
            if einord == UK and regel == "U2":
                inter = "–"
            else:
                inter = interessen
            stand = STAND if link and "geo.admin" in link else "gemäss Quelle"
            ws.append([n, q, rest, grund, bet, befund, einord, regel, inter, link, stand, conf, luecke or "–"])
            row = ws.max_row
            ws.cell(row, 7).fill = PatternFill("solid", fgColor=FILL[einord])
            if link:
                ws.cell(row, 10).hyperlink = link
        style_body(ws, 8, ws.max_row, len(hdr))
        for col, w in zip("ABCDEFGHIJKLM", (5, 6, 30, 26, 9, 40, 22, 7, 42, 34, 12, 11, 34)):
            ws.column_dimensions[col].width = w
        ws.freeze_panes = "D8"
        ws.auto_filter.ref = f"A7:M{ws.max_row}"

    # 14 Datenanfrage
    ws = new_sheet(wb, "14_Q_Datenanfrage")
    title(ws, "14 · Datenanfrage Q – Daten, die Gemeinde oder Kanton liefern müssen",
          f"Stand {STAND} · Bis zur Lieferung gelten die betroffenen Einordnungen als vorläufig")
    ws.append([])
    ws.append(["Q", "Benötigte Daten", "Gemeinde(n)", "Lieferant", "Bezugsweg", "Priorität"])
    style_header(ws[4])
    for d in DATENANFRAGE:
        ws.append(list(d))
    style_body(ws, 5, ws.max_row, 6)
    for col, w in zip("ABCDEF", (8, 60, 24, 26, 28, 10)):
        ws.column_dimensions[col].width = w

    # 15 Recherchevorgehen
    ws = new_sheet(wb, "15_Recherchevorgehen")
    title(ws, "15 · Recherchevorgehen Q – wiederholbar und automatisierbar",
          f"Stand {STAND} · Alle Runner liegen im Repository halterniklas/Geodaten-in-Gemeinden (.github/workflows)")
    ws.append([])
    ws.append(["Schritt", "Arbeitsschritt", "Vorgehen", "Werkzeug / Quelle", "Automatisierbar", "Verlässlichkeit"])
    style_header(ws[4])
    for v in VORGEHEN:
        ws.append(list(v))
    style_body(ws, 5, ws.max_row, 6)
    for col, w in zip("ABCDEF", (8, 24, 70, 40, 18, 30)):
        ws.column_dimensions[col].width = w

    # Übersicht ergänzen (Zeilen 13/14 sind im Aufbau-Block frei)
    ov = wb["Übersicht"]
    for row, (a, b) in zip((13, 14), (
            ("9_Linkpruefung", "Protokoll der Linkprüfung (GitHub-Runner) mit Ergebnis je Link"),
            ("10–15 Q-Profil", "Q-Einordnungslogik, Q-Restriktionsprofile Münchenstein / Wil / Seelisberg, "
                               "Datenanfrage Q, Recherchevorgehen"))):
        for col, v in ((1, a), (2, b)):
            ov.cell(row, col, v)
            ov.cell(row, col)._style = ov.cell(12, col)._style
    wb.save(path)
    print("ok")


if __name__ == "__main__":
    main()
