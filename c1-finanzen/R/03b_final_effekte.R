# ==============================================================================
# 03b_final_effekte.R – Funktionen für finale Anpassungen auf allen Vergleichsgemeinden:
#   Partial Dependence (PDP), Accumulated Local Effects (ALE) und Prognosen für Zielgemeinden.
# Alle Modelle werden über dieselben fit_*-Funktionen angepasst (inkl. innerem Tuning);
# Vorhersagen für veränderte Datensätze entstehen durch EINEN Fit auf gestapelten Testdaten.
# ==============================================================================
pdp_1d <- function(train, vars, modell, var, n_grid = 30, jahr_faktor = TRUE, seed = CFG$seed) {
  gitter <- unique(as.numeric(quantile(train[[var]], probs = seq(0.02, 0.98, length.out = n_grid), na.rm = TRUE)))
  big <- map_dfr(seq_along(gitter), function(i) { d <- train; d[[var]] <- gitter[i]; d$.g <- i; d })
  pr <- MODELLE[[modell]](train, big, vars, jahr_faktor = jahr_faktor, seed = seed)$pred
  tibble(modell = modell, variable = var, x = gitter[big$.g], pred = pr) %>%
    group_by(modell, variable, x) %>% summarise(pdp = mean(pred), .groups = "drop")
}
ale_1d <- function(train, vars, modell, var, K = 15, jahr_faktor = TRUE, seed = CFG$seed) {
  z <- unique(as.numeric(quantile(train[[var]], probs = seq(0, 1, length.out = K + 1), na.rm = TRUE)))
  if (length(z) < 4) return(NULL)
  bin <- cut(train[[var]], breaks = z, include.lowest = TRUE, labels = FALSE)
  lo <- train; hi <- train
  lo[[var]] <- z[bin]; hi[[var]] <- z[bin + 1]
  big <- bind_rows(lo, hi)
  pr <- MODELLE[[modell]](train, big, vars, jahr_faktor = jahr_faktor, seed = seed)$pred
  n <- nrow(train); d <- pr[(n + 1):(2 * n)] - pr[1:n]
  lokal <- tapply(d, factor(bin, levels = seq_len(length(z) - 1)), mean)
  lokal[is.na(lokal)] <- 0
  ale <- cumsum(lokal); nk <- as.numeric(table(factor(bin, levels = seq_len(length(z) - 1))))
  mitte <- (z[-1] + z[-length(z)]) / 2
  ale_c <- ale - sum(ale * nk) / sum(nk)
  tibble(modell = modell, variable = var, x = mitte, ale = as.numeric(ale_c))
}
