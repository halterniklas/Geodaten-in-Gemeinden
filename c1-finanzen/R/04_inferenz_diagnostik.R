# ==============================================================================
# 04_inferenz_diagnostik.R – Inferenzstatistik und Modelldiagnostik
#   (getrennt von der Vorhersageevaluation in 03_modelle.R)
#   - lm: Koeffizienten, 95%-KI, p-Werte (gemeindegeclusterte SE bei Panel, HC3 im Querschnitt)
#   - Panel mit Gemeinde- und Jahreseffekten
#   - GAM: parametrische und approximative Smooth-p-Werte
#   - Residuen, Heteroskedastizität (Breusch-Pagan), Kollinearität (VIF), räumliche Autokorrelation (Moran's I)
# Random Forest und XGBoost liefern bewusst keine Koeffizienten-p-Werte.
# ==============================================================================
source("R/00_setup.R")
suppressPackageStartupMessages({library(sandwich); library(lmtest); library(mgcv); library(spdep)})
dat <- readRDS(p_mod("analysedaten_modelle.rds"))
A <- dat$A; B <- dat$B; B_s <- dat$B_s

# ---- Hilfsfunktionen ------------------------------------------------------------------
koef_tabelle <- function(m, cluster = NULL, label = "") {
  if (!is.null(cluster)) {
    V <- sandwich::vcovCL(m, cluster = cluster, type = "HC1"); df <- length(unique(cluster)) - 1; vt <- "Cluster (Gemeinde), HC1"
  } else { V <- sandwich::vcovHC(m, type = "HC3"); df <- m$df.residual; vt <- "HC3" }
  est <- coef(m); se <- sqrt(diag(V)); tt <- est / se
  tibble(modell = label, term = names(est), schaetzer = est, std_fehler = se, t = tt,
         ci_lo = est - qt(.975, df) * se, ci_hi = est + qt(.975, df) * se,
         p_wert = 2 * pt(abs(tt), df, lower.tail = FALSE), vcov_typ = vt, df = df)
}
gueteinsample <- function(m, label, n_cl = NA) {
  s <- summary(m)
  tibble(modell = label, n = nobs(m), n_gemeinden = n_cl, r2_insample = s$r.squared, r2_adj_insample = s$adj.r.squared,
         sigma = s$sigma)
}
vif_tab <- function(m, label) {
  X <- model.matrix(m)[, -1, drop = FALSE]
  X <- X[, apply(X, 2, sd) > 0, drop = FALSE]
  R <- cor(X); v <- diag(solve(R))
  tibble(modell = label, term = colnames(X), vif = v)
}
moran_tab <- function(d, res, label, k = 5) {
  g <- tibble(bfs_nr = d$bfs_nr, x = d$x_lv95, y = d$y_lv95, e = res) %>% group_by(bfs_nr) %>%
    summarise(x = first(x), y = first(y), e = mean(e), .groups = "drop")
  nb <- spdep::knn2nb(spdep::knearneigh(as.matrix(g[, c("x", "y")]), k = k))
  lw <- spdep::nb2listw(nb, style = "W")
  set.seed(CFG$seed)
  mt <- spdep::moran.mc(g$e, lw, nsim = 999)
  tibble(modell = label, n_gemeinden = nrow(g), k_nachbarn = k, morans_i = unname(mt$statistic), p_permutation = mt$p.value)
}
bp_tab <- function(m, label) { b <- lmtest::bptest(m); tibble(modell = label, bp_statistik = unname(b$statistic), bp_df = unname(b$parameter), p_wert = b$p.value) }

