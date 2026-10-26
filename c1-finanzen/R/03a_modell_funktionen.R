# ==============================================================================
# 03a_modell_funktionen.R – Modelle, Tuning, verschachtelte Kreuzvalidierung
# Modelle: Nullmodell, lm, Random Forest (ranger), GAM (mgcv), Gradient Boosting (xgboost)
# Vorverarbeitung (Faktor-Levels, Dummy-Kodierung) wird je Trainingsdatensatz festgelegt.
# Gemeinde-IDs sind NIE Prädiktoren; sie dienen nur der gruppierten Fold-Bildung.
# MaxEnt: bewusst nicht implementiert (siehe Bericht, Abschnitt Methodik).
# ==============================================================================

# ---- Kennzahlen --------------------------------------------------------------
metriken <- function(y, pred) {
  sse <- sum((y - pred)^2); sst <- sum((y - mean(y))^2)
  tibble(n = length(y), r2 = 1 - sse / sst, rmse = sqrt(mean((y - pred)^2)),
         mae = mean(abs(y - pred)), mse = mean((y - pred)^2))
}

# ---- Fold-Bildung ------------------------------------------------------------
# Gruppierte, nach Kanton geschichtete Folds: alle Jahre einer Gemeinde im selben Fold.
folds_gruppiert <- function(gem, k, seed) {
  set.seed(seed)
  g <- gem %>% distinct(bfs_nr, kanton) %>% group_by(kanton) %>%
    mutate(fold = sample(rep_len(seq_len(k), n()))) %>% ungroup()
  g
}
# Räumlich geblockt: je Kanton k-means (LV95-Zentren) in k Blöcke; Block j jedes Kantons -> Fold j.
folds_raeumlich <- function(gem, k, seed) {
  set.seed(seed)
  gem %>% distinct(bfs_nr, kanton, x_lv95, y_lv95) %>% group_by(kanton) %>%
    group_modify(function(d, key) {
      km <- stats::kmeans(scale(d[, c("x_lv95", "y_lv95")]), centers = min(k, nrow(d)), nstart = 25)
      # Blöcke nach Ost-West-Lage ordnen, damit die Zuordnung zu Fold-Nummern reproduzierbar ist
      ord <- order(tapply(d$x_lv95, km$cluster, mean))
      d$fold <- match(km$cluster, ord)
      d[, c("bfs_nr", "fold")]
    }) %>% ungroup()
}
inner_folds <- function(train, k, seed) {
  g <- folds_gruppiert(train, k, seed)
  train %>% left_join(select(g, bfs_nr, ifold = fold), by = "bfs_nr") %>% pull(ifold)
}

# ---- Designmatrizen -----------------------------------------------------------
bereite_vor <- function(train, test, vars, jahr_faktor) {
  tr <- train[, vars, drop = FALSE]; te <- test[, vars, drop = FALSE]
  if ("kanton" %in% vars) {
    lev <- sort(unique(as.character(train$kanton)))
    tr$kanton <- factor(as.character(tr$kanton), levels = lev)
    te$kanton <- factor(as.character(te$kanton), levels = lev)
  }
  if ("jahr" %in% vars && jahr_faktor) {
    lev <- sort(unique(train$jahr))
    tr$jahr <- factor(tr$jahr, levels = lev); te$jahr <- factor(te$jahr, levels = lev)
  }
  list(train = tr, test = te)
}
dummy_matrix <- function(tr, te) {
  fm <- ~ . - 1
  mt <- model.matrix(fm, data = tr)
  me <- model.matrix(fm, data = te)
  miss <- setdiff(colnames(mt), colnames(me))
  if (length(miss)) me <- cbind(me, matrix(0, nrow(me), length(miss), dimnames = list(NULL, miss)))
  list(train = mt, test = me[, colnames(mt), drop = FALSE])
}

# ---- Modell: Nullmodell ---------------------------------------------------------
fit_null <- function(train, test, vars, ...) list(pred = rep(mean(train$y), nrow(test)), par = "Mittelwert Training")

# ---- Modell: lineare Regression ---------------------------------------------------
fit_lm <- function(train, test, vars, jahr_faktor = TRUE, ...) {
  d <- bereite_vor(train, test, vars, jahr_faktor)
  m <- lm(train$y ~ ., data = d$train)
  list(pred = as.numeric(predict(m, newdata = d$test)), par = "OLS")
}

# ---- Modell: GAM ---------------------------------------------------------------------
fit_gam <- function(train, test, vars, jahr_faktor = TRUE, k_smooth = NULL, ...) {
  if (is.null(k_smooth)) k_smooth <- if (nrow(train) > 600) 5 else 4
  d <- bereite_vor(train, test, vars, jahr_faktor)
  stetig <- setdiff(vars, c("kanton", "jahr"))
  stetig <- stetig[vapply(stetig, function(v) length(unique(d$train[[v]])) > k_smooth + 1, logical(1))]
  fix <- setdiff(vars, stetig)
  fm <- reformulate(c(sprintf("s(%s, k = %d)", stetig, k_smooth), fix), response = "y")
  dd <- cbind(y = train$y, d$train)
  m <- mgcv::gam(fm, data = dd, method = "REML", select = TRUE)
  list(pred = as.numeric(predict(m, newdata = d$test)), par = paste0("k=", k_smooth, "; REML; select=TRUE"))
}

