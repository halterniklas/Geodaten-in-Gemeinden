# ==============================================================================
# 03_modelle.R – Modellvergleich mit verschachtelter Kreuzvalidierung
#   Untersuchung A: Bevölkerungswachstum -> Selbstfinanzierungsanteil (Panel)
#   Untersuchung B: Bauzonenbeanspruchung -> Selbstfinanzierungsanteil / Nettoschuld (Querschnitt)
# Wil, Münchenstein und Seelisberg sind vollständig aus Training, Tuning und Validierung ausgeschlossen.
# Alle Modelle und beide Spezifikationen nutzen identische äussere Folds.
# ==============================================================================
source("R/00_setup.R")
source("R/03a_modell_funktionen.R")
t0 <- Sys.time()

panel <- read_csv(p_proc("panel_gemeindejahre.csv"), show_col_types = FALSE)
quer  <- read_csv(p_proc("querschnitt_bauzonen_2022.csv"), show_col_types = FALSE)

# ------------------------------- Untersuchung A -------------------------------
A <- panel %>% filter(modell_ok, !ziel) %>%
  transmute(y = sfa, bfs_nr, kanton, jahr, log_pop, anteil_u20, anteil_65p, wachstum5, x_lv95, y_lv95)
spec_A <- list(basis = c("log_pop", "anteil_u20", "anteil_65p", "kanton", "jahr"),
               erweitert = c("log_pop", "anteil_u20", "anteil_65p", "kanton", "jahr", "wachstum5"))
cat(sprintf("A: %d Gemeindejahre, %d Gemeinden (ohne Zielgemeinden)\n", nrow(A), n_distinct(A$bfs_nr)))

fA <- folds_gruppiert(A, CFG$k_outer, CFG$seed)
fA_sp <- folds_raeumlich(A, CFG$k_outer, CFG$seed)
foldvec_A  <- A %>% left_join(select(fA, bfs_nr, fold), by = "bfs_nr") %>% pull(fold)
foldvec_As <- A %>% left_join(select(fA_sp, bfs_nr, fold), by = "bfs_nr") %>% pull(fold)

cat("A – gruppierte Kreuzvalidierung\n")
cvA  <- cv_aussen(A, foldvec_A,  spec_A, label = "gruppiert (Gemeinde)")
cat("A – räumlich geblockte Kreuzvalidierung\n")
cvAs <- cv_aussen(A, foldvec_As, spec_A, label = "räumlich geblockt")
cat("A – vorwärtsgerichtete zeitliche Splits (Test 2023, 2024, 2025)\n")
foldvec_At <- ifelse(A$jahr >= 2023, A$jahr, NA_integer_)
cvAt <- cv_aussen(A, foldvec_At, spec_A, jahr_faktor = FALSE, label = "zeitlich vorwärts",
                  train_fn = function(d, f) d$jahr < f)

# ------------------------------- Untersuchung B -------------------------------
B <- quer %>% filter(!ziel) %>%
  transmute(y = sfa_2022, y_robust = sfa_mittel_2021_23, y_schuld = nettoschuld_2022, bfs_nr, kanton, jahr = 2022L,
            log_pop, anteil_u20 = anteil_u20_2021, anteil_65p = anteil_65p_2021, wachstum5 = wachstum5_2021,
            bauzone_m2_je_ew, x_lv95, y_lv95) %>%
  filter(!is.na(y), !is.na(bauzone_m2_je_ew), !is.na(wachstum5))
spec_B <- list(basis = c("log_pop", "anteil_u20", "anteil_65p", "wachstum5", "kanton"),
               erweitert = c("log_pop", "anteil_u20", "anteil_65p", "wachstum5", "kanton", "bauzone_m2_je_ew"))
cat(sprintf("B: %d Gemeinden (ohne Zielgemeinden)\n", nrow(B)))
fB <- folds_gruppiert(B, CFG$k_outer, CFG$seed + 1)
fB_sp <- folds_raeumlich(B, CFG$k_outer, CFG$seed + 1)
foldvec_B  <- B %>% left_join(select(fB, bfs_nr, fold), by = "bfs_nr") %>% pull(fold)
foldvec_Bs <- B %>% left_join(select(fB_sp, bfs_nr, fold), by = "bfs_nr") %>% pull(fold)
cat("B – SFA 2022, gruppierte Kreuzvalidierung\n")
cvB  <- cv_aussen(B, foldvec_B,  spec_B, label = "gruppiert (Gemeinde)")
cat("B – SFA 2022, räumlich geblockte Kreuzvalidierung\n")
cvBs <- cv_aussen(B, foldvec_Bs, spec_B, label = "räumlich geblockt")

