# ==============================================================================
# 02_aufbereitung.R – Rohdaten -> Analysedaten (data/processed/*.csv)
#   1) BFS STATPOP (Bevölkerung, Altersstruktur) und Gemeindeliste/Zentren
#   2) Gemeindefinanzen SG (RMSG-Kennzahlen), BL (Konten HRM2), UR (PDF-Kennzahlen)
#   3) ARE Bauzonenstatistik 2022
#   4) Verknüpfung + Dateninventur (Abdeckung, Fehlwerte, methodische Brüche)
# Es werden keine Werte erfunden; fehlende Variablen bleiben NA und werden
# in der Dateninventur ausgewiesen.
# ==============================================================================
source("R/00_setup.R")
suppressPackageStartupMessages({library(readxl); library(pdftools); library(sf)})

# ------------------------------------------------------------------------------
# 1) Bevölkerung (BFS STATPOP, Tabelle px-x-0102010000_101, ständige Wohnbevölkerung)
# ------------------------------------------------------------------------------
lies_pop <- function(jahr) {
  f <- p_raw(sprintf("bfs_statpop_sg_bl_ur_%d.csv", jahr))
  if (!file.exists(f)) stop("Fehlt: ", f, " (siehe R/01_download.R)")
  x <- read_csv(f, locale = locale(encoding = "latin1"), show_col_types = FALSE, progress = FALSE)
  altersspalten <- grep("Jahr", names(x), value = TRUE)
  altersspalten <- altersspalten[!altersspalten %in% "Jahr"]
  alter <- suppressWarnings(as.integer(str_extract(altersspalten, "^[0-9]+")))
  m <- as.matrix(x[, altersspalten])
  tibble(
    jahr     = as.integer(jahr),
    bfs_nr   = as.integer(str_match(x[[2]], "^\\.+([0-9]{4})")[, 2]),
    gemeinde = str_trim(str_replace(x[[2]], "^\\.+[0-9]{4}\\s+", "")),
    pop      = rowSums(m, na.rm = TRUE),
    pop_u20  = rowSums(m[, alter < 20, drop = FALSE], na.rm = TRUE),
    pop_65p  = rowSums(m[, alter >= 65, drop = FALSE], na.rm = TRUE)
  )
}
pop <- map_dfr(2010:2025, lies_pop) %>%
  mutate(anteil_u20 = 100 * pop_u20 / pop, anteil_65p = 100 * pop_65p / pop)
stopifnot(!anyNA(pop$bfs_nr), all(pop$pop > 0))

# Gemeindegrenzen BFS (generalisiert, Gebietsstand 1.1.2025): Kanton, Zentrum, Geometrie
zip_gg <- p_raw("bfs_gemeindegrenzen_gg25.zip")
tmp_gg <- file.path(tempdir(), "gg25"); dir.create(tmp_gg, showWarnings = FALSE)
unzip(zip_gg, exdir = tmp_gg)
f_geo <- list.files(tmp_gg, pattern = "^Communes_K4_20250101_2056\\.geojson$", recursive = TRUE, full.names = TRUE)
stopifnot(length(f_geo) == 1)
geo <- st_read(f_geo, quiet = TRUE)
if (is.na(st_crs(geo)) || st_crs(geo)$epsg != 2056) {
  bb <- st_bbox(geo)
  geo <- if (bb["xmax"] > 1e5) st_set_crs(geo, 2056) else st_transform(geo, 2056)
}
geo <- geo %>% transmute(bfs_nr = as.integer(GDENR), gemeinde_geo = GDENAME,
                         kanton = KTKZ, flaeche_ha = AREA_HA,
                         x_lv95 = as.numeric(E_CNTR), y_lv95 = as.numeric(N_CNTR))
gemeinden <- geo %>% st_drop_geometry() %>%
  filter(bfs_nr %in% unique(pop$bfs_nr)) %>%
  left_join(distinct(pop, bfs_nr, gemeinde), by = "bfs_nr")
stopifnot(nrow(gemeinden) == n_distinct(pop$bfs_nr), all(gemeinden$kanton %in% CFG$kantone))
geo_sel <- geo %>% filter(bfs_nr %in% gemeinden$bfs_nr)
saveRDS(geo_sel, p_proc("gemeindegrenzen_sg_bl_ur.rds"))

