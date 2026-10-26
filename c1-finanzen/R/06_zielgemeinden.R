# ==============================================================================
# 06_zielgemeinden.R – Anwendung auf Wil SG, Münchenstein BL, Seelisberg UR
# Die Zielgemeinden waren weder im Training noch im Tuning noch in der Validierung.
# Die Modelle werden auf allen Vergleichsgemeinden angepasst (inkl. innerem Tuning) und
# auf die Zielgemeinden angewendet. Zusätzlich: Einordnung in die Vergleichsgruppe
# und Prüfung, ob die Merkmalskombination im Trainingsbereich liegt (Extrapolation).
# ==============================================================================
source("R/00_setup.R")
source("R/03a_modell_funktionen.R")
dat <- readRDS(p_mod("analysedaten_modelle.rds")); A <- dat$A; B <- dat$B; B_s <- dat$B_s
spec_A <- dat$spec_A; spec_B <- dat$spec_B
panel <- read_csv(p_proc("panel_gemeindejahre.csv"), show_col_types = FALSE)
quer  <- read_csv(p_proc("querschnitt_bauzonen_2022.csv"), show_col_types = FALSE)
zs    <- read_csv(p_tab("cv_zusammenfassung.csv"), show_col_types = FALSE)
lab   <- CFG$ziel_label

rmse_oof <- function(un_prefix, modell, spec = "erweitert", val = "gruppiert (Gemeinde)") {
  zs %>% filter(str_starts(untersuchung, un_prefix), modell == !!modell, spezifikation == spec, validierung == val) %>% pull(rmse_oof_gesamt) %>% first()
}
pct <- function(x, ref) mean(ref <= x, na.rm = TRUE) * 100          # Perzentilrang (Anteil Vergleichswerte <= x)

# ---- Trainingsbereich ---------------------------------------------------------------------------------------------
bereich_pruefung <- function(train, ziel, vars_stetig, id_cols) {
  X <- as.matrix(train[, vars_stetig]); mu <- colMeans(X); S <- cov(X)
  d2_train <- mahalanobis(X, mu, S); schwelle <- quantile(d2_train, 0.975)
  out <- ziel[, id_cols, drop = FALSE]
  Z <- as.matrix(ziel[, vars_stetig])
  out$mahalanobis_d2 <- mahalanobis(Z, mu, S); out$mahalanobis_schwelle_97_5 <- unname(schwelle)
  for (v in vars_stetig) {
    out[[paste0("in_min_max_", v)]] <- ziel[[v]] >= min(train[[v]]) & ziel[[v]] <= max(train[[v]])
    q <- quantile(train[[v]], c(.05, .95)); out[[paste0("in_5_95_", v)]] <- ziel[[v]] >= q[1] & ziel[[v]] <= q[2]
  }
  out$alle_in_min_max <- rowSums(!as.matrix(out[paste0("in_min_max_", vars_stetig)])) == 0
  out$bewertung <- case_when(!out$alle_in_min_max ~ "ausserhalb des Trainingsbereichs (Extrapolation)",
                             out$mahalanobis_d2 > out$mahalanobis_schwelle_97_5 ~ "ungewöhnliche Merkmalskombination (Mahalanobis > 97.5 %)",
                             rowSums(!as.matrix(out[paste0("in_5_95_", vars_stetig)])) > 0 ~ "im Trainingsbereich, aber am Rand (ausserhalb 5–95 %)",
                             TRUE ~ "im Trainingsbereich")
  out
}

# ================================ Untersuchung A =======================================================================
ZA <- panel %>% filter(ziel, modell_ok) %>%
  transmute(y = sfa, bfs_nr, kanton, jahr, log_pop, anteil_u20, anteil_65p, wachstum5, ziel_label)