# Robustheit: SFA als 3-Jahres-Mittel 2021-2023
B_r <- B %>% filter(!is.na(y_robust)) %>% mutate(y = y_robust)
foldvec_Br <- B_r %>% left_join(select(fB, bfs_nr, fold), by = "bfs_nr") %>% pull(fold)
cat("B – Robustheit: SFA-Mittel 2021–2023\n")
cvBr <- cv_aussen(B_r, foldvec_Br, spec_B, label = "gruppiert (Gemeinde), SFA-Mittel 2021-23")

# Sekundär: Nettoschuld je Einwohner (nur SG und BL; UR nur Nettoschuld II -> nicht vergleichbar)
B_s <- B %>% filter(kanton %in% c("SG", "BL"), !is.na(y_schuld)) %>% mutate(y = y_schuld)
fB_s <- folds_gruppiert(B_s, CFG$k_outer, CFG$seed + 2)
foldvec_Bsch <- B_s %>% left_join(select(fB_s, bfs_nr, fold), by = "bfs_nr") %>% pull(fold)
cat(sprintf("B sekundär – Nettoschuld je Einwohner: %d Gemeinden (SG, BL)\n", nrow(B_s)))
cvBsch <- cv_aussen(B_s, foldvec_Bsch, spec_B, label = "gruppiert (Gemeinde), Nettoschuld je EW")

# ------------------------------- Ergebnisse sichern ------------------------------
sammle <- function(un, ...) {
  l <- list(...)
  list(pred = bind_rows(map(l, "pred")) %>% mutate(untersuchung = un, .before = 1),
       par  = bind_rows(map(l, "par"))  %>% mutate(untersuchung = un, .before = 1))
}
resA <- sammle("A: Bevölkerungswachstum", cvA, cvAs, cvAt)
resB <- sammle("B: Bauzonenbeanspruchung (SFA 2022)", cvB, cvBs, cvBr)
resS <- sammle("B sekundär: Nettoschuld je EW", cvBsch)
oof <- bind_rows(resA$pred, resB$pred, resS$pred)
par <- bind_rows(resA$par, resB$par, resS$par)
write_csv(oof, p_mod("oof_vorhersagen.csv"))
write_tab(par, "cv_hyperparameter.csv")

fm  <- oof %>% group_by(untersuchung) %>% group_modify(~ fold_metriken(.x)) %>% ungroup()
zs  <- oof %>% group_by(untersuchung) %>% group_modify(~ zusammenfassung(fold_metriken(.x), .x)) %>% ungroup()
inc <- oof %>% group_by(untersuchung) %>% group_modify(~ inkrement_bootstrap(.x)) %>% ungroup()
write_tab(fm,  "cv_foldergebnisse.csv")
write_tab(zs,  "cv_zusammenfassung.csv")
write_tab(inc, "cv_inkrement_bootstrap.csv")

folds_all <- bind_rows(
  fA    %>% mutate(untersuchung = "A", validierung = "gruppiert (Gemeinde)"),
  fA_sp %>% mutate(untersuchung = "A", validierung = "räumlich geblockt"),
  fB    %>% mutate(untersuchung = "B (SFA 2022)", validierung = "gruppiert (Gemeinde)"),
  fB_sp %>% mutate(untersuchung = "B (SFA 2022)", validierung = "räumlich geblockt"),
  fB_s  %>% mutate(untersuchung = "B sekundär (Nettoschuld)", validierung = "gruppiert (Gemeinde)")) %>%
  select(untersuchung, validierung, bfs_nr, kanton, fold)
write_csv(folds_all, p_mod("fold_zuordnung.csv"))
write_csv(tibble(untersuchung = "A", validierung = "zeitlich vorwärts", test_jahr = 2023:2025,
                 trainingsjahre = paste0("alle Jahre < ", 2023:2025)), p_mod("fold_zuordnung_zeitlich.csv"))

saveRDS(list(A = A, B = B, B_s = B_s, spec_A = spec_A, spec_B = spec_B), p_mod("analysedaten_modelle.rds"))
cat("\n== Modellvergleich abgeschlossen in", round(difftime(Sys.time(), t0, units = "mins"), 1), "min ==\n")
print(zs %>% filter(validierung == "gruppiert (Gemeinde)") %>%
        select(untersuchung, spezifikation, modell, rmse_mittel, r2_mittel, r2_oof_gesamt, skill_vs_null) %>% as.data.frame(), digits = 3)