pop <- pop %>% left_join(select(gemeinden, bfs_nr, kanton), by = "bfs_nr")
pop <- pop %>% group_by(bfs_nr) %>% arrange(jahr, .by_group = TRUE) %>%
  mutate(pop_t5 = lag(pop, 5),
         wachstum5 = 100 * ((pop / pop_t5)^(1/5) - 1)) %>% ungroup()
write_csv(pop, p_proc("bevoelkerung_statpop_2010_2025.csv"))
write_csv(gemeinden, p_proc("gemeinden_stamm.csv"))

# Namens-Schlüssel (Verknüpfung SG/UR, deren Quellen keine BFS-Nummer enthalten)
schluessel <- gemeinden %>% transmute(kanton, bfs_nr, name_key = norm_name(gemeinde))
stopifnot(!anyDuplicated(schluessel[, c("kanton", "name_key")]))

# ------------------------------------------------------------------------------
# 2a) St. Gallen: Kennzahlen RMSG je Gemeinde (Blätter 2017–2025)
# ------------------------------------------------------------------------------
lies_sg_blatt <- function(blatt) {
  f <- p_raw("sg_kennzahlen_rmsg.xlsx")
  x <- suppressMessages(read_excel(f, sheet = blatt, col_names = FALSE, .name_repair = "minimal"))
  kopf <- which(str_detect(replace_na(as.character(x[[2]]), ""), "Wohn"))[1]
  hdr <- str_replace_all(replace_na(as.character(unlist(x[kopf, ])), ""), "[-\\s]+", "")
  col <- function(muster, ausschluss = NULL) {
    i <- which(str_detect(hdr, regex(muster, ignore_case = TRUE)))
    if (!is.null(ausschluss)) i <- i[!str_detect(hdr[i], regex(ausschluss, ignore_case = TRUE))]
    if (length(i) == 0) NA_integer_ else i[1]
  }
  cm <- c(pop = col("Wohnbev"), steuerfuss = col("steuerfuss"), einfache_steuer_je_ew = col("EinfacheSteuer"),
          op_ergebnis = col("OperativesErgebnis"), nvq = col("Nettoverschuldungsquotient"),
          sfg = col("Selbstfinanzierungsgrad", "Fünfjahres|Funfjahres|durchschnitt"),
          zins = col("Zinsbelastungsanteil"), nettoschuld1_je_ew = col("NettoschuldIje"),
          nettoschuld2_je_ew = col("NettoschuldIIje"), sfa = col("Selbstfinanzierungsanteil"))
  d <- x[(kopf + 1):nrow(x), , drop = FALSE]
  name <- as.character(d[[1]])
  out <- tibble(jahr = as.integer(blatt), gemeinde_quelle = name)
  for (k in names(cm)) out[[k]] <- if (is.na(cm[[k]])) NA_real_ else suppressWarnings(as.numeric(unlist(d[[cm[[k]]]])))
  out %>% filter(!is.na(gemeinde_quelle), !is.na(pop),
                 !str_detect(gemeinde_quelle, "^(Wahlkreis|Total|Kanton|Region)"))
}
blaetter_sg <- excel_sheets(p_raw("sg_kennzahlen_rmsg.xlsx"))
sg_roh <- map_dfr(blaetter_sg, lies_sg_blatt) %>% mutate(name_key = norm_name(gemeinde_quelle))
sg <- sg_roh %>% left_join(filter(schluessel, kanton == "SG"), by = "name_key")
sg_unverknuepft <- sg %>% filter(is.na(bfs_nr)) %>% count(gemeinde_quelle, name = "n_jahre") %>%
  mutate(kanton = "SG", grund = "nicht im aktuellen Gebietsstand 2025 (Fusion) bzw. Namensabweichung")
sg <- sg %>% filter(!is.na(bfs_nr)) %>%
  transmute(kanton = "SG", bfs_nr, jahr, pop_quelle = pop, sfa, sfg, nettoschuld_je_ew = nettoschuld1_je_ew,
            nettoschuld_def = "Nettoschuld I je Einwohner (RMSG)", steuer_je_ew = einfache_steuer_je_ew,
            steuer_def = "Einfache Steuer (100 %) je Einwohner (RMSG)", steuerfuss, quelle = "sg_kennzahlen_rmsg.xlsx")

