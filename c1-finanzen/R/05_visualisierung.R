# ==============================================================================
# 05_visualisierung.R – Abbildungen (output/figures/*.png) und zugehörige Tabellen
# ==============================================================================
source("R/00_setup.R")
source("R/03a_modell_funktionen.R"); source("R/03b_final_effekte.R")
suppressPackageStartupMessages({library(sf); library(mgcv)})
dat <- readRDS(p_mod("analysedaten_modelle.rds")); A <- dat$A; B <- dat$B; B_s <- dat$B_s
spec_A <- dat$spec_A; spec_B <- dat$spec_B
panel <- read_csv(p_proc("panel_gemeindejahre.csv"), show_col_types = FALSE)
quer  <- read_csv(p_proc("querschnitt_bauzonen_2022.csv"), show_col_types = FALSE)
geo   <- readRDS(p_proc("gemeindegrenzen_sg_bl_ur.rds"))
fm    <- read_csv(p_tab("cv_foldergebnisse.csv"), show_col_types = FALSE)
zs    <- read_csv(p_tab("cv_zusammenfassung.csv"), show_col_types = FALSE)
oof   <- read_csv(p_mod("oof_vorhersagen.csv"), show_col_types = FALSE)

KT_COL <- c(SG = "#2A6F97", BL = "#C1666B", UR = "#4C956C")
ziel_namen <- CFG$ziel_label
th <- theme_minimal(base_size = 11) + theme(panel.grid.minor = element_blank(), legend.position = "bottom",
                                            plot.title = element_text(face = "bold"), strip.text = element_text(face = "bold"))
speichere <- function(p, name, w = 9, h = 5.5) ggsave(p_fig(name), p, width = w, height = h, dpi = 150, bg = "white")
ziel_marke <- function(d) d %>% filter(ziel)

# ---- 1) Karten der zentralen Variablen -----------------------------------------------------------------------
kt_grenze <- geo %>% left_join(distinct(panel, bfs_nr, kanton), by = "bfs_nr")
karte_daten <- geo %>%
  left_join(quer %>% select(bfs_nr, `Bauzonenbeanspruchung 2022 (m² je Einwohner)` = bauzone_m2_je_ew,
                            `SFA 2022 (%)` = sfa_2022), by = "bfs_nr") %>%
  left_join(panel %>% filter(jahr == 2025) %>% select(bfs_nr, `Bevölkerungswachstum 2020–25 (% p. a.)` = wachstum5), by = "bfs_nr")
kd_long <- karte_daten %>% pivot_longer(c(`Bevölkerungswachstum 2020–25 (% p. a.)`, `SFA 2022 (%)`, `Bauzonenbeanspruchung 2022 (m² je Einwohner)`),
                                       names_to = "variable", values_to = "wert") %>%
  mutate(variable = factor(variable, levels = c("Bevölkerungswachstum 2020–25 (% p. a.)", "SFA 2022 (%)", "Bauzonenbeanspruchung 2022 (m² je Einwohner)")))
ziel_geo <- geo %>% filter(bfs_nr %in% CFG$ziel_bfs) %>% mutate(label = unname(ziel_namen[as.character(bfs_nr)]))
zentren <- st_centroid(ziel_geo)
karten_panels <- function(v, farbe, titel) {
  d <- kd_long %>% filter(variable == v)
  lim <- quantile(d$wert, c(.02, .98), na.rm = TRUE)
  ggplot(d) + geom_sf(aes(fill = pmin(pmax(wert, lim[1]), lim[2])), colour = "white", linewidth = .08) +
    geom_sf(data = ziel_geo, fill = NA, colour = "black", linewidth = .5) +
    geom_sf_text(data = zentren, aes(label = label), size = 2.6, nudge_y = 6000, fontface = "bold") +
    scale_fill_viridis_c(option = farbe, na.value = "grey85", name = NULL, direction = -1) +
    labs(title = titel) + theme_void(base_size = 10) + theme(legend.position = "bottom", plot.title = element_text(face = "bold", size = 10),
                                                       legend.key.width = unit(1.2, "cm"))
}
for (i in 1:3) {
  v <- levels(kd_long$variable)[i]
  speichere(karten_panels(v, c("viridis", "magma", "cividis")[i], v), sprintf("karte_%d.png", i), 8, 5.5)
}
cat("Karten gespeichert\n")

