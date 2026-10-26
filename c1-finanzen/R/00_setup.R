# ==============================================================================
# 00_setup.R  –  Pakete, Pfade, Konfiguration, Zufallsseed
# Wird von allen anderen Skripten per source("R/00_setup.R") geladen.
# Arbeitsverzeichnis = Projektordner (RStudio: .Rproj öffnen).
# ==============================================================================

options(stringsAsFactors = FALSE, scipen = 999, warn = 1, width = 120, encoding = "UTF-8")
# UTF-8-Locale sicherstellen (Umlaute in Namen, Beschriftungen und CSV-Dateien)
if (!l10n_info()[["UTF-8"]]) {
  for (loc in c("de_CH.UTF-8", "de_DE.UTF-8", "en_US.UTF-8", "C.UTF-8")) {
    if (nzchar(suppressWarnings(Sys.setlocale("LC_CTYPE", loc)))) break
  }
}

pakete <- c("dplyr", "tidyr", "readr", "readxl", "stringr", "purrr", "tibble",
            "ggplot2", "scales", "sf", "pdftools", "jsonlite", "httr",
            "ranger", "mgcv", "xgboost", "sandwich", "lmtest", "spdep",
            "knitr", "rmarkdown")
fehlend <- pakete[!vapply(pakete, requireNamespace, logical(1), quietly = TRUE)]
if (length(fehlend) > 0) {
  stop("Fehlende Pakete: ", paste(fehlend, collapse = ", "),
       "\nInstallation: install.packages(c(", paste0('"', fehlend, '"', collapse = ", "), "))",
       "\noder renv::restore() (siehe README).", call. = FALSE)
}
suppressPackageStartupMessages({
  library(dplyr); library(tidyr); library(readr); library(stringr)
  library(purrr); library(tibble); library(ggplot2)
})

# --- Konfiguration -------------------------------------------------------------
CFG <- list(
  seed            = 20261026L,           # globaler Zufallsseed
  k_outer         = 5L,                  # äussere Folds
  k_inner         = 3L,                  # innere Folds (Tuning)
  n_boot          = 2000L,               # Bootstrap über Gemeinden (Differenz der Prognosefehler)
  ziel_bfs        = c(Wil = 3427L, Muenchenstein = 2769L, Seelisberg = 1215L),
  ziel_label      = c(`3427` = "Wil SG", `2769` = "Münchenstein BL", `1215` = "Seelisberg UR"),
  kantone         = c("SG", "BL", "UR"),
  bauzonen_jahr   = 2022L,               # Erhebungsstand ARE (1.1.2022)
  bauzonen_fin_jahr = 2022L,             # Finanzjahr des Querschnitts (Hauptspezifikation)
  bauzonen_fin_robust = 2021:2023,       # Robustheit: Mittel über 3 Jahre
  min_gemeinden_kanton_modell = 30L,     # Mindestzahl Gemeinden für eigenständiges kantonales Modell
  stand_datum     = format(Sys.Date(), "%Y-%m-%d")
)
set.seed(CFG$seed)

# --- Pfade ---------------------------------------------------------------------
PATH <- list(
  raw        = "data/raw/download",
  raw_probe  = "data/raw/_probe",
  processed  = "data/processed",
  tables     = "output/tables",
  figures    = "output/figures",
  models     = "output/models"
)
invisible(lapply(PATH, dir.create, recursive = TRUE, showWarnings = FALSE))

p_raw  <- function(...) file.path(PATH$raw, ...)
p_proc <- function(...) file.path(PATH$processed, ...)
p_tab  <- function(...) file.path(PATH$tables, ...)
p_fig  <- function(...) file.path(PATH$figures, ...)
p_mod  <- function(...) file.path(PATH$models, ...)

write_tab <- function(x, name) {
  readr::write_csv(x, p_tab(name), na = "")
  invisible(x)
}

# Normalisierung von Gemeindenamen für das Verknüpfen von Quellen ohne BFS-Nummer
norm_name <- function(x) {
  x <- gsub("\\s*\\([A-Z]{2}\\)\\s*", "", x)               # "(SG)", "(UR)" entfernen
  x <- iconv(x, from = "UTF-8", to = "ASCII//TRANSLIT")
  x <- tolower(x)
  gsub("[^a-z0-9]", "", x)
}