# ------------------------------------------------------------------------------
# 2b) Basel-Landschaft: Kennzahlen aus Kontenebene (HRM2, Gesamthaushalt)
#     Definition gemäss Finanzhandbuch BL, Kap. 16 (siehe Quellenprotokoll)
# ------------------------------------------------------------------------------
bl_roh <- read_delim(p_raw("bl_dataset_10640.csv"), delim = ";", col_types = cols(.default = "c"),
                     progress = FALSE, show_col_types = FALSE) %>%
  transmute(jahr = as.integer(jahr), bfs_nr = as.integer(bfs_nummer), rt = rechnungsteil,
            konto = kontenart_nr, betrag = as.numeric(betrag_chf))
summe <- function(d, rt, praefix) {
  d %>% filter(rt == !!rt, str_detect(konto, paste0("^(", paste(praefix, collapse = "|"), ")"))) %>%
    group_by(jahr, bfs_nr) %>% summarise(v = sum(betrag, na.rm = TRUE), .groups = "drop")
}
komp <- function(rt, praefix, name) summe(bl_roh, rt, praefix) %>% rename(!!name := v)
bl_k <- reduce(list(
  komp("Erfolgsrechnung", "3", "aufwand"), komp("Erfolgsrechnung", "4", "ertrag"),
  komp("Erfolgsrechnung", "33", "k33"),   komp("Erfolgsrechnung", "35", "k35"),
  komp("Erfolgsrechnung", "364", "k364"), komp("Erfolgsrechnung", "365", "k365"),
  komp("Erfolgsrechnung", "366", "k366"), komp("Erfolgsrechnung", "389", "k389"),
  komp("Erfolgsrechnung", "4391", "k4391"), komp("Erfolgsrechnung", "4490", "k4490"),
  komp("Erfolgsrechnung", "45", "k45"),   komp("Erfolgsrechnung", "489", "k489"),
  komp("Erfolgsrechnung", c("40", "41", "42", "43", "44", "45", "46", "484"), "laufender_ertrag"),
  komp("Erfolgsrechnung", "40", "fiskalertrag"),
  komp("Bilanz", "20", "fremdkapital"), komp("Bilanz", "10", "finanzvermoegen")
), full_join, by = c("jahr", "bfs_nr")) %>%
  mutate(across(-c(jahr, bfs_nr), ~ replace_na(.x, 0))) %>%
  mutate(selbstfinanzierung = ertrag - aufwand + k33 + k35 + k364 + k365 + k366 + k389 -
           k4391 - k4490 - k45 - k489,
         sfa = 100 * selbstfinanzierung / laufender_ertrag)
bl <- bl_k %>%
  left_join(select(pop, bfs_nr, jahr, pop), by = c("bfs_nr", "jahr")) %>%
  transmute(kanton = "BL", bfs_nr, jahr, pop_quelle = NA_real_, sfa, sfg = NA_real_,
            nettoschuld_je_ew = (fremdkapital - finanzvermoegen) / pop,
            nettoschuld_def = "(Fremdkapital 20 - Finanzvermögen 10) / Einwohner (FHB BL 16.5)",
            steuer_je_ew = fiskalertrag / pop,
            steuer_def = "Fiskalertrag (Konten 40) je Einwohner – satzabhängig",
            steuerfuss = NA_real_, quelle = "bl_dataset_10640.csv (data.bl.ch, Dataset 10640)") %>%
  filter(bfs_nr %in% schluessel$bfs_nr[schluessel$kanton == "BL"])

