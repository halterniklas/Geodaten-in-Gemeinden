# ==============================================================================
# 01_download.R – Datenbeschaffung, Quellenprotokoll und Dateninventur der Quellen
#
# Lädt alle Rohdaten nach data/raw/download/ (unverändert, nie überschrieben, ausser force = TRUE).
# Bereits vorhandene Dateien werden übersprungen. Ist eine Quelle nicht erreichbar
# (z. B. Firmen-Firewall), gibt es zwei Wege:
#   a) GitHub Actions: .github/workflows/c1-daten.yml lädt die Rohdaten auf einem GitHub-Runner
#      (Python-Skripte in tools/) und committet sie in data/raw/ (so wurde die Erstbeschaffung gemacht).
#   b) Dateien manuell nach data/raw/download/ legen (Dateinamen siehe data/raw/quellenprotokoll.csv).
# ==============================================================================
source("R/00_setup.R")
force_download <- identical(Sys.getenv("C1_FORCE_DOWNLOAD"), "1")
ua <- httr::user_agent("Mozilla/5.0 (c1-finanzen; reproducible research)")

hole <- function(url, datei, optional = FALSE) {
  ziel <- p_raw(datei)
  if (file.exists(ziel) && !force_download) return(tibble(datei, status = "vorhanden", bytes = file.size(ziel)))
  r <- tryCatch(httr::GET(url, ua, httr::write_disk(ziel, overwrite = TRUE), httr::timeout(600)), error = function(e) e)
  if (inherits(r, "error") || httr::status_code(r) != 200) {
    if (file.exists(ziel)) unlink(ziel)
    msg <- if (inherits(r, "error")) conditionMessage(r) else paste("HTTP", httr::status_code(r))
    (if (optional) message else warning)("Download fehlgeschlagen: ", datei, " (", msg, ")", call. = FALSE)
    return(tibble(datei, status = paste("FEHLER:", msg), bytes = NA_real_))
  }
  tibble(datei, status = "heruntergeladen", bytes = file.size(ziel))
}

# ---- Direkt-URLs ---------------------------------------------------------------------------------------------------
sg_basis <- "https://www.sg.ch/politik-verwaltung/gemeinden/gemeindefinanzen/_jcr_content/Par/sgch_accordion_list_1344425806/AccordionListPar"
direkt <- tribble(
  ~datei, ~url, ~optional,
  "are_bzs2022_gemeinden.xlsx", "https://www.are.admin.ch/dam/de/sd-web/7cEPibyb2l-3/bauzonenstatistik_schweiz_2022_gemeinden.xlsx", FALSE,
  "are_bzs2022_resultate.xlsx", "https://www.are.admin.ch/dam/de/sd-web/uPugMgFnGj0m/bauzonenstatistik_schweiz_2022_resultate.xlsx", TRUE,
  "are_bzs2022_raumgliederung.xlsx", "https://www.are.admin.ch/dam/de/sd-web/lTUT9gVTUx4y/bauzonenstatistik_schweiz_2022_raumgliederung.xlsx", TRUE,
  "are_bzs2022_bericht.pdf", "https://www.are.admin.ch/dam/de/sd-web/AS4q88PlZYXF/bzs_2022.pdf", TRUE,
  "are_bzs2017.zip", "https://www.are.admin.ch/dam/de/sd-web/iLHkdaGp7qi3/Bauzonenstatistik_Schweiz_2017.zip", TRUE,
  "are_bzs2012.zip", "https://www.are.admin.ch/dam/de/sd-web/3lK47686QIeu/Bauzonenstatistik_Schweiz_2012.zip", TRUE,
  "sg_kennzahlen_rmsg.xlsx", paste0(sg_basis, "/sgch_accordion_396006679/AccordionPar/sgch_downloadlist/DownloadListPar/sgch_download.ocFile/Kennzahlen%20neues%20Rechnungslegungsmodell%20der%20St.Galler%20Gemeinden.xlsx"), FALSE,
  "sg_kennzahlenberechnung_rmsg_v1_2.xlsx", paste0(sg_basis, "/sgch_accordion_228014448/AccordionPar/sgch_downloadlist/DownloadListPar/sgch_download_237847518.ocFile/Kennzahlenberechnung%20RMSG%20(Version%201.2).xlsx"), FALSE,
  "sg_detailberechnungen_rmsg.pdf", paste0(sg_basis, "/sgch_accordion_228014448/AccordionPar/sgch_downloadlist/DownloadListPar/sgch_download.ocFile/Detailberechnungen%20Kennzahlen%20RMSG.pdf"), TRUE,
  "bfs_gemeindegrenzen_gg25.zip", "https://dam-api.bfs.admin.ch/hub/api/dam/assets/34367751/master", FALSE,
  "bl_dataset_10640.csv", "https://data.bl.ch/api/explore/v2.1/catalog/datasets/10640/exports/csv?delimiter=%3B&lang=de&timezone=UTC&use_labels=false", FALSE,
  "bl_dataset_10640_meta.json", "https://data.bl.ch/api/explore/v2.1/catalog/datasets/10640", TRUE,
  "bl_dataset_10650.csv", "https://data.bl.ch/api/explore/v2.1/catalog/datasets/10650/exports/csv?delimiter=%3B&lang=de&timezone=UTC&use_labels=false", TRUE,
  "bfs_px_bev_meta.json", "https://www.pxweb.bfs.admin.ch/api/v1/de/px-x-0102010000_101/px-x-0102010000_101.px", FALSE
)
res <- pmap_dfr(direkt, function(datei, url, optional) hole(url, datei, optional) %>% mutate(url = url))

