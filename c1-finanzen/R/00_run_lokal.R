# ==============================================================================
# 00_run_lokal.R – Einstiegspunkt für die lokale Ausführung in RStudio
#   1. Projekt c1-finanzen.Rproj öffnen
#   2. Diese Datei öffnen und "Source" klicken (oder source("R/00_run_lokal.R"))
# Installiert fehlende Pakete (CRAN), lädt bei fehlenden Rohdaten die Quellen herunter,
# führt die gesamte Pipeline aus und rendert den Bericht (report/bericht.html).
# Voraussetzungen: R >= 4.3, Internet, für den Bericht Quarto (https://quarto.org).
# ==============================================================================
stopifnot("Bitte das RStudio-Projekt c1-finanzen.Rproj öffnen (Arbeitsverzeichnis = Projektordner)" =
            file.exists("c1-finanzen.Rproj"))

pakete <- c("dplyr", "tidyr", "readr", "readxl", "stringr", "purrr", "tibble", "ggplot2", "scales",
            "sf", "pdftools", "jsonlite", "httr", "ranger", "mgcv", "xgboost", "sandwich", "lmtest",
            "spdep", "knitr", "rmarkdown")
fehlend <- setdiff(pakete, rownames(installed.packages()))
if (length(fehlend)) install.packages(fehlend, repos = "https://cloud.r-project.org")

# Optional, für exakt dieselben Paketversionen:  renv::restore()   (falls renv.lock vorhanden)
source("R/run_all.R", encoding = "UTF-8")