# ---- Modell: Random Forest (Tuning über innere gruppierte Folds) -------------------------
rf_raster <- function(p, n) {
  mt <- sort(unique(pmax(1, c(2, ceiling(p / 2), p))))
  mn <- if (n > 800) c(5, 15, 40) else c(3, 6, 12)
  expand.grid(mtry = mt, min.node.size = mn)
}
rf_fit_pred <- function(tr, ytr, te, mtry, mns, seed) {
  m <- ranger::ranger(x = tr, y = ytr, num.trees = 500, mtry = mtry, min.node.size = mns,
                      seed = seed, num.threads = 2, respect.unordered.factors = "order")
  predict(m, data = te)$predictions
}
fit_rf <- function(train, test, vars, jahr_faktor = FALSE, seed = 1, ...) {
  d <- bereite_vor(train, test, vars, jahr_faktor = FALSE)
  rast <- rf_raster(length(vars), nrow(train))
  fid <- inner_folds(train, CFG$k_inner, seed)
  err <- vapply(seq_len(nrow(rast)), function(i) {
    mean(vapply(sort(unique(fid)), function(f) {
      a <- fid != f; b <- fid == f
      p <- rf_fit_pred(d$train[a, , drop = FALSE], train$y[a], d$train[b, , drop = FALSE],
                       rast$mtry[i], rast$min.node.size[i], seed)
      mean((train$y[b] - p)^2)
    }, numeric(1)))
  }, numeric(1))
  b <- which.min(err)
  pred <- rf_fit_pred(d$train, train$y, d$test, rast$mtry[b], rast$min.node.size[b], seed)
  list(pred = pred, par = sprintf("mtry=%d; min.node.size=%d; inner_MSE=%.2f", rast$mtry[b], rast$min.node.size[b], err[b]))
}

# ---- Modell: Gradient Boosting (xgboost) -----------------------------------------------------
xgb_raster <- function(n) {
  expand.grid(eta = c(0.03, 0.1), max_depth = c(2, 3), stringsAsFactors = FALSE)
}
xgb_fit <- function(Xtr, ytr, eta, depth, nrounds, seed) {
  dtr <- xgboost::xgb.DMatrix(Xtr, label = ytr)
  xgboost::xgb.train(params = list(objective = "reg:squarederror", eta = eta, max_depth = depth,
                                   min_child_weight = 5, subsample = 0.8, colsample_bytree = 0.8,
                                   nthread = 2, seed = seed, verbosity = 0),
                     data = dtr, nrounds = nrounds)
}
fit_xgb <- function(train, test, vars, jahr_faktor = FALSE, seed = 1, ...) {
  d <- bereite_vor(train, test, vars, jahr_faktor = FALSE)
  dm <- dummy_matrix(d$train, d$test)
  rast <- xgb_raster(nrow(train)); rounds <- c(50, 100, 200, 400)
  fid <- inner_folds(train, CFG$k_inner, seed)
  res <- list()
  for (i in seq_len(nrow(rast))) {
    mse <- matrix(NA_real_, length(unique(fid)), length(rounds))
    for (jf in seq_along(sort(unique(fid)))) {
      f <- sort(unique(fid))[jf]; a <- fid != f; b <- fid == f
      m <- xgb_fit(dm$train[a, , drop = FALSE], train$y[a], rast$eta[i], rast$max_depth[i], max(rounds), seed)
      for (r in seq_along(rounds)) {
        p <- predict(m, dm$train[b, , drop = FALSE], iterationrange = c(1, rounds[r]))
        mse[jf, r] <- mean((train$y[b] - p)^2)
      }
    }
    res[[i]] <- tibble(i = i, nrounds = rounds, mse = colMeans(mse))
  }
  res <- bind_rows(res); best <- res[which.min(res$mse), ]
  m <- xgb_fit(dm$train, train$y, rast$eta[best$i], rast$max_depth[best$i], best$nrounds, seed)
  list(pred = as.numeric(predict(m, dm$test)),
       par = sprintf("eta=%.2f; max_depth=%d; nrounds=%d; inner_MSE=%.2f", rast$eta[best$i], rast$max_depth[best$i], best$nrounds, best$mse))
}

MODELLE <- list(Nullmodell = fit_null, lm = fit_lm, `Random Forest` = fit_rf, GAM = fit_gam, XGBoost = fit_xgb)