# ------------------------------------------------------------------------------
# 2c) Uri: Kennzahlen aus den PDF-Berichten der Finanzkontrolle Uri
# ------------------------------------------------------------------------------
zahl <- function(t) {
  t <- str_replace_all(t, "[‘’'`´]", "")
  t <- str_replace_all(t, "[‐‑‒–−]", "-")
  ifelse(t %in% c("-", "", "–"), NA_real_, suppressWarnings(as.numeric(t)))
}
parse_ur_tabelle <- function(seite_text) {
  # liefert je Gemeinde und Jahr v1 (erste Spalte des Jahres) und v2 (zweite Spalte, falls vorhanden)
  zeilen <- str_split(seite_text, "\n")[[1]]
  kopf <- zeilen[str_detect(zeilen, "^\\s*Gemeinde\\s+[0-9]{4}")][1]
  jahre <- as.integer(str_extract_all(kopf, "[0-9]{4}")[[1]])
  res <- list()
  for (z in zeilen) {
    tok <- str_split(str_squish(z), " ")[[1]]
    name <- tok[1]
    if (length(tok) < 1 + length(jahre) || name %in% c("Gemeinde", "Total", "in", "absolut")) next
    werte <- zahl(tok[-1])
    k <- length(werte) / length(jahre)
    if (!k %in% c(1, 2)) next
    res[[length(res) + 1]] <- tibble(gemeinde_quelle = name, jahr = jahre,
                                     v1 = werte[seq(1, length(werte), by = k)],
                                     v2 = if (k == 2) werte[seq(2, length(werte), by = 2)] else NA_real_)
  }
  bind_rows(res)
}
ur_pdfs <- list.files(PATH$raw, pattern = "^ur_gemeindefinanzstatistik_[0-9]{4}\\.pdf$", full.names = TRUE)
ur_liste <- list()
for (f in ur_pdfs) {
  berichtsjahr <- as.integer(str_extract(basename(f), "[0-9]{4}"))
  s <- pdf_text(f)
  kopf <- vapply(s, function(t) { z <- str_squish(str_split(t, "\n")[[1]]); paste(head(z[nzchar(z)], 3), collapse = " ") }, "")
  i_sfa <- which(str_detect(kopf, "Entwicklung Kennzahl: Selbstfinanzierungsanteil"))
  i_ns2 <- which(str_detect(kopf, "Entwicklung Kennzahl: Nettoschuld II"))
  i_sfg <- which(str_detect(kopf, "Entwicklung Kennzahl: Selbstfinanzierungsgrad"))
  if (length(i_sfa) == 0) next          # ältere Berichte ohne Kennzahlen-Zeitreihe
  a <- parse_ur_tabelle(s[i_sfa[1]]) %>% transmute(gemeinde_quelle, jahr, sfa = v2)
  b <- if (length(i_ns2)) parse_ur_tabelle(s[i_ns2[1]]) %>% transmute(gemeinde_quelle, jahr, nettoschuld_je_ew = v2) else NULL
  g <- if (length(i_sfg)) parse_ur_tabelle(s[i_sfg[1]]) %>% transmute(gemeinde_quelle, jahr, sfg = v1) else NULL
  d <- a
  if (!is.null(b)) d <- left_join(d, b, by = c("gemeinde_quelle", "jahr"))
  if (!is.null(g)) d <- left_join(d, g, by = c("gemeinde_quelle", "jahr"))
  ur_liste[[length(ur_liste) + 1]] <- mutate(d, bericht = berichtsjahr)
}
ur_roh <- bind_rows(ur_liste)
# je Gemeinde und Jahr gilt der Wert des jüngsten Berichts (Revisionen werden übernommen)
ur_roh <- ur_roh %>% arrange(gemeinde_quelle, jahr, desc(bericht)) %>%
  distinct(gemeinde_quelle, jahr, .keep_all = TRUE) %>% mutate(name_key = norm_name(gemeinde_quelle))
ur_revisionen <- bind_rows(ur_liste) %>% group_by(gemeinde_quelle, jahr) %>%
  summarise(n_berichte = n(), sfa_min = min(sfa, na.rm = TRUE), sfa_max = max(sfa, na.rm = TRUE), .groups = "drop") %>%
  filter(n_berichte > 1, abs(sfa_max - sfa_min) > 0.05)
ur <- ur_roh %>% left_join(filter(schluessel, kanton == "UR"), by = "name_key")
ur_unverknuepft <- ur %>% filter(is.na(bfs_nr)) %>% count(gemeinde_quelle, name = "n_jahre") %>%
  mutate(kanton = "UR", grund = "nicht im aktuellen Gebietsstand 2025 (Fusion Bauen -> Seedorf 2021)")