# ---- 2) Deskriptive Streudiagramme --------------------------------------------------------------------------
pA <- ggplot(A, aes(wachstum5, y, colour = kanton)) + geom_point(alpha = .35, size = 1) +
  geom_smooth(aes(group = 1), method = "loess", formula = y ~ x, colour = "black", se = TRUE, linewidth = .8) +
  geom_point(data = panel %>% filter(ziel, modell_ok), aes(wachstum5, sfa), colour = "black", shape = 21, fill = "gold", size = 2.4, stroke = .7, inherit.aes = FALSE) +
  scale_colour_manual(values = KT_COL, name = "Kanton") + labs(title = "Untersuchung A: Bevölkerungswachstum und Selbstfinanzierungsanteil",
  subtitle = "Gemeindejahre der Vergleichsgemeinden (Punkte), LOESS-Glättung; gelb = Zielgemeinden (nicht im Modell)",
  x = "Annualisiertes Bevölkerungswachstum der letzten 5 Jahre (% p. a.)", y = "Selbstfinanzierungsanteil (%)") + th
speichere(pA, "streu_A_wachstum_sfa.png", 9, 5.5)
pB <- ggplot(B, aes(bauzone_m2_je_ew, y, colour = kanton)) + geom_point(alpha = .7, size = 1.6) +
  geom_smooth(aes(group = 1), method = "lm", formula = y ~ x, colour = "black", linewidth = .8) +
  geom_point(data = quer %>% filter(ziel), aes(bauzone_m2_je_ew, sfa_2022), colour = "black", shape = 21, fill = "gold", size = 3, stroke = .7, inherit.aes = FALSE) +
  scale_colour_manual(values = KT_COL, name = "Kanton") + labs(title = "Untersuchung B: Bauzonenbeanspruchung und Selbstfinanzierungsanteil 2022",
  subtitle = "Je Gemeinde ein Punkt; lineare Anpassung; gelb = Zielgemeinden (nicht im Modell)",
  x = "Bauzonenfläche 2022 je Einwohner (m²)", y = "Selbstfinanzierungsanteil 2022 (%)") + th
speichere(pB, "streu_B_bauzonen_sfa.png", 9, 5.5)
pB2 <- ggplot(B_s, aes(bauzone_m2_je_ew, y, colour = kanton)) + geom_point(alpha = .7, size = 1.6) +
  geom_smooth(aes(group = 1), method = "lm", formula = y ~ x, colour = "black", linewidth = .8) +
  scale_colour_manual(values = KT_COL[c("SG", "BL")], name = "Kanton") +
  labs(title = "Sekundär: Bauzonenbeanspruchung und Nettoschuld je Einwohner 2022 (nur SG, BL)",
       x = "Bauzonenfläche 2022 je Einwohner (m²)", y = "Nettoschuld I je Einwohner (CHF)") + th
speichere(pB2, "streu_B_bauzonen_nettoschuld.png", 9, 5.5)

# ---- 3) Finanzzeitreihen ----------------------------------------------------------------------------------------
ts <- panel %>% filter(modell_ok, !ziel) %>% group_by(kanton, jahr) %>%
  summarise(med = median(sfa), q25 = quantile(sfa, .25), q75 = quantile(sfa, .75), .groups = "drop")
pT <- ggplot(ts, aes(jahr)) + geom_ribbon(aes(ymin = q25, ymax = q75, fill = kanton), alpha = .2) +
  geom_line(aes(y = med, colour = kanton), linewidth = 1) +
  geom_line(data = panel %>% filter(ziel, jahr >= 2015), aes(jahr, sfa, linetype = ziel_label), colour = "black", linewidth = .8, inherit.aes = FALSE) +
  scale_colour_manual(values = KT_COL, name = "Median Vergleichsgemeinden") + scale_fill_manual(values = KT_COL, guide = "none") +
  scale_linetype_manual(values = c("solid", "dashed", "dotted"), name = "Zielgemeinden") +
  scale_x_continuous(breaks = 2015:2025) +
  labs(title = "Selbstfinanzierungsanteil im Zeitverlauf", subtitle = "Band = Interquartilsbereich der Vergleichsgemeinden je Kanton",
       x = NULL, y = "Selbstfinanzierungsanteil (%)") + th + theme(axis.text.x = element_text(angle = 45, hjust = 1))
speichere(pT, "zeitreihe_sfa.png", 9, 5.5)

# ---- 4) Modellvergleich (äussere Kreuzvalidierung) ---------------------------------------------------------------------
fmv <- fm %>% mutate(modell = factor(modell, levels = c("Nullmodell", "lm", "GAM", "Random Forest", "XGBoost")),
                     validierung = factor(validierung))