# =============================== Untersuchung A =====================================================
fA_b <- lm(y ~ log_pop + anteil_u20 + anteil_65p + factor(kanton) + factor(jahr), data = A)
fA_e <- lm(y ~ wachstum5 + log_pop + anteil_u20 + anteil_65p + factor(kanton) + factor(jahr), data = A)
cl <- A$bfs_nr
tA <- bind_rows(koef_tabelle(fA_b, cl, "A Basis (gepoolt)"), koef_tabelle(fA_e, cl, "A Basis + Wachstum (gepoolt)"))
write_tab(tA, "inferenz_A_lm_gepoolt.csv")
wA <- lmtest::waldtest(fA_b, fA_e, vcov = function(x) sandwich::vcovCL(x, cluster = cl, type = "HC1"), test = "F")
guete_A <- bind_rows(gueteinsample(fA_b, "A Basis (gepoolt)", n_distinct(A$bfs_nr)), gueteinsample(fA_e, "A Basis + Wachstum (gepoolt)", n_distinct(A$bfs_nr))) %>%
  mutate(wald_F_wachstum = c(NA, wA$F[2]), wald_p_wachstum = c(NA, wA$`Pr(>F)`[2]))
write_tab(guete_A, "inferenz_A_lm_guete_insample.csv")

# kantonale Modelle (Heterogenität; UR nur indikativ)
tA_kt <- map_dfr(CFG$kantone, function(k) {
  d <- A %>% filter(kanton == k); ng <- n_distinct(d$bfs_nr)
  m <- lm(y ~ wachstum5 + log_pop + anteil_u20 + anteil_65p + factor(jahr), data = d)
  koef_tabelle(m, d$bfs_nr, paste0("A erweitert, nur ", k)) %>% mutate(n_gemeinden = ng, n_beob = nrow(d),
    belastbar = ng >= CFG$min_gemeinden_kanton_modell)
}) %>% filter(term %in% c("wachstum5", "log_pop", "anteil_u20", "anteil_65p"))
write_tab(tA_kt, "inferenz_A_lm_kantonal.csv")

# Steuerkraft-Sensitivität (nur SG/BL; kantonsspezifische, nicht vergleichbare Grössen)
panel_st <- read_csv(p_proc("panel_gemeindejahre.csv"), show_col_types = FALSE) %>% filter(modell_ok, !ziel, kanton %in% c("SG", "BL"), !is.na(steuer_je_ew))
tA_st <- map_dfr(c("SG", "BL"), function(k) {
  d <- panel_st %>% filter(kanton == k) %>% mutate(steuer_1000 = steuer_je_ew / 1000)
  m0 <- lm(sfa ~ log_pop + anteil_u20 + anteil_65p + steuer_1000 + factor(jahr), data = d)
  m1 <- lm(sfa ~ wachstum5 + log_pop + anteil_u20 + anteil_65p + steuer_1000 + factor(jahr), data = d)
  koef_tabelle(m1, d$bfs_nr, paste0("A erweitert + Steuermass, nur ", k)) %>%
    mutate(r2_insample = summary(m1)$r2, r2_basis = summary(m0)$r2) %>% filter(term %in% c("wachstum5", "steuer_1000"))
})
write_tab(tA_st, "inferenz_A_sensitivitaet_steuerkraft.csv")

# Panel mit Gemeinde- und Jahreseffekten (within-Schätzung, Cluster-SE)
fA_fe <- lm(y ~ wachstum5 + log_pop + anteil_u20 + anteil_65p + factor(bfs_nr) + factor(jahr), data = A)
tA_fe <- koef_tabelle(fA_fe, cl, "A Panel: Gemeinde- und Jahreseffekte") %>% filter(term %in% c("wachstum5", "log_pop", "anteil_u20", "anteil_65p"))
fA_fe0 <- lm(y ~ log_pop + anteil_u20 + anteil_65p + factor(bfs_nr) + factor(jahr), data = A)
tA_fe <- tA_fe %>% mutate(r2_within_zuwachs_ueber_basis = summary(fA_fe)$r.squared - summary(fA_fe0)$r.squared)
write_tab(tA_fe, "inferenz_A_panel_fixed_effects.csv")

# GAM
gA <- mgcv::gam(y ~ s(wachstum5, k = 5) + s(log_pop, k = 5) + s(anteil_u20, k = 5) + s(anteil_65p, k = 5) + factor(kanton) + factor(jahr),
                data = A, method = "REML", select = TRUE)