if (!"nettoschuld_je_ew" %in% names(ur)) ur$nettoschuld_je_ew <- NA_real_
if (!"sfg" %in% names(ur)) ur$sfg <- NA_real_
ur <- ur %>% filter(!is.na(bfs_nr)) %>%
  transmute(kanton = "UR", bfs_nr, jahr, pop_quelle = NA_real_, sfa, sfg, nettoschuld_je_ew,
            nettoschuld_def = "Nettoschuld II je Einwohner (Nettolast) – NICHT vergleichbar mit SG/BL",
            steuer_je_ew = NA_real_, steuer_def = "nicht verfügbar", steuerfuss = NA_real_,
            quelle = "ur_gemeindefinanzstatistik_<Jahr>.pdf")

# ------------------------------------------------------------------------------
# 3) ARE Bauzonenstatistik 2022 (Gebietsstand 1.1.2022; Flächen in Hektaren)
# ------------------------------------------------------------------------------
bz_roh <- read_excel(p_raw("are_bzs2022_gemeinden.xlsx"), sheet = "Statistik_Hauptnutzung")
hn <- grep("^HN_", names(bz_roh), value = TRUE)
bauzonen <- bz_roh %>%
  transmute(bfs_nr = as.integer(Gem_No), name_are = Name, kt_are = Kt_Kz,
            across(all_of(hn), ~ replace_na(as.numeric(.x), 0))) %>%
  mutate(bauzone_ha = rowSums(across(all_of(hn)))) %>%
  filter(kt_are %in% CFG$kantone)
bauzonen <- bauzonen %>% left_join(filter(pop, jahr == CFG$bauzonen_jahr - 1) %>% select(bfs_nr, pop_stichtag = pop), by = "bfs_nr") %>%
  mutate(bauzone_m2_je_ew = bauzone_ha * 10000 / pop_stichtag)
bz_nicht_verknuepft <- anti_join(bauzonen, gemeinden, by = "bfs_nr")
bz_fehlt <- anti_join(gemeinden, bauzonen, by = "bfs_nr")
bauzonen <- semi_join(bauzonen, gemeinden, by = "bfs_nr")
write_csv(bauzonen, p_proc("bauzonen_2022_gemeinden.csv"))

# ------------------------------------------------------------------------------
# 4) Panel Gemeindejahre
# ------------------------------------------------------------------------------
# Erste Jahre mit konsistenter Kennzahlenreihe (Begründung: R/02 Abschnitt "Methodische Brüche"
# und output/tables/inventur_methodische_brueche.csv)
MODELL_START <- c(SG = 2019L, BL = 2015L, UR = 2014L)
fin <- bind_rows(sg, bl, ur) %>% select(-pop_quelle)
panel <- fin %>%
  inner_join(select(pop, bfs_nr, jahr, pop, anteil_u20, anteil_65p, wachstum5), by = c("bfs_nr", "jahr")) %>%
  left_join(select(gemeinden, bfs_nr, gemeinde, x_lv95, y_lv95), by = "bfs_nr") %>%
  mutate(log_pop = log(pop),
         ziel = bfs_nr %in% CFG$ziel_bfs,
         ziel_label = unname(CFG$ziel_label[as.character(bfs_nr)]),
         # Rechnungsmodell/Methodik: erstes Jahr mit konsistenter, vollständiger Kennzahlenreihe
         modell_start = unname(MODELL_START[kanton]),
         modell_ok = jahr >= modell_start & !is.na(sfa) & !is.na(wachstum5))
write_csv(panel, p_proc("panel_gemeindejahre.csv"))

# Querschnitt Untersuchung B (Bauzonen-Erhebungsstand 1.1.2022)
fin_b <- fin %>% filter(jahr %in% CFG$bauzonen_fin_robust) %>% group_by(kanton, bfs_nr) %>%
  summarise(sfa_2022 = sfa[jahr == CFG$bauzonen_fin_jahr][1],
            sfa_mittel_2021_23 = if (sum(!is.na(sfa)) == 3) mean(sfa) else NA_real_,
            nettoschuld_2022 = nettoschuld_je_ew[jahr == CFG$bauzonen_fin_jahr][1],
            nettoschuld_def = nettoschuld_def[1],
            steuer_je_ew_2022 = steuer_je_ew[jahr == CFG$bauzonen_fin_jahr][1], .groups = "drop")