modelle_apply <- c("lm", "GAM", "Random Forest", "XGBoost")
predA <- map_dfr(c("basis", "erweitert"), function(sp) {
  map_dfr(modelle_apply, function(mn) {
    pr <- MODELLE[[mn]](A, ZA, spec_A[[sp]], jahr_faktor = TRUE, seed = CFG$seed)$pred
    tibble(ZA[, c("ziel_label", "bfs_nr", "kanton", "jahr", "y")], spezifikation = sp, modell = mn, vorhersage = pr)
  })
}) %>% mutate(residuum = y - vorhersage)
# kantonsinternes lm (nur Vergleichsgemeinden des eigenen Kantons) als Gegenprobe zur gepoolten Schätzung
predA_kt <- map_dfr(unique(ZA$kanton), function(k) {
  tr <- A %>% filter(kanton == k); te <- ZA %>% filter(kanton == k)
  v <- setdiff(spec_A$erweitert, "kanton")
  pr <- MODELLE$lm(tr, te, v, jahr_faktor = TRUE)$pred
  tibble(te[, c("ziel_label", "bfs_nr", "kanton", "jahr", "y")], spezifikation = "erweitert", modell = "lm (nur eigener Kanton)",
         vorhersage = pr, residuum = te$y - pr, n_vergleichsgemeinden = n_distinct(tr$bfs_nr))
})
# lm-Prognoseintervall (95 %, klassisch)
pi_A <- map_dfr(unique(ZA$kanton), function(k) NULL)
lmA <- lm(y ~ ., data = A %>% mutate(jahr = factor(jahr)) %>% select(y, all_of(spec_A$erweitert)))
piA <- predict(lmA, newdata = ZA %>% mutate(jahr = factor(jahr, levels = levels(factor(A$jahr)))), interval = "prediction")
predA <- predA %>% left_join(tibble(ZA[, c("bfs_nr", "jahr")], pi_lo = piA[, "lwr"], pi_hi = piA[, "upr"]) %>% mutate(modell = "lm", spezifikation = "erweitert"),
                             by = c("bfs_nr", "jahr", "modell", "spezifikation"))
einordA <- ZA %>% rowwise() %>% mutate(
  perz_sfa_kanton = pct(y, A$y[A$kanton == kanton & A$jahr == jahr]),
  perz_sfa_alle   = pct(y, A$y[A$jahr == jahr]),
  perz_wachstum_kanton = pct(wachstum5, A$wachstum5[A$kanton == kanton & A$jahr == jahr]),
  perz_wachstum_alle   = pct(wachstum5, A$wachstum5[A$jahr == jahr]),
  n_vergleich_kanton_jahr = sum(A$kanton == kanton & A$jahr == jahr)) %>% ungroup() %>%
  select(ziel_label, bfs_nr, jahr, starts_with("perz_"), n_vergleich_kanton_jahr)
rangeA <- bereich_pruefung(A, ZA, c("wachstum5", "log_pop", "anteil_u20", "anteil_65p"), c("ziel_label", "bfs_nr", "jahr"))
write_tab(bind_rows(predA, predA_kt), "zielgemeinden_A_vorhersagen.csv")
write_tab(einordA, "zielgemeinden_A_einordnung.csv"); write_tab(rangeA, "zielgemeinden_A_trainingsbereich.csv")

# ================================ Untersuchung B =======================================================================
ZB <- quer %>% filter(ziel) %>%
  transmute(y = sfa_2022, y_schuld = nettoschuld_2022, bfs_nr, kanton, jahr = 2022L, ziel_label, log_pop,
            anteil_u20 = anteil_u20_2021, anteil_65p = anteil_65p_2021, wachstum5 = wachstum5_2021, bauzone_m2_je_ew)