sg <- summary(gA)
tA_gam <- bind_rows(
  as_tibble(sg$p.table, rownames = "term") %>% rename(schaetzer = Estimate, std_fehler = `Std. Error`, t = `t value`, p_wert = `Pr(>|t|)`) %>% mutate(art = "parametrisch"),
  as_tibble(sg$s.table, rownames = "term") %>% rename(edf_ = edf, ref_df = Ref.df, F = F, p_wert = `p-value`) %>% mutate(art = "Smooth (approximativ)", edf = edf_) %>% select(-edf_)) %>%
  mutate(modell = "A GAM erweitert", .before = 1)
write_tab(tA_gam, "inferenz_A_gam.csv")
write_tab(tibble(modell = "A GAM erweitert", devianz_erklaert = sg$dev.expl, r2_adj = sg$r.sq, n = sg$n, reml = as.numeric(sg$sp.criterion)), "inferenz_A_gam_guete.csv")
saveRDS(gA, p_mod("gam_A.rds"))

# Diagnostik A
diag_A <- list(
  bp = bp_tab(fA_e, "A Basis + Wachstum"),
  vif = vif_tab(fA_e, "A Basis + Wachstum"),
  moran = moran_tab(A, resid(fA_e), "A Basis + Wachstum (Gemeindemittel der Residuen)"))
write_tab(diag_A$bp, "diagnostik_A_breusch_pagan.csv"); write_tab(diag_A$vif, "diagnostik_A_vif.csv"); write_tab(diag_A$moran, "diagnostik_A_moran.csv")
write_csv(tibble(bfs_nr = A$bfs_nr, kanton = A$kanton, jahr = A$jahr, y = A$y, fitted = fitted(fA_e), resid = resid(fA_e)), p_mod("residuen_A_lm.csv"))
write_tab(tibble(prediktor = c("wachstum5", "log_pop", "anteil_u20", "anteil_65p"),
                 korr_mit_wachstum5 = c(1, cor(A[, c("log_pop", "anteil_u20", "anteil_65p")], A$wachstum5)[, 1] |> unname())) %>% mutate(.before = 1, untersuchung = "A"), "diagnostik_A_korrelation_wachstum.csv")

# =============================== Untersuchung B =====================================================
fB_b <- lm(y ~ log_pop + anteil_u20 + anteil_65p + wachstum5 + factor(kanton), data = B)
fB_e <- lm(y ~ bauzone_m2_je_ew + log_pop + anteil_u20 + anteil_65p + wachstum5 + factor(kanton), data = B)
fB_l <- lm(y ~ log(bauzone_m2_je_ew) + log_pop + anteil_u20 + anteil_65p + wachstum5 + factor(kanton), data = B)
tB <- bind_rows(koef_tabelle(fB_b, NULL, "B Basis (gepoolt)"), koef_tabelle(fB_e, NULL, "B Basis + Bauzonen m2/EW (gepoolt)"),
                koef_tabelle(fB_l, NULL, "B Basis + log(Bauzonen m2/EW) (Sensitivität)"))
write_tab(tB, "inferenz_B_lm_gepoolt.csv")
wB <- lmtest::waldtest(fB_b, fB_e, vcov = function(x) sandwich::vcovHC(x, type = "HC3"), test = "F")
guete_B <- bind_rows(gueteinsample(fB_b, "B Basis (gepoolt)"), gueteinsample(fB_e, "B Basis + Bauzonen m2/EW (gepoolt)")) %>%
  mutate(wald_F_bauzonen = c(NA, wB$F[2]), wald_p_bauzonen = c(NA, wB$`Pr(>F)`[2]))
write_tab(guete_B, "inferenz_B_lm_guete_insample.csv")

tB_kt <- map_dfr(CFG$kantone, function(k) {
  d <- B %>% filter(kanton == k)
  m <- lm(y ~ bauzone_m2_je_ew + log_pop + anteil_u20 + anteil_65p + wachstum5, data = d)
  koef_tabelle(m, NULL, paste0("B erweitert, nur ", k)) %>% mutate(n_gemeinden = nrow(d), belastbar = nrow(d) >= CFG$min_gemeinden_kanton_modell)
}) %>% filter(term %in% c("bauzone_m2_je_ew", "log_pop", "anteil_u20", "anteil_65p", "wachstum5"))
write_tab(tB_kt, "inferenz_B_lm_kantonal.csv")