pM <- ggplot(fmv, aes(modell, rmse, colour = spezifikation)) +
  stat_summary(fun = mean, geom = "point", size = 3, position = position_dodge(.5)) +
  geom_point(alpha = .35, position = position_dodge(.5), size = 1.3) +
  facet_wrap(~ untersuchung + validierung, scales = "free_y", ncol = 2, labeller = label_wrap_gen(34)) +
  scale_colour_manual(values = c(basis = "#555555", erweitert = "#D1495B"), name = "Spezifikation") +
  labs(title = "Modellvergleich auf unabhängigen Daten (äussere Folds)", subtitle = "Gross = Mittel über Folds, klein = einzelne Folds; kleinerer RMSE ist besser",
       x = NULL, y = "RMSE (Prozentpunkte bzw. CHF)") + th + theme(axis.text.x = element_text(angle = 30, hjust = 1))
speichere(pM, "modellvergleich_rmse.png", 12, 9)
pM2 <- ggplot(fmv %>% filter(validierung == "gruppiert (Gemeinde)" | str_detect(as.character(validierung), "gruppiert")), aes(modell, r2, colour = spezifikation)) +
  stat_summary(fun = mean, geom = "point", size = 3, position = position_dodge(.5)) +
  geom_point(alpha = .35, position = position_dodge(.5), size = 1.3) + geom_hline(yintercept = 0, linetype = 2) +
  facet_wrap(~untersuchung, scales = "free_y", ncol = 2, labeller = label_wrap_gen(30)) +
  scale_colour_manual(values = c(basis = "#555555", erweitert = "#D1495B"), name = "Spezifikation") +
  labs(title = "R² auf unabhängigen Vorhersagen (1 − SSE/SST), gruppierte Kreuzvalidierung", x = NULL, y = "R² (kann negativ sein)") + th +
  theme(axis.text.x = element_text(angle = 30, hjust = 1))
speichere(pM2, "modellvergleich_r2.png", 11, 7)

# beobachtet vs. vorhergesagt (OOF) für das erweiterte lm und GAM
oof_p <- oof %>% filter(validierung == "gruppiert (Gemeinde)", spezifikation == "erweitert", modell %in% c("lm", "GAM", "Random Forest"),
                        str_detect(untersuchung, "^A|^B \\(SFA|^B: ")) %>% mutate(untersuchung = str_wrap(untersuchung, 30))
pO <- ggplot(oof_p, aes(pred, y)) + geom_point(alpha = .25, size = .9) + geom_abline(linetype = 2, colour = "red") +
  facet_grid(untersuchung ~ modell, scales = "free") + labs(title = "Out-of-Fold-Vorhersagen vs. Beobachtung (erweiterte Spezifikation)", x = "Vorhersage", y = "Beobachtet") + th
speichere(pO, "oof_beobachtet_vs_vorhergesagt.png", 11, 7)

# ---- 5) PDP und ALE (finale Anpassung auf allen Vergleichsgemeinden) ----------------------------------------------------------
modelle_effekt <- c("Random Forest", "XGBoost", "GAM")
pdpA <- map_dfr(modelle_effekt, ~ pdp_1d(A, spec_A$erweitert, .x, "wachstum5"))
aleA <- map_dfr(modelle_effekt, ~ ale_1d(A, spec_A$erweitert, .x, "wachstum5"))
pdpB <- map_dfr(modelle_effekt, ~ pdp_1d(B, spec_B$erweitert, .x, "bauzone_m2_je_ew", jahr_faktor = FALSE))
aleB <- map_dfr(modelle_effekt, ~ ale_1d(B, spec_B$erweitert, .x, "bauzone_m2_je_ew", jahr_faktor = FALSE))
write_tab(bind_rows(pdpA, pdpB) %>% rename(wert_pdp = pdp), "effekte_pdp.csv"); write_tab(bind_rows(aleA, aleB), "effekte_ale.csv")
pd_plot <- function(pdp, ale, daten, var, xlab, titel) {
  a <- pdp %>% transmute(modell, x, effekt = pdp - mean(pdp), art = "Partial Dependence (zentriert)")
  a <- pdp %>% group_by(modell) %>% mutate(effekt = pdp - mean(pdp), art = "Partial Dependence (zentriert)") %>% ungroup() %>% select(modell, x, effekt, art)
  b <- ale %>% transmute(modell, x, effekt = ale, art = "ALE (zentriert)")
  ggplot(bind_rows(a, b), aes(x, effekt, colour = modell)) + geom_line(linewidth = .9) + geom_hline(yintercept = 0, linetype = 3) +
    geom_rug(data = tibble(x = daten[[var]], effekt = NA_real_, modell = NA_character_), aes(x = x), inherit.aes = FALSE, sides = "b", alpha = .25) +
    facet_wrap(~art) + labs(title = titel, x = xlab, y = "Effekt auf den Selbstfinanzierungsanteil (Prozentpunkte)", colour = "Modell") + th
}
speichere(pd_plot(pdpA, aleA, A, "wachstum5", "Bevölkerungswachstum 5 Jahre (% p. a.)", "Untersuchung A: Effekt des Bevölkerungswachstums (PDP und ALE)"), "pdp_ale_A_wachstum.png", 10, 5)
speichere(pd_plot(pdpB, aleB, B, "bauzone_m2_je_ew", "Bauzonenfläche je Einwohner (m²)", "Untersuchung B: Effekt der Bauzonenbeanspruchung (PDP und ALE)"), "pdp_ale_B_bauzonen.png", 10, 5)
cat("PDP/ALE gespeichert\n")