predB <- map_dfr(c("basis", "erweitert"), function(sp) {
  map_dfr(modelle_apply, function(mn) {
    pr <- MODELLE[[mn]](B, ZB, spec_B[[sp]], jahr_faktor = FALSE, seed = CFG$seed)$pred
    tibble(ZB[, c("ziel_label", "bfs_nr", "kanton", "y")], zielgroesse = "SFA 2022 (%)", spezifikation = sp, modell = mn, vorhersage = pr)
  })
}) %>% mutate(residuum = y - vorhersage)
ZBs <- ZB %>% filter(kanton %in% c("SG", "BL"))
predBs <- map_dfr(c("basis", "erweitert"), function(sp) {
  map_dfr(modelle_apply, function(mn) {
    pr <- MODELLE[[mn]](B_s, ZBs, spec_B[[sp]], jahr_faktor = FALSE, seed = CFG$seed)$pred
    tibble(ZBs[, c("ziel_label", "bfs_nr", "kanton")], y = ZBs$y_schuld, zielgroesse = "Nettoschuld I je Einwohner 2022 (CHF)", spezifikation = sp, modell = mn, vorhersage = pr)
  })
}) %>% mutate(residuum = y - vorhersage)
lmB <- lm(y ~ ., data = B %>% select(y, all_of(spec_B$erweitert)))
piB <- predict(lmB, newdata = ZB, interval = "prediction")
predB <- predB %>% left_join(tibble(bfs_nr = ZB$bfs_nr, pi_lo = piB[, "lwr"], pi_hi = piB[, "upr"], modell = "lm", spezifikation = "erweitert"), by = c("bfs_nr", "modell", "spezifikation"))
einordB <- ZB %>% rowwise() %>% mutate(
  perz_bauzonen_kanton = pct(bauzone_m2_je_ew, B$bauzone_m2_je_ew[B$kanton == kanton]),
  perz_bauzonen_alle = pct(bauzone_m2_je_ew, B$bauzone_m2_je_ew),
  perz_sfa_kanton = pct(y, B$y[B$kanton == kanton]), perz_sfa_alle = pct(y, B$y),
  perz_nettoschuld_kanton = if (kanton %in% c("SG", "BL")) pct(y_schuld, B_s$y[B_s$kanton == kanton]) else NA_real_,
  n_vergleich_kanton = sum(B$kanton == kanton)) %>% ungroup() %>%
  select(ziel_label, bfs_nr, bauzone_m2_je_ew, y, y_schuld, starts_with("perz_"), n_vergleich_kanton) %>% rename(sfa_2022 = y, nettoschuld_2022 = y_schuld)
rangeB <- bereich_pruefung(B, ZB, c("bauzone_m2_je_ew", "log_pop", "anteil_u20", "anteil_65p", "wachstum5"), c("ziel_label", "bfs_nr"))
write_tab(bind_rows(predB, predBs), "zielgemeinden_B_vorhersagen.csv")
write_tab(einordB, "zielgemeinden_B_einordnung.csv"); write_tab(rangeB, "zielgemeinden_B_trainingsbereich.csv")

# ---- Kurzübersicht für den Bericht ----------------------------------------------------------------------------------------------------
jahr_max <- max(ZA$jahr)
uebersicht <- bind_rows(
  predA %>% filter(spezifikation == "erweitert", jahr == jahr_max) %>% mutate(untersuchung = paste0("A: SFA ", jahr_max), zielgroesse = "SFA (%)"),
  predB %>% filter(spezifikation == "erweitert") %>% mutate(untersuchung = "B: SFA 2022"),
  predBs %>% filter(spezifikation == "erweitert") %>% mutate(untersuchung = "B sekundär: Nettoschuld 2022")) %>%
  select(untersuchung, ziel_label, modell, beobachtet = y, vorhersage, residuum, any_of(c("pi_lo", "pi_hi")))
write_tab(uebersicht, "zielgemeinden_uebersicht.csv")
cat("\n== Zielgemeinden abgeschlossen ==\n")
print(uebersicht %>% mutate(across(where(is.numeric), ~ round(.x, 1))) %>% as.data.frame())
print(rangeA %>% filter(jahr == jahr_max) %>% select(ziel_label, bewertung, mahalanobis_d2, mahalanobis_schwelle_97_5) %>% as.data.frame())
print(rangeB %>% select(ziel_label, bewertung, mahalanobis_d2, mahalanobis_schwelle_97_5) %>% as.data.frame())