pop_b <- pop %>% filter(jahr == CFG$bauzonen_jahr - 1) %>%
  select(bfs_nr, pop_2021 = pop, anteil_u20_2021 = anteil_u20, anteil_65p_2021 = anteil_65p, wachstum5_2021 = wachstum5)
quer_b <- gemeinden %>% select(bfs_nr, gemeinde, kanton, x_lv95, y_lv95) %>%
  left_join(fin_b %>% select(-kanton), by = "bfs_nr") %>%
  left_join(pop_b, by = "bfs_nr") %>%
  left_join(select(bauzonen, bfs_nr, bauzone_ha, bauzone_m2_je_ew), by = "bfs_nr") %>%
  mutate(log_pop = log(pop_2021), ziel = bfs_nr %in% CFG$ziel_bfs,
         ziel_label = unname(CFG$ziel_label[as.character(bfs_nr)]))
write_csv(quer_b, p_proc("querschnitt_bauzonen_2022.csv"))

# ------------------------------------------------------------------------------
# 5) Dateninventur-Tabellen
# ------------------------------------------------------------------------------
inv_abdeckung <- fin %>% group_by(kanton) %>%
  summarise(gemeinden = n_distinct(bfs_nr), jahr_min = min(jahr), jahr_max = max(jahr),
            gemeindejahre = n(), sfa_vorhanden = sum(!is.na(sfa)),
            nettoschuld_vorhanden = sum(!is.na(nettoschuld_je_ew)),
            steuer_vorhanden = sum(!is.na(steuer_je_ew)), .groups = "drop")
write_tab(inv_abdeckung, "inventur_finanzabdeckung_kanton.csv")

inv_jahre <- fin %>% group_by(kanton, jahr) %>%
  summarise(gemeinden = n_distinct(bfs_nr), sfa_fehlend = sum(is.na(sfa)), .groups = "drop")
write_tab(inv_jahre, "inventur_finanz_gemeinden_je_jahr.csv")

inv_fehlwerte <- panel %>% group_by(kanton) %>%
  summarise(across(c(sfa, nettoschuld_je_ew, steuer_je_ew, wachstum5, anteil_u20, anteil_65p),
                   ~ sum(is.na(.x)), .names = "fehlend_{.col}"), n = n(), .groups = "drop")
write_tab(inv_fehlwerte, "inventur_fehlwerte_panel.csv")

inv_unverknuepft <- bind_rows(sg_unverknuepft, ur_unverknuepft) %>%
  bind_rows(tibble(kanton = character(), gemeinde_quelle = character(), n_jahre = integer(), grund = character()))
write_tab(inv_unverknuepft, "inventur_nicht_verknuepfte_gemeinden.csv")
write_tab(ur_revisionen, "inventur_ur_revidierte_werte.csv")

