# ==============================================================================
# run_all.R – komplette Pipeline in der richtigen Reihenfolge (Projekt in RStudio öffnen,
# dann source("R/run_all.R")). Laufzeit ca. 10–15 Minuten.
# ==============================================================================
stopifnot(file.exists("c1-finanzen.Rproj"))
schritte <- c("R/01_download.R", "R/01b_dateninventur_quellen.R", "R/02_aufbereitung.R", "R/03_modelle.R",
              "R/04_inferenz_diagnostik.R", "R/05_visualisierung.R", "R/06_zielgemeinden.R")
for (s in schritte) {
  cat("\n################ ", s, " ################\n")
  t0 <- Sys.time()
  # jeder Schritt in eigener Umgebung; Fehler stoppen die Pipeline
  source(s, local = new.env(parent = globalenv()), encoding = "UTF-8")
  cat(sprintf("-> %s fertig (%.1f min)\n", s, as.numeric(difftime(Sys.time(), t0, units = "mins"))))
}
# Quarto-Bericht (benötigt Quarto >= 1.4: https://quarto.org)
if (nzchar(Sys.which("quarto"))) {
  system2("quarto", c("render", "report/bericht.qmd"))
} else message("Quarto nicht gefunden – Bericht nicht gerendert (siehe README).")