# ---- 6) GAM-Effektplots mit Unsicherheitsband (±1.96 SE, Partialeffekte) ---------------------------------------------------------------
gam_effekte <- function(g, daten, vars_s, ref_kanton, ref_jahr = NULL) {
  map_dfr(vars_s, function(v) {
    gx <- seq(min(daten[[v]]), max(daten[[v]]), length.out = 100)
    nd <- daten[rep(1, 100), , drop = FALSE]
    for (w in vars_s) nd[[w]] <- median(daten[[w]]); nd[[v]] <- gx
    nd$kanton <- ref_kanton; if (!is.null(ref_jahr)) nd$jahr <- ref_jahr
    pr <- predict(g, newdata = nd, type = "terms", se.fit = TRUE)
    col <- paste0("s(", v, ")")
    tibble(variable = v, x = gx, effekt = pr$fit[, col], se = pr$se.fit[, col])
  })
}
gA <- readRDS(p_mod("gam_A.rds")); gB <- readRDS(p_mod("gam_B.rds"))
geA <- gam_effekte(gA, A, c("wachstum5", "log_pop", "anteil_u20", "anteil_65p"), "SG", max(A$jahr))
geB <- gam_effekte(gB, B, c("bauzone_m2_je_ew", "log_pop", "anteil_u20", "anteil_65p", "wachstum5"), "SG")
write_tab(bind_rows(geA %>% mutate(untersuchung = "A"), geB %>% mutate(untersuchung = "B")), "effekte_gam_partial.csv")
gp <- function(ge, titel) ggplot(ge, aes(x, effekt)) + geom_ribbon(aes(ymin = effekt - 1.96 * se, ymax = effekt + 1.96 * se), alpha = .25, fill = "#2A6F97") +
  geom_line(colour = "#2A6F97", linewidth = 1) + geom_hline(yintercept = 0, linetype = 3) + facet_wrap(~variable, scales = "free_x") +
  labs(title = titel, subtitle = "Partialeffekte der Smooth-Terme mit approximativem 95%-Band (REML, Doppelstrafe)", x = NULL, y = "Partialeffekt (Prozentpunkte)") + th
speichere(gp(geA, "GAM Untersuchung A: Effektplots"), "gam_effekte_A.png", 10, 6.5)
speichere(gp(geB, "GAM Untersuchung B: Effektplots"), "gam_effekte_B.png", 10, 6.5)

# ---- 7) Residualdiagnostik ---------------------------------------------------------------------------------------------------------------------------
rA <- read_csv(p_mod("residuen_A_lm.csv"), show_col_types = FALSE) %>% mutate(untersuchung = "A: lm Basis + Wachstum")
rB <- read_csv(p_mod("residuen_B_lm.csv"), show_col_types = FALSE) %>% mutate(untersuchung = "B: lm Basis + Bauzonen", jahr = 2022L)
rr <- bind_rows(rA, rB)
p1 <- ggplot(rr, aes(fitted, resid, colour = kanton)) + geom_point(alpha = .3, size = .8) + geom_hline(yintercept = 0) +
  geom_smooth(aes(group = 1), method = "loess", formula = y ~ x, colour = "black", se = FALSE, linewidth = .6) +
  facet_wrap(~untersuchung, scales = "free") + scale_colour_manual(values = KT_COL) + labs(title = "Residuen gegen angepasste Werte", x = "Angepasst", y = "Residuum") + th
p2 <- ggplot(rr, aes(sample = resid)) + stat_qq(alpha = .4, size = .8) + stat_qq_line(colour = "red") + facet_wrap(~untersuchung, scales = "free") +
  labs(title = "Normalitätsplot der Residuen", x = "Theoretische Quantile", y = "Stichprobenquantile") + th
speichere(p1, "residuen_fitted.png", 10, 4.8); speichere(p2, "residuen_qq.png", 10, 4.8)
cat("Abbildungen vollständig in", PATH$figures, "\n")