inv_brueche <- tribble(
  ~kanton, ~thema, ~befund, ~behandlung, ~quelle,
  "SG", "Rechnungsmodell", "RMSG-Kennzahlenblätter 2017 und 2018 sind nur für wenige Gemeinden befüllt (2017: 1, 2018: 11 Gemeinden); vollständig ab 2019.",
        "Analysefenster SG ab 2019.", "sg_kennzahlen_rmsg.xlsx, Blätter 2017–2025",
  "SG", "Definition Selbstfinanzierungsanteil", "Änderungsprotokoll der Kennzahlenberechnung RMSG: «Anpassung Definition der Kennzahl Selbstfinanzierungsanteil» in Version 1.2 (Stand 06.2025). Ob veröffentlichte Altwerte rückwirkend neu berechnet wurden, ist aus den Quellen nicht ersichtlich.",
        "Als möglicher methodischer Bruch markiert; nicht korrigierbar; im Bericht als Unsicherheit ausgewiesen.", "sg_kennzahlenberechnung_rmsg_v1_2.xlsx, Blatt Eingabemaske",
  "SG", "Gebietsstand", "Fusionen im Beobachtungsfenster (Hemberg, Oberhelfenschwil u. a. -> Neckertal): Vor-Fusions-Einheiten sind nicht im Gebietsstand 2025 und werden nicht mit BFS-Nummern verknüpft.",
        "Betroffene Gemeindejahre ausgeschlossen (siehe inventur_nicht_verknuepfte_gemeinden.csv).", "BFS Gemeindegrenzen gg25",
  "BL", "Rechnungsmodell", "Daten HRM2 ab 2015 (Dataset 10640); Gesamthaushalt inkl. Spezialfinanzierungen. Kennzahlen werden aus Konten gemäss Finanzhandbuch BL Kap. 16 selbst berechnet.",
        "Analysefenster BL ab 2015.", "data.bl.ch Dataset 10640; Finanzhandbuch BL Kap. 16",
  "UR", "Rechnungsmodell", "Umstellung auf HRM2 am 1.1.2012; Kennzahlen ab 2014 nach überarbeiteter Fachempfehlung berechnet (Hinweis in den Berichten 2015–2020).",
        "Analysefenster UR ab 2014 (Wachstumsvariable beschränkt faktisch auf >= 2015).", "ur_gemeindefinanzstatistik_2015.pdf, _2018.pdf",
  "UR", "Gebietsstand", "Bauen fusioniert 2021 mit Seedorf; Bauen ist nicht im Gebietsstand 2025.", "Bauen ausgeschlossen.", "BFS Gemeindegrenzen gg25",
  "UR", "Nettoschuld", "Nur Nettoschuld II (Nettolast) je Einwohner veröffentlicht; nicht vergleichbar mit Nettoschuld I (SG, BL).",
        "UR in Nettoschuld-Analyse (B sekundär) nicht verwendet.", "ur_gemeindefinanzstatistik_2025.pdf, Kennzahlen S. 14ff.",
  "UR", "Steuerkraft", "In den veröffentlichten Kennzahlentabellen kein Fiskalertrag/Steuerkraft je Gemeinde.", "Steuerkraft-Kontrolle für UR nicht verfügbar; keine Ersatzgrösse.", "ur_gemeindefinanzstatistik_2025.pdf",
  "SG/BL", "Steuerkraft", "SG: einfache Steuer (100 %) je Einwohner; BL: Fiskalertrag je Einwohner (satzabhängig). Beide kantonsspezifisch und nicht direkt vergleichbar; kein einheitlicher Steuerkraftindex in den Quellen.",
        "Nur in kantonalen Sensitivitätsmodellen, nicht in gepoolten Modellen.", "RMSG-Kennzahlen (SG); data.bl.ch 10640 (BL)",
  "alle", "Bevölkerung", "BFS-Tabelle liefert Bevölkerung im Gebietsstand 2025 rückwirkend (fusionierte Gemeinden werden zusammengefasst).", "Wachstum je Gemeinde im aktuellen Gebietsstand.", "BFS px-x-0102010000_101"
)
write_tab(inv_brueche, "inventur_methodische_brueche.csv")

inv_bz <- tibble(
  gemeinden_gesamt = nrow(gemeinden), mit_bauzonen = n_distinct(bauzonen$bfs_nr),
  ohne_bauzonen = nrow(bz_fehlt), are_ohne_bfs_treffer = nrow(bz_nicht_verknuepft))
write_tab(inv_bz, "inventur_bauzonen_verknuepfung.csv")

cat("\n== Aufbereitung abgeschlossen ==\n")
print(inv_abdeckung)
cat("Panel Gemeindejahre:", nrow(panel), " | im Modellbereich (modell_ok):", sum(panel$modell_ok), "\n")
print(panel %>% filter(modell_ok) %>% group_by(kanton) %>% summarise(gemeinden = n_distinct(bfs_nr), beobachtungen = n(), jahre = paste(range(jahr), collapse = "-")))
cat("Querschnitt B:", nrow(quer_b), " | vollständig (SFA 2022 + Bauzonen):",
    sum(complete.cases(quer_b[, c("sfa_2022", "bauzone_m2_je_ew", "wachstum5_2021")])), "\n")