# ---- Äussere Kreuzvalidierung -----------------------------------------------------------------
# daten: Spalten y, bfs_nr, kanton, jahr + Prädiktoren; fold_tab: bfs_nr -> fold (oder fold je Zeile)
cv_aussen <- function(daten, fold_vec, specs, modelle = MODELLE, jahr_faktor = TRUE, label = "",
                      train_fn = NULL, verbose = TRUE) {
  folds <- sort(unique(fold_vec[!is.na(fold_vec)]))
  out_pred <- list(); out_par <- list()
  for (f in folds) {
    i_te <- which(fold_vec == f)
    i_tr <- if (is.null(train_fn)) which(fold_vec != f | is.na(fold_vec)) else which(train_fn(daten, f))
    te <- daten[i_te, , drop = FALSE]; tr <- daten[i_tr, , drop = FALSE]
    stopifnot(length(intersect(tr$bfs_nr, te$bfs_nr)) == 0 || !is.null(train_fn))  # keine Gemeinde in Train und Test
    for (sp in names(specs)) {
      for (mn in names(modelle)) {
        res <- modelle[[mn]](tr, te, specs[[sp]], jahr_faktor = jahr_faktor, seed = CFG$seed + as.integer(f))
        out_pred[[length(out_pred) + 1]] <- tibble(validierung = label, spezifikation = sp, modell = mn, fold = f,
                                                   bfs_nr = te$bfs_nr, jahr = te$jahr, y = te$y, pred = res$pred)
        out_par[[length(out_par) + 1]] <- tibble(validierung = label, spezifikation = sp, modell = mn, fold = f,
                                                 n_train = nrow(tr), n_test = nrow(te), hyperparameter = res$par)
      }
    }
    if (verbose) cat(sprintf("  [%s] Fold %s (%d von %d) fertig\n", label, f, match(f, folds), length(folds)))
  }
  list(pred = bind_rows(out_pred), par = bind_rows(out_par))
}

fold_metriken <- function(pred) {
  pred %>% group_by(validierung, spezifikation, modell, fold) %>% group_modify(~ metriken(.x$y, .x$pred)) %>% ungroup()
}
zusammenfassung <- function(fm, pred) {
  agg <- fm %>% group_by(validierung, spezifikation, modell) %>%
    summarise(folds = n(), across(c(r2, rmse, mae, mse), list(mittel = mean, sd = sd), .names = "{.col}_{.fn}"), .groups = "drop")
  gesamt <- pred %>% group_by(validierung, spezifikation, modell) %>% group_modify(~ metriken(.x$y, .x$pred)) %>% ungroup() %>%
    transmute(validierung, spezifikation, modell, n_oof = n, r2_oof_gesamt = r2, rmse_oof_gesamt = rmse)
  mse_null <- pred %>% filter(modell == "Nullmodell") %>% group_by(validierung, spezifikation) %>%
    summarise(mse_null = mean((y - pred)^2), .groups = "drop")
  left_join(agg, gesamt, by = c("validierung", "spezifikation", "modell")) %>%
    left_join(mse_null, by = c("validierung", "spezifikation")) %>%
    mutate(skill_vs_null = 1 - (rmse_oof_gesamt^2) / mse_null) %>% select(-mse_null)
}

# ---- Zusätzlicher Prognosebeitrag der erweiterten Spezifikation (Cluster-Bootstrap über Gemeinden) ----
inkrement_bootstrap <- function(pred, basis = "basis", erweitert = "erweitert", B = CFG$n_boot, seed = CFG$seed) {
  set.seed(seed)
  res <- list()
  for (mn in setdiff(unique(pred$modell), character(0))) {
    for (v in unique(pred$validierung)) {
      a <- pred %>% filter(modell == mn, validierung == v, spezifikation == basis) %>% select(bfs_nr, jahr, y, p0 = pred)
      b <- pred %>% filter(modell == mn, validierung == v, spezifikation == erweitert) %>% select(bfs_nr, jahr, p1 = pred)
      d <- inner_join(a, b, by = c("bfs_nr", "jahr")) %>% mutate(dse = (y - p0)^2 - (y - p1)^2)
      g <- d %>% group_by(bfs_nr) %>% summarise(s = sum(dse), n = n(), .groups = "drop")
      est <- sum(g$s) / sum(g$n)
      bs <- replicate(B, { i <- sample.int(nrow(g), replace = TRUE); sum(g$s[i]) / sum(g$n[i]) })
      res[[length(res) + 1]] <- tibble(validierung = v, modell = mn, delta_mse = est,
                                       ci_lo = unname(quantile(bs, .025)), ci_hi = unname(quantile(bs, .975)),
                                       delta_rmse = sqrt(mean((d$y - d$p0)^2)) - sqrt(mean((d$y - d$p1)^2)),
                                       anteil_bootstrap_positiv = mean(bs > 0))
    }
  }
  bind_rows(res)
}