# Robustheit: SFA-Mittel 2021-23
Br <- B %>% filter(!is.na(y_robust))
fBr <- lm(y_robust ~ bauzone_m2_je_ew + log_pop + anteil_u20 + anteil_65p + wachstum5 + factor(kanton), data = Br)
write_tab(koef_tabelle(fBr, NULL, "B Robustheit: SFA-Mittel 2021-23"), "inferenz_B_lm_robustheit_sfa_mittel.csv")

# Sekundär: Nettoschuld je Einwohner (SG, BL)
fS_b <- lm(y_schuld ~ log_pop + anteil_u20 + anteil_65p + wachstum5 + factor(kanton), data = B_s %>% mutate(y_schuld = y))
fS_e <- lm(y_schuld ~ bauzone_m2_je_ew + log_pop + anteil_u20 + anteil_65p + wachstum5 + factor(kanton), data = B_s %>% mutate(y_schuld = y))
write_tab(bind_rows(koef_tabelle(fS_b, NULL, "B sekundär Nettoschuld je EW: Basis (SG, BL)"), koef_tabelle(fS_e, NULL, "B sekundär Nettoschuld je EW: + Bauzonen (SG, BL)")), "inferenz_B_nettoschuld_lm.csv")

gB <- mgcv::gam(y ~ s(bauzone_m2_je_ew, k = 4) + s(log_pop, k = 4) + s(anteil_u20, k = 4) + s(anteil_65p, k = 4) + s(wachstum5, k = 4) + factor(kanton),
                data = B, method = "REML", select = TRUE)
sB <- summary(gB)
tB_gam <- bind_rows(
  as_tibble(sB$p.table, rownames = "term") %>% rename(schaetzer = Estimate, std_fehler = `Std. Error`, t = `t value`, p_wert = `Pr(>|t|)`) %>% mutate(art = "parametrisch"),
  as_tibble(sB$s.table, rownames = "term") %>% rename(ref_df = Ref.df, p_wert = `p-value`) %>% mutate(art = "Smooth (approximativ)")) %>%
  mutate(modell = "B GAM erweitert", .before = 1)
write_tab(tB_gam, "inferenz_B_gam.csv")
saveRDS(gB, p_mod("gam_B.rds"))

diag_B <- list(bp = bp_tab(fB_e, "B Basis + Bauzonen"), vif = vif_tab(fB_e, "B Basis + Bauzonen"),
               moran = moran_tab(B, resid(fB_e), "B Basis + Bauzonen"))
write_tab(diag_B$bp, "diagnostik_B_breusch_pagan.csv"); write_tab(diag_B$vif, "diagnostik_B_vif.csv"); write_tab(diag_B$moran, "diagnostik_B_moran.csv")
write_csv(tibble(bfs_nr = B$bfs_nr, kanton = B$kanton, y = B$y, fitted = fitted(fB_e), resid = resid(fB_e)), p_mod("residuen_B_lm.csv"))
write_tab(tibble(untersuchung = "B", prediktor = c("log_pop", "anteil_u20", "anteil_65p", "wachstum5"),
                 korr_mit_bauzonen = cor(B[, c("log_pop", "anteil_u20", "anteil_65p", "wachstum5")], B$bauzone_m2_je_ew)[, 1] |> unname()), "diagnostik_B_korrelation_bauzonen.csv")

cat("\n== Inferenz abgeschlossen ==\n")
print(guete_A); print(tA %>% filter(term == "wachstum5") %>% select(modell, schaetzer, ci_lo, ci_hi, p_wert))
print(guete_B); print(tB %>% filter(str_detect(term, "bauzone")) %>% select(modell, schaetzer, ci_lo, ci_hi, p_wert))
print(diag_A$moran); print(diag_B$moran)