# ---- Uri: Berichte der Finanzkontrolle (Dokumentnummern aus der Publikationsseite) ------------------------------------------------
ur_seite <- tryCatch(httr::content(httr::GET("https://www.ur.ch/publikationen/6680", ua, httr::timeout(120)), as = "text", encoding = "UTF-8"), error = function(e) "")
ur_doc <- str_match_all(ur_seite, '<a title="Jahr ([0-9]{4})" href="(/_doc/[0-9]+)"')[[1]]
if (nrow(ur_doc) == 0 && !any(file.exists(list.files(PATH$raw, "^ur_gemeindefinanzstatistik", full.names = TRUE)))) warning("Uri-Publikationsseite nicht lesbar und keine UR-PDFs vorhanden.")
res_ur <- if (nrow(ur_doc) > 0) {
  map_dfr(unique(split(ur_doc[, 2:3, drop = FALSE], seq_len(nrow(ur_doc)))), function(z) {
    hole(paste0("https://www.ur.ch", z[[2]]), sprintf("ur_gemeindefinanzstatistik_%s.pdf", z[[1]]), optional = TRUE) %>% mutate(url = paste0("https://www.ur.ch", z[[2]]))
  })
} else tibble()

# ---- BFS PxWeb (STATPOP, px-x-0102010000_101): Gemeinden SG/BL/UR, je Jahr, alle Alter -----------------------------------------------------------
px <- "https://www.pxweb.bfs.admin.ch/api/v1/de/px-x-0102010000_101/px-x-0102010000_101.px"
res_px <- tibble()
if (file.exists(p_raw("bfs_px_bev_meta.json"))) {
  meta <- jsonlite::fromJSON(p_raw("bfs_px_bev_meta.json"), simplifyVector = FALSE)
  vm <- setNames(meta$variables, vapply(meta$variables, `[[`, "", "code"))
  gcode <- "Kanton (-) / Bezirk (>>) / Gemeinde (......)"
  codes <- unlist(vm[[gcode]]$values); texte <- unlist(vm[[gcode]]$valueTexts)
  kt <- NA_character_; sel <- character()
  for (i in seq_along(codes)) {
    if (startsWith(texte[i], "- ")) kt <- texte[i]
    else if (startsWith(texte[i], "......") && kt %in% c("- St. Gallen", "- Basel-Landschaft", "- Uri")) sel <- c(sel, codes[i])
  }
  alter <- setdiff(unlist(vm[["Alter"]]$values), "-99999")
  res_px <- map_dfr(unlist(vm[["Jahr"]]$values), function(j) {
    datei <- sprintf("bfs_statpop_sg_bl_ur_%s.csv", j)
    if (file.exists(p_raw(datei)) && !force_download) return(tibble(datei, status = "vorhanden", bytes = file.size(p_raw(datei)), url = px))
    q <- list(query = list(
      list(code = "Jahr", selection = list(filter = "item", values = list(j))),
      list(code = gcode, selection = list(filter = "item", values = as.list(sel))),
      list(code = "Bevölkerungstyp", selection = list(filter = "item", values = list("1"))),
      list(code = "Staatsangehörigkeit (Kategorie)", selection = list(filter = "item", values = list("-99999"))),
      list(code = "Geschlecht", selection = list(filter = "item", values = list("-99999"))),
      list(code = "Alter", selection = list(filter = "item", values = as.list(alter)))),
      response = list(format = "csv"))
    r <- tryCatch(httr::POST(px, ua, body = jsonlite::toJSON(q, auto_unbox = TRUE), httr::content_type_json(), httr::timeout(300)), error = function(e) e)
    if (inherits(r, "error") || httr::status_code(r) != 200) { warning("PxWeb-Abfrage fehlgeschlagen: ", j, call. = FALSE); return(tibble(datei, status = "FEHLER", bytes = NA_real_, url = px)) }
    writeBin(httr::content(r, "raw"), p_raw(datei)); Sys.sleep(1)
    tibble(datei, status = "heruntergeladen", bytes = file.size(p_raw(datei)), url = px)
  })
}

digest_sha256 <- function(f) {
  if (requireNamespace("digest", quietly = TRUE)) digest::digest(f, algo = "sha256", file = TRUE)
  else unname(tools::md5sum(f))          # Fallback: MD5 (Paket digest nicht installiert)
}

# ---- Quellenprotokoll ---------------------------------------------------------------------------------------------------------------------------------
logs <- list.files(PATH$raw_probe, "summary2?\\.json$", full.names = TRUE)
abruf_runner <- tryCatch(max(c(jsonlite::fromJSON(file.path(PATH$raw_probe, "summary2.json"))$retrieved,
                              jsonlite::fromJSON(p_raw("_fetch4_log.json"))$retrieved), na.rm = TRUE), error = function(e) NA_character_)
proto <- bind_rows(res, res_ur, res_px) %>%
  mutate(abrufdatum_dieser_lauf = format(Sys.time(), "%Y-%m-%d %H:%M %Z"),
         abrufdatum_github_runner_utc = abruf_runner,
         groesse_mb = round(bytes / 1e6, 2), sha256 = vapply(datei, function(f) if (file.exists(p_raw(f))) digest_sha256(p_raw(f)) else NA_character_, ""))
readr::write_csv(proto, "data/raw/quellenprotokoll.csv", na = "")
cat("Quellenprotokoll geschrieben:", nrow(proto), "Dateien;", sum(grepl("FEHLER", proto$status)), "Fehler\n")
