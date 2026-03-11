###############################################################################
#
#  MASTER'S THESIS STATISTICAL ANALYSIS SCRIPT
#  ============================================
#
#  Title:   Quality of Physical Activity Information on Traditional Websites
#           Versus Social Media Platforms: A Cross-Sectional Content Analysis
#           Using DISCERN and JAMA Benchmarks
#
#  Author:  Ayokunle Ademola-John
#  Program: Master of Public Health (MPH), Lithuanian Sports University
#  Supervisor: Dr. Antanas Usas
#
#  HOW TO RUN:
#  1. Set your working directory to the /analysis/ folder, or open the
#     RStudio project from there.
#  2. Ensure ../data/csv/master_dataset.csv exists with all 200 scored items.
#  3. (Optional) Ensure ../data/csv/second_rater_scores.csv exists for IRR.
#  4. Run the entire script: source("analysis_script.R")
#     Or run section-by-section in RStudio.
#  5. Output is saved to:
#       - analysis/output/tables/   (CSV tables)
#       - analysis/output/figures/  (PNG figures)
#       - analysis/output/analysis_report.txt  (narrative summary)
#
#  PACKAGES REQUIRED:
#    tidyverse, ggplot2, FSA, dunn.test, irr, rstatix, DescTools,
#    effectsize, flextable, officer, scales
#
#  DATE CREATED: 2026-02-26
#
###############################################################################


# =============================================================================
# SECTION 0: SETUP & DATA IMPORT
# =============================================================================

cat("\n")
cat("================================================================\n")
cat("  THESIS ANALYSIS SCRIPT — Starting\n")
cat("================================================================\n\n")

# --- 0a. Install and load required packages ----------------------------------

required_packages <- c(
  "tidyverse", "ggplot2", "FSA", "dunn.test", "irr", "rstatix",
  "DescTools", "effectsize", "flextable", "officer", "scales"
)

install_if_missing <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    cat(paste0("  Installing package: ", pkg, "\n"))
    install.packages(pkg, repos = "https://cran.r-project.org", quiet = TRUE)
  }
}

cat("Checking and installing required packages...\n")
invisible(lapply(required_packages, install_if_missing))

# Load all packages
suppressPackageStartupMessages({
  library(tidyverse)
  library(ggplot2)
  library(FSA)
  library(dunn.test)
  library(irr)
  library(rstatix)
  library(DescTools)
  library(effectsize)
  library(flextable)
  library(officer)
  library(scales)
})

cat("All packages loaded successfully.\n\n")

# --- 0b. Create output directories -------------------------------------------

output_dir     <- file.path(getwd(), "output")
tables_dir     <- file.path(output_dir, "tables")
figures_dir    <- file.path(output_dir, "figures")

dir.create(tables_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(figures_dir, recursive = TRUE, showWarnings = FALSE)

cat(paste0("Output directories created/verified:\n"))
cat(paste0("  Tables:  ", tables_dir, "\n"))
cat(paste0("  Figures: ", figures_dir, "\n\n"))

# --- 0c. Track section completion ---------------------------------------------

section_status <- list()  # Will store TRUE/FALSE for each section

# --- 0d. Set global ggplot theme (APA-style, publication quality) -------------

# Attempt to use Times New Roman; fall back to serif if unavailable
apa_theme <- theme_minimal(base_size = 12) +
  theme(
    text = element_text(family = "serif"),
    plot.title = element_text(face = "bold", size = 14, hjust = 0.5),
    plot.subtitle = element_text(size = 11, hjust = 0.5),
    axis.title = element_text(size = 12),
    axis.text = element_text(size = 10),
    legend.title = element_text(size = 11),
    legend.text = element_text(size = 10),
    panel.grid.major = element_line(color = "grey90", linewidth = 0.3),
    panel.grid.minor = element_blank(),
    strip.text = element_text(size = 11, face = "bold"),
    plot.margin = margin(10, 15, 10, 15)
  )

theme_set(apa_theme)

# Platform colour palette
platform_colors <- c(
  "Website"   = "#2166AC",
  "YouTube"   = "#D62728",
  "TikTok"    = "#1A1A1A",
  "Instagram" = "#7B2D8E"
)

# --- 0e. Read the master dataset ----------------------------------------------

data_path <- file.path(getwd(), "..", "data", "csv", "master_dataset.csv")
data_path <- normalizePath(data_path, mustWork = FALSE)

cat(paste0("Reading master dataset from:\n  ", data_path, "\n"))

if (!file.exists(data_path)) {
  stop("ERROR: master_dataset.csv not found at the expected path.\n",
       "  Expected: ", data_path, "\n",
       "  Please ensure the file exists before running this script.")
}

df <- read.csv(data_path, stringsAsFactors = FALSE, na.strings = c("", "NA"))

cat(paste0("  Rows loaded: ", nrow(df), "\n"))
cat(paste0("  Columns loaded: ", ncol(df), "\n\n"))

# --- 0f. Convert categorical variables to factors with correct levels ----------

# Platform (ordered for consistent display)
df$Platform <- factor(df$Platform,
                       levels = c("Website", "YouTube", "TikTok", "Instagram"))

# Creator Type
df$Creator_Type <- factor(df$Creator_Type,
                          levels = c("Healthcare professional",
                                     "Certified fitness professional",
                                     "Fitness influencer",
                                     "General user",
                                     "Organization"))

# Content Format
df$Content_Format <- factor(df$Content_Format,
                            levels = c("Text article",
                                       "Long video (>5min)",
                                       "Short video (<60s)",
                                       "Image+caption",
                                       "Carousel"))

# DISCERN Category (ordered)
df$DISCERN_Category <- factor(df$DISCERN_Category,
                              levels = c("Very Poor", "Poor", "Fair",
                                         "Good", "Excellent"),
                              ordered = TRUE)

# JAMA binary variables: ensure "Y"/"N"
jama_cols <- c("JAMA_Authorship", "JAMA_Attribution",
               "JAMA_Disclosure", "JAMA_Currency")
for (col in jama_cols) {
  df[[col]] <- factor(df[[col]], levels = c("Y", "N"))
}

# --- 0g. Create Professional binary variable ----------------------------------

df$Professional <- ifelse(
  df$Creator_Type %in% c("Healthcare professional",
                          "Certified fitness professional"),
  "Professional",
  "Non-professional"
)
df$Professional <- factor(df$Professional,
                          levels = c("Professional", "Non-professional"))

cat("Categorical variables converted to factors.\n")
cat("Professional binary variable created.\n\n")

# --- 0h. Data quality checks --------------------------------------------------

cat("=== DATA QUALITY CHECKS ===\n")

# Check for missing values in key columns
key_cols <- c("Item_ID", "Platform", "Creator_Type", "Content_Format",
              paste0("DISCERN_Q", 1:16), "DISCERN_Total",
              "DISCERN_Section1", "DISCERN_Section2",
              jama_cols, "JAMA_Total")

missing_summary <- sapply(key_cols, function(col) {
  if (col %in% names(df)) sum(is.na(df[[col]])) else NA
})

if (any(missing_summary > 0, na.rm = TRUE)) {
  cat("WARNING: Missing values detected in key columns:\n")
  problematic <- missing_summary[missing_summary > 0 & !is.na(missing_summary)]
  for (nm in names(problematic)) {
    cat(paste0("  ", nm, ": ", problematic[nm], " missing\n"))
  }
} else {
  cat("  No missing values in key analysis columns.\n")
}

# Check columns that should exist
missing_cols <- key_cols[!key_cols %in% names(df)]
if (length(missing_cols) > 0) {
  cat(paste0("WARNING: Expected columns not found: ",
             paste(missing_cols, collapse = ", "), "\n"))
}

# Check DISCERN_Total range (should be 16-80)
if ("DISCERN_Total" %in% names(df)) {
  out_of_range <- sum(df$DISCERN_Total < 16 | df$DISCERN_Total > 80,
                      na.rm = TRUE)
  if (out_of_range > 0) {
    cat(paste0("WARNING: ", out_of_range,
               " DISCERN_Total values outside valid range (16-80).\n"))
  } else {
    cat("  All DISCERN_Total values within valid range (16-80).\n")
  }
}

# Check JAMA_Total range (0-4)
if ("JAMA_Total" %in% names(df)) {
  out_of_range_j <- sum(df$JAMA_Total < 0 | df$JAMA_Total > 4, na.rm = TRUE)
  if (out_of_range_j > 0) {
    cat(paste0("WARNING: ", out_of_range_j,
               " JAMA_Total values outside valid range (0-4).\n"))
  } else {
    cat("  All JAMA_Total values within valid range (0-4).\n")
  }
}

# Check sample sizes per platform
cat("\n  Sample sizes per platform:\n")
print(table(df$Platform))

# Check individual DISCERN items (should be 1-5)
discern_q_cols <- paste0("DISCERN_Q", 1:16)
discern_q_present <- discern_q_cols[discern_q_cols %in% names(df)]
if (length(discern_q_present) > 0) {
  for (qcol in discern_q_present) {
    bad <- sum(df[[qcol]] < 1 | df[[qcol]] > 5, na.rm = TRUE)
    if (bad > 0) {
      cat(paste0("WARNING: ", qcol, " has ", bad,
                 " values outside 1-5 range.\n"))
    }
  }
}

cat("\n=== DATA QUALITY CHECKS COMPLETE ===\n\n")

# --- Initialize report text ---------------------------------------------------

report_lines <- c(
  "================================================================",
  "  STATISTICAL ANALYSIS REPORT",
  paste0("  Generated: ", Sys.time()),
  "================================================================",
  "",
  "Study: Quality of Physical Activity Information on Traditional",
  "Websites Versus Social Media Platforms",
  "Author: Ayokunle Ademola-John",
  paste0("Total sample: N = ", nrow(df)),
  ""
)


# =============================================================================
# SECTION 1: SAMPLE CHARACTERISTICS (Table 1)
# =============================================================================

cat("\n--- SECTION 1: Sample Characteristics ---\n")

section_status[["1_Sample_Characteristics"]] <- tryCatch({

  # 1a. Platform x Content_Format crosstab
  crosstab_format <- table(df$Platform, df$Content_Format)
  crosstab_format_df <- as.data.frame.matrix(crosstab_format)
  crosstab_format_df$Platform <- rownames(crosstab_format_df)
  crosstab_format_df <- crosstab_format_df[, c("Platform",
                                                setdiff(names(crosstab_format_df),
                                                        "Platform"))]

  cat("  Platform x Content Format crosstab:\n")
  print(crosstab_format)

  # 1b. Platform x Creator_Type crosstab
  crosstab_creator <- table(df$Platform, df$Creator_Type)
  crosstab_creator_df <- as.data.frame.matrix(crosstab_creator)
  crosstab_creator_df$Platform <- rownames(crosstab_creator_df)
  crosstab_creator_df <- crosstab_creator_df[, c("Platform",
                                                  setdiff(names(crosstab_creator_df),
                                                          "Platform"))]

  cat("\n  Platform x Creator Type crosstab:\n")
  print(crosstab_creator)

  # 1c. Engagement metrics by platform
  engagement_cols <- c("Views", "Likes", "Shares", "Comments")
  engagement_present <- engagement_cols[engagement_cols %in% names(df)]

  if (length(engagement_present) > 0) {
    engagement_summary <- df %>%
      group_by(Platform) %>%
      summarise(
        across(all_of(engagement_present),
               list(
                 Median = ~median(.x, na.rm = TRUE),
                 IQR    = ~IQR(.x, na.rm = TRUE),
                 Min    = ~min(.x, na.rm = TRUE),
                 Max    = ~max(.x, na.rm = TRUE)
               ),
               .names = "{.col}_{.fn}"),
        .groups = "drop"
      )

    cat("\n  Engagement metrics summary by platform:\n")
    print(as.data.frame(engagement_summary))
  } else {
    engagement_summary <- NULL
    cat("  No engagement metric columns found.\n")
  }

  # 1d. Professional vs Non-professional counts
  prof_table <- table(df$Platform, df$Professional)
  cat("\n  Platform x Professional status:\n")
  print(prof_table)

  # Save Table 1 components
  write.csv(crosstab_format_df,
            file.path(tables_dir, "table1a_platform_x_format.csv"),
            row.names = FALSE)
  write.csv(crosstab_creator_df,
            file.path(tables_dir, "table1b_platform_x_creator.csv"),
            row.names = FALSE)
  if (!is.null(engagement_summary)) {
    write.csv(engagement_summary,
              file.path(tables_dir, "table1c_engagement_by_platform.csv"),
              row.names = FALSE)
  }

  # Add to report
  report_lines <<- c(report_lines,
    "----------------------------------------------------------------",
    "SECTION 1: SAMPLE CHARACTERISTICS",
    "----------------------------------------------------------------",
    "",
    paste0("Total items analyzed: N = ", nrow(df)),
    paste0("Items per platform: ",
           paste(names(table(df$Platform)), "=",
                 as.numeric(table(df$Platform)), collapse = ", ")),
    ""
  )

  cat("  Section 1 completed successfully.\n")
  TRUE
}, error = function(e) {
  cat(paste0("  ERROR in Section 1: ", e$message, "\n"))
  FALSE
})


# =============================================================================
# SECTION 2: INTER-RATER RELIABILITY (Table 2)
# =============================================================================

cat("\n--- SECTION 2: Inter-Rater Reliability ---\n")

section_status[["2_InterRater_Reliability"]] <- tryCatch({

  # Try both possible filenames
  irr_path1 <- file.path(getwd(), "..", "data", "csv",
                          "second_rater_scores.csv")
  irr_path2 <- file.path(getwd(), "..", "data", "csv",
                          "second_rater.csv")
  irr_path1 <- normalizePath(irr_path1, mustWork = FALSE)
  irr_path2 <- normalizePath(irr_path2, mustWork = FALSE)

  irr_path <- NA
  if (file.exists(irr_path1)) {
    irr_path <- irr_path1
  } else if (file.exists(irr_path2)) {
    irr_path <- irr_path2
  }

  if (is.na(irr_path)) {
    cat("  NOTE: Second rater file not found. Checked:\n")
    cat(paste0("    ", irr_path1, "\n"))
    cat(paste0("    ", irr_path2, "\n"))
    cat("  Skipping inter-rater reliability analysis.\n")
    cat("  Place the file and re-run this section when ready.\n")

    report_lines <<- c(report_lines,
      "----------------------------------------------------------------",
      "SECTION 2: INTER-RATER RELIABILITY",
      "----------------------------------------------------------------",
      "",
      "Second rater data file not found. Section skipped.",
      ""
    )

    TRUE  # Not a failure; data simply not available yet

  } else {
    cat(paste0("  Reading second rater data from:\n  ", irr_path, "\n"))

    df_rater2 <- read.csv(irr_path, stringsAsFactors = FALSE,
                          na.strings = c("", "NA"))

    cat(paste0("  Second rater items: ", nrow(df_rater2), "\n"))

    # Merge on Item_ID
    # Suffix: .r1 = main rater, .r2 = second rater
    irr_merged <- merge(
      df[, c("Item_ID", "DISCERN_Total", "DISCERN_Section1",
             "DISCERN_Section2", jama_cols)],
      df_rater2[, c("Item_ID",
                     intersect(names(df_rater2),
                               c("DISCERN_Total", "DISCERN_Section1",
                                 "DISCERN_Section2", jama_cols)))],
      by = "Item_ID",
      suffixes = c(".r1", ".r2")
    )

    cat(paste0("  Matched items for IRR: ", nrow(irr_merged), "\n"))

    if (nrow(irr_merged) < 5) {
      cat("  WARNING: Fewer than 5 matched items. IRR may be unreliable.\n")
    }

    # --- ICC for DISCERN_Total ---
    icc_total <- icc(
      irr_merged[, c("DISCERN_Total.r1", "DISCERN_Total.r2")],
      model = "twoway",
      type  = "agreement",
      unit  = "single"
    )
    cat("\n  ICC for DISCERN_Total:\n")
    cat(paste0("    ICC = ", round(icc_total$value, 3),
               "  95% CI [", round(icc_total$lbound, 3), ", ",
               round(icc_total$ubound, 3), "]\n"))

    # --- ICC for DISCERN_Section1 ---
    icc_s1 <- icc(
      irr_merged[, c("DISCERN_Section1.r1", "DISCERN_Section1.r2")],
      model = "twoway",
      type  = "agreement",
      unit  = "single"
    )
    cat(paste0("    ICC Section 1 = ", round(icc_s1$value, 3),
               "  95% CI [", round(icc_s1$lbound, 3), ", ",
               round(icc_s1$ubound, 3), "]\n"))

    # --- ICC for DISCERN_Section2 ---
    icc_s2 <- icc(
      irr_merged[, c("DISCERN_Section2.r1", "DISCERN_Section2.r2")],
      model = "twoway",
      type  = "agreement",
      unit  = "single"
    )
    cat(paste0("    ICC Section 2 = ", round(icc_s2$value, 3),
               "  95% CI [", round(icc_s2$lbound, 3), ", ",
               round(icc_s2$ubound, 3), "]\n"))

    # --- Cohen's kappa for each JAMA criterion ---
    kappa_results <- data.frame(
      Criterion = character(),
      Kappa = numeric(),
      p_value = numeric(),
      Interpretation = character(),
      stringsAsFactors = FALSE
    )

    interpret_kappa <- function(k) {
      if (is.na(k)) return("N/A")
      if (k < 0.20) return("Poor")
      if (k < 0.40) return("Fair")
      if (k < 0.60) return("Moderate")
      if (k < 0.80) return("Substantial")
      return("Almost perfect")
    }

    for (jcol in jama_cols) {
      col_r1 <- paste0(jcol, ".r1")
      col_r2 <- paste0(jcol, ".r2")

      if (col_r1 %in% names(irr_merged) & col_r2 %in% names(irr_merged)) {
        # Convert to factor with same levels for kappa
        r1_vals <- factor(irr_merged[[col_r1]], levels = c("Y", "N"))
        r2_vals <- factor(irr_merged[[col_r2]], levels = c("Y", "N"))

        kap <- kappa2(cbind(as.numeric(r1_vals), as.numeric(r2_vals)))

        kappa_results <- rbind(kappa_results, data.frame(
          Criterion = gsub("JAMA_", "", jcol),
          Kappa = round(kap$value, 3),
          p_value = round(kap$p.value, 4),
          Interpretation = interpret_kappa(kap$value),
          stringsAsFactors = FALSE
        ))

        cat(paste0("    Cohen's kappa (", gsub("JAMA_", "", jcol), ") = ",
                   round(kap$value, 3), ", p = ",
                   format(kap$p.value, digits = 4), " [",
                   interpret_kappa(kap$value), "]\n"))
      }
    }

    # Build Table 2
    table2 <- data.frame(
      Measure = c("DISCERN Total (ICC)", "DISCERN Section 1 (ICC)",
                  "DISCERN Section 2 (ICC)",
                  paste0("JAMA ", kappa_results$Criterion, " (kappa)")),
      Statistic = c(
        round(icc_total$value, 3), round(icc_s1$value, 3),
        round(icc_s2$value, 3), kappa_results$Kappa
      ),
      CI_Lower = c(
        round(icc_total$lbound, 3), round(icc_s1$lbound, 3),
        round(icc_s2$lbound, 3), rep(NA, nrow(kappa_results))
      ),
      CI_Upper = c(
        round(icc_total$ubound, 3), round(icc_s1$ubound, 3),
        round(icc_s2$ubound, 3), rep(NA, nrow(kappa_results))
      ),
      p_value = c(
        NA, NA, NA, kappa_results$p_value
      ),
      Interpretation = c(
        interpret_kappa(icc_total$value),
        interpret_kappa(icc_s1$value),
        interpret_kappa(icc_s2$value),
        kappa_results$Interpretation
      ),
      stringsAsFactors = FALSE
    )

    write.csv(table2, file.path(tables_dir, "table2_irr.csv"),
              row.names = FALSE)

    # Report
    report_lines <<- c(report_lines,
      "----------------------------------------------------------------",
      "SECTION 2: INTER-RATER RELIABILITY",
      "----------------------------------------------------------------",
      "",
      paste0("N = ", nrow(irr_merged), " items assessed by both raters."),
      "",
      paste0("DISCERN Total ICC = ", round(icc_total$value, 3),
             " (95% CI: ", round(icc_total$lbound, 3), "-",
             round(icc_total$ubound, 3), "), indicating ",
             tolower(interpret_kappa(icc_total$value)), " agreement."),
      paste0("DISCERN Section 1 ICC = ", round(icc_s1$value, 3),
             " (95% CI: ", round(icc_s1$lbound, 3), "-",
             round(icc_s1$ubound, 3), ")."),
      paste0("DISCERN Section 2 ICC = ", round(icc_s2$value, 3),
             " (95% CI: ", round(icc_s2$lbound, 3), "-",
             round(icc_s2$ubound, 3), ")."),
      ""
    )

    for (i in seq_len(nrow(kappa_results))) {
      report_lines <<- c(report_lines,
        paste0("Cohen's kappa for JAMA ", kappa_results$Criterion[i],
               " = ", kappa_results$Kappa[i],
               " (p = ", kappa_results$p_value[i], "), indicating ",
               tolower(kappa_results$Interpretation[i]), " agreement.")
      )
    }
    report_lines <<- c(report_lines, "")

    cat("  Section 2 completed successfully.\n")
    TRUE
  }
}, error = function(e) {
  cat(paste0("  ERROR in Section 2: ", e$message, "\n"))
  FALSE
})


# =============================================================================
# SECTION 3: DISCERN ANALYSIS (Tables 3 & 4)
# =============================================================================

cat("\n--- SECTION 3: DISCERN Analysis ---\n")

section_status[["3_DISCERN_Analysis"]] <- tryCatch({

  # ---- 3a. Descriptive Statistics ----

  cat("  3a. Descriptive statistics for DISCERN_Total by Platform...\n")

  discern_desc <- df %>%
    group_by(Platform) %>%
    summarise(
      N      = n(),
      Median = median(DISCERN_Total, na.rm = TRUE),
      IQR    = IQR(DISCERN_Total, na.rm = TRUE),
      Q1     = quantile(DISCERN_Total, 0.25, na.rm = TRUE),
      Q3     = quantile(DISCERN_Total, 0.75, na.rm = TRUE),
      Mean   = round(mean(DISCERN_Total, na.rm = TRUE), 2),
      SD     = round(sd(DISCERN_Total, na.rm = TRUE), 2),
      Min    = min(DISCERN_Total, na.rm = TRUE),
      Max    = max(DISCERN_Total, na.rm = TRUE),
      .groups = "drop"
    )

  # Overall row
  discern_overall <- df %>%
    summarise(
      Platform = "Overall",
      N      = n(),
      Median = median(DISCERN_Total, na.rm = TRUE),
      IQR    = IQR(DISCERN_Total, na.rm = TRUE),
      Q1     = quantile(DISCERN_Total, 0.25, na.rm = TRUE),
      Q3     = quantile(DISCERN_Total, 0.75, na.rm = TRUE),
      Mean   = round(mean(DISCERN_Total, na.rm = TRUE), 2),
      SD     = round(sd(DISCERN_Total, na.rm = TRUE), 2),
      Min    = min(DISCERN_Total, na.rm = TRUE),
      Max    = max(DISCERN_Total, na.rm = TRUE)
    )

  discern_desc_full <- bind_rows(discern_desc, discern_overall)

  cat("  DISCERN Total descriptive statistics by platform:\n")
  print(as.data.frame(discern_desc_full))

  # DISCERN item-level medians by platform
  discern_q_cols <- paste0("DISCERN_Q", 1:16)
  discern_q_present <- discern_q_cols[discern_q_cols %in% names(df)]

  if (length(discern_q_present) > 0) {
    item_medians <- df %>%
      group_by(Platform) %>%
      summarise(
        across(all_of(discern_q_present),
               ~median(.x, na.rm = TRUE),
               .names = "{.col}_Median"),
        .groups = "drop"
      )
    cat("\n  DISCERN item-level medians by platform computed.\n")
  }

  # DISCERN category frequency by platform
  discern_cat_table <- table(df$Platform, df$DISCERN_Category)
  discern_cat_pct <- prop.table(discern_cat_table, margin = 1) * 100

  cat("\n  DISCERN Category distribution by platform (%):\n")
  print(round(discern_cat_pct, 1))

  # ---- 3b. Inferential Statistics ----

  cat("\n  3b. Inferential statistics...\n")

  # Shapiro-Wilk test by group (test normality assumption)
  cat("\n  Shapiro-Wilk normality tests by platform:\n")
  shapiro_results <- df %>%
    group_by(Platform) %>%
    summarise(
      W = shapiro.test(DISCERN_Total)$statistic,
      p_value = shapiro.test(DISCERN_Total)$p.value,
      Normal = ifelse(shapiro.test(DISCERN_Total)$p.value > 0.05,
                      "Yes", "No"),
      .groups = "drop"
    )
  print(as.data.frame(shapiro_results))

  # Levene's test for homogeneity of variance
  levene_result <- levene_test(df, DISCERN_Total ~ Platform)
  cat(paste0("\n  Levene's test: F(", levene_result$df1, ", ",
             levene_result$df2, ") = ", round(levene_result$statistic, 3),
             ", p = ", format(levene_result$p, digits = 4), "\n"))

  # Kruskal-Wallis H test
  kw_test <- kruskal.test(DISCERN_Total ~ Platform, data = df)
  cat(paste0("\n  Kruskal-Wallis test: H(", kw_test$parameter, ") = ",
             round(kw_test$statistic, 3), ", p = ",
             format(kw_test$p.value, digits = 4), "\n"))

  # Effect size: epsilon-squared (eta-squared H)
  # epsilon_squared = (H - k + 1) / (n - k) where k = number of groups
  k <- length(unique(df$Platform))
  n_total <- nrow(df)
  epsilon_sq <- (kw_test$statistic - k + 1) / (n_total - k)
  epsilon_sq <- max(0, epsilon_sq)  # Cannot be negative

  # Interpretation of epsilon-squared
  interpret_eps <- function(e) {
    if (e < 0.01) return("negligible")
    if (e < 0.06) return("small")
    if (e < 0.14) return("moderate")
    return("large")
  }

  cat(paste0("  Effect size (epsilon-squared): ", round(epsilon_sq, 4),
             " [", interpret_eps(epsilon_sq), "]\n"))

  # Post-hoc: Dunn's test (if Kruskal-Wallis is significant)
  dunn_results <- NULL
  if (kw_test$p.value < 0.05) {
    cat("\n  Kruskal-Wallis significant. Performing Dunn's post-hoc test...\n")

    # Use FSA::dunnTest for clean output
    dunn_out <- dunnTest(DISCERN_Total ~ Platform, data = df,
                         method = "bonferroni")
    dunn_results <- dunn_out$res
    dunn_results$Significant <- ifelse(dunn_results$P.adj < 0.05, "Yes", "No")

    cat("\n  Dunn's post-hoc comparisons (Bonferroni corrected):\n")
    print(dunn_results)
  } else {
    cat("  Kruskal-Wallis not significant (p >= 0.05). No post-hoc needed.\n")
  }

  # ---- Save Tables ----

  # Table 3: Descriptive DISCERN
  write.csv(discern_desc_full,
            file.path(tables_dir, "table3_discern_descriptive.csv"),
            row.names = FALSE)

  # Table 4: Inferential results
  table4 <- data.frame(
    Test = "Kruskal-Wallis H",
    Statistic = round(kw_test$statistic, 3),
    df = kw_test$parameter,
    p_value = format(kw_test$p.value, digits = 4),
    Effect_Size = paste0("epsilon-sq = ", round(epsilon_sq, 4)),
    Effect_Interpretation = interpret_eps(epsilon_sq),
    stringsAsFactors = FALSE
  )

  if (!is.null(dunn_results)) {
    dunn_export <- dunn_results
    names(dunn_export) <- c("Comparison", "Z", "P_unadjusted",
                            "P_Bonferroni", "Significant")
    write.csv(dunn_export,
              file.path(tables_dir, "table4b_dunn_posthoc.csv"),
              row.names = FALSE)
  }

  write.csv(table4,
            file.path(tables_dir, "table4a_kruskal_wallis.csv"),
            row.names = FALSE)

  # Save DISCERN category table
  discern_cat_export <- as.data.frame.matrix(discern_cat_table)
  discern_cat_export$Platform <- rownames(discern_cat_export)
  discern_cat_export <- discern_cat_export[, c("Platform",
                                                setdiff(names(discern_cat_export),
                                                        "Platform"))]
  write.csv(discern_cat_export,
            file.path(tables_dir, "table3b_discern_categories.csv"),
            row.names = FALSE)

  # ---- Report text ----
  report_lines <<- c(report_lines,
    "----------------------------------------------------------------",
    "SECTION 3: DISCERN ANALYSIS",
    "----------------------------------------------------------------",
    "",
    "Descriptive Statistics:",
    ""
  )

  for (i in seq_len(nrow(discern_desc))) {
    report_lines <<- c(report_lines,
      paste0("  ", discern_desc$Platform[i], ": Median = ",
             discern_desc$Median[i],
             " (IQR = ", discern_desc$IQR[i],
             "; Q1 = ", discern_desc$Q1[i],
             ", Q3 = ", discern_desc$Q3[i],
             "), Mean = ", discern_desc$Mean[i],
             " (SD = ", discern_desc$SD[i], ")")
    )
  }

  report_lines <<- c(report_lines,
    "",
    "Normality:",
    paste0("  Shapiro-Wilk tests indicated that DISCERN_Total was ",
           ifelse(all(shapiro_results$Normal == "No"),
                  "not normally distributed for any platform,",
                  "not normally distributed for at least one platform,"),
           " supporting the use of non-parametric tests."),
    "",
    paste0("Levene's test for homogeneity of variance: F(",
           levene_result$df1, ", ", levene_result$df2, ") = ",
           round(levene_result$statistic, 3),
           ", p = ", format(levene_result$p, digits = 4), "."),
    "",
    paste0("A Kruskal-Wallis H test revealed a ",
           ifelse(kw_test$p.value < 0.05, "statistically significant",
                  "non-significant"),
           " difference in DISCERN Total scores across the four platforms, ",
           "H(", kw_test$parameter, ") = ",
           round(kw_test$statistic, 3),
           ", p = ", format(kw_test$p.value, digits = 4),
           ", epsilon-squared = ", round(epsilon_sq, 4),
           " (", interpret_eps(epsilon_sq), " effect)."),
    ""
  )

  if (!is.null(dunn_results)) {
    report_lines <<- c(report_lines,
      "Dunn's post-hoc pairwise comparisons (Bonferroni-corrected):"
    )
    for (i in seq_len(nrow(dunn_results))) {
      report_lines <<- c(report_lines,
        paste0("  ", dunn_results$Comparison[i], ": Z = ",
               round(dunn_results$Z[i], 3),
               ", p(adj) = ", format(dunn_results$P.adj[i], digits = 4),
               ifelse(dunn_results$P.adj[i] < 0.05, " *", ""))
      )
    }
    report_lines <<- c(report_lines, "")
  }

  cat("  Section 3 completed successfully.\n")
  TRUE
}, error = function(e) {
  cat(paste0("  ERROR in Section 3: ", e$message, "\n"))
  FALSE
})


# =============================================================================
# SECTION 4: JAMA ANALYSIS (Tables 5 & 6)
# =============================================================================

cat("\n--- SECTION 4: JAMA Analysis ---\n")

section_status[["4_JAMA_Analysis"]] <- tryCatch({

  jama_criteria <- c("JAMA_Authorship", "JAMA_Attribution",
                     "JAMA_Disclosure", "JAMA_Currency")

  # ---- 4a. Descriptive: Frequency and % meeting each criterion ----

  cat("  4a. JAMA compliance by platform...\n")

  jama_desc_list <- list()

  for (jcol in jama_criteria) {
    tbl <- table(df$Platform, df[[jcol]])
    # Count "Y" per platform
    y_counts <- ifelse("Y" %in% colnames(tbl), tbl[, "Y"], rep(0, nrow(tbl)))
    n_per_platform <- rowSums(tbl)
    pct <- round(y_counts / n_per_platform * 100, 1)

    jama_desc_list[[gsub("JAMA_", "", jcol)]] <- data.frame(
      Platform = names(y_counts),
      N_Yes = as.numeric(y_counts),
      N_Total = as.numeric(n_per_platform),
      Pct_Yes = pct,
      stringsAsFactors = FALSE
    )
  }

  # Combine into Table 5
  table5 <- data.frame(Platform = levels(df$Platform))
  for (crit in names(jama_desc_list)) {
    d <- jama_desc_list[[crit]]
    table5[[paste0(crit, "_n")]] <- d$N_Yes[match(table5$Platform,
                                                   d$Platform)]
    table5[[paste0(crit, "_pct")]] <- d$Pct_Yes[match(table5$Platform,
                                                       d$Platform)]
  }

  # Mean JAMA_Total by platform
  jama_mean <- df %>%
    group_by(Platform) %>%
    summarise(
      Mean_JAMA_Total = round(mean(JAMA_Total, na.rm = TRUE), 2),
      Median_JAMA_Total = median(JAMA_Total, na.rm = TRUE),
      SD_JAMA_Total = round(sd(JAMA_Total, na.rm = TRUE), 2),
      .groups = "drop"
    )

  table5 <- merge(table5, jama_mean, by = "Platform")

  cat("  JAMA compliance summary:\n")
  print(table5)

  # ---- 4b. Inferential: Chi-square / Fisher's exact ----

  cat("\n  4b. Chi-square / Fisher's exact tests for JAMA criteria...\n")

  chisq_results <- data.frame(
    Criterion = character(),
    Test_Used = character(),
    Statistic = numeric(),
    df = numeric(),
    p_value = numeric(),
    Cramers_V = numeric(),
    V_Interpretation = character(),
    stringsAsFactors = FALSE
  )

  interpret_v <- function(v, k) {
    # Interpretation depends on df* = min(r-1, c-1)
    # For 4x2 table, df* = 1
    if (v < 0.10) return("negligible")
    if (v < 0.30) return("small")
    if (v < 0.50) return("medium")
    return("large")
  }

  for (jcol in jama_criteria) {
    tbl <- table(df$Platform, df[[jcol]])

    # Check expected counts
    expected <- chisq.test(tbl)$expected
    use_fisher <- any(expected < 5)

    if (use_fisher) {
      # Fisher's exact test
      fisher_res <- fisher.test(tbl, simulate.p.value = TRUE, B = 10000)
      test_stat <- NA
      test_df <- NA
      test_p <- fisher_res$p.value
      test_name <- "Fisher's exact"
    } else {
      # Chi-square test
      chi_res <- chisq.test(tbl)
      test_stat <- round(chi_res$statistic, 3)
      test_df <- chi_res$parameter
      test_p <- chi_res$p.value
      test_name <- "Chi-square"
    }

    # Cramer's V
    cv <- CramerV(tbl)

    chisq_results <- rbind(chisq_results, data.frame(
      Criterion = gsub("JAMA_", "", jcol),
      Test_Used = test_name,
      Statistic = test_stat,
      df = test_df,
      p_value = round(test_p, 4),
      Cramers_V = round(cv, 3),
      V_Interpretation = interpret_v(cv),
      stringsAsFactors = FALSE
    ))

    cat(paste0("    ", gsub("JAMA_", "", jcol), ": ",
               test_name, ", p = ", format(test_p, digits = 4),
               ", Cramer's V = ", round(cv, 3), "\n"))
  }

  # Chi-square for JAMA_Total as categorical (0, 1, 2, 3, 4)
  jama_total_tbl <- table(df$Platform, df$JAMA_Total)
  expected_jt <- chisq.test(jama_total_tbl)$expected
  use_fisher_jt <- any(expected_jt < 5)

  if (use_fisher_jt) {
    fisher_jt <- fisher.test(jama_total_tbl,
                              simulate.p.value = TRUE, B = 10000)
    jt_p <- fisher_jt$p.value
    jt_name <- "Fisher's exact"
    jt_stat <- NA
    jt_df <- NA
  } else {
    chi_jt <- chisq.test(jama_total_tbl)
    jt_p <- chi_jt$p.value
    jt_name <- "Chi-square"
    jt_stat <- round(chi_jt$statistic, 3)
    jt_df <- chi_jt$parameter
  }

  cv_jt <- CramerV(jama_total_tbl)

  chisq_results <- rbind(chisq_results, data.frame(
    Criterion = "JAMA_Total (categorical)",
    Test_Used = jt_name,
    Statistic = jt_stat,
    df = jt_df,
    p_value = round(jt_p, 4),
    Cramers_V = round(cv_jt, 3),
    V_Interpretation = interpret_v(cv_jt),
    stringsAsFactors = FALSE
  ))

  cat(paste0("    JAMA_Total (categorical): ",
             jt_name, ", p = ", format(jt_p, digits = 4),
             ", Cramer's V = ", round(cv_jt, 3), "\n"))

  # ---- Save Tables ----
  write.csv(table5, file.path(tables_dir, "table5_jama_compliance.csv"),
            row.names = FALSE)
  write.csv(chisq_results, file.path(tables_dir, "table6_jama_chisquare.csv"),
            row.names = FALSE)

  # ---- Report text ----
  report_lines <<- c(report_lines,
    "----------------------------------------------------------------",
    "SECTION 4: JAMA BENCHMARK ANALYSIS",
    "----------------------------------------------------------------",
    ""
  )

  for (crit in names(jama_desc_list)) {
    d <- jama_desc_list[[crit]]
    report_lines <<- c(report_lines,
      paste0(crit, " compliance: ",
             paste(d$Platform, " = ", d$Pct_Yes, "%", collapse = "; "), ".")
    )
  }

  report_lines <<- c(report_lines, "")

  for (i in seq_len(nrow(chisq_results))) {
    row <- chisq_results[i, ]
    stat_str <- ifelse(is.na(row$Statistic), "",
                       paste0("chi-sq(", row$df, ") = ", row$Statistic, ", "))
    report_lines <<- c(report_lines,
      paste0(row$Criterion, ": ", row$Test_Used, ", ",
             stat_str,
             "p = ", row$p_value,
             ", Cramer's V = ", row$Cramers_V,
             " (", row$V_Interpretation, " effect).",
             ifelse(row$p_value < 0.05, " *", ""))
    )
  }
  report_lines <<- c(report_lines, "")

  cat("  Section 4 completed successfully.\n")
  TRUE
}, error = function(e) {
  cat(paste0("  ERROR in Section 4: ", e$message, "\n"))
  FALSE
})


# =============================================================================
# SECTION 5: CREATOR TYPE ANALYSIS (Table 7)
# =============================================================================

cat("\n--- SECTION 5: Creator Type Analysis ---\n")

section_status[["5_Creator_Type"]] <- tryCatch({

  # ---- 5a. Descriptive: DISCERN by Professional vs Non-professional ----

  cat("  5a. DISCERN by Professional status...\n")

  prof_desc <- df %>%
    group_by(Professional) %>%
    summarise(
      N      = n(),
      Median = median(DISCERN_Total, na.rm = TRUE),
      IQR    = IQR(DISCERN_Total, na.rm = TRUE),
      Q1     = quantile(DISCERN_Total, 0.25, na.rm = TRUE),
      Q3     = quantile(DISCERN_Total, 0.75, na.rm = TRUE),
      Mean   = round(mean(DISCERN_Total, na.rm = TRUE), 2),
      SD     = round(sd(DISCERN_Total, na.rm = TRUE), 2),
      .groups = "drop"
    )

  cat("  Professional vs Non-professional DISCERN scores:\n")
  print(as.data.frame(prof_desc))

  # ---- 5b. Mann-Whitney U test ----

  cat("\n  5b. Mann-Whitney U test...\n")

  mw_test <- wilcox.test(DISCERN_Total ~ Professional, data = df,
                          exact = FALSE)

  cat(paste0("    Mann-Whitney U: W = ", mw_test$statistic,
             ", p = ", format(mw_test$p.value, digits = 4), "\n"))

  # Effect size: rank-biserial correlation
  # r = 1 - (2U) / (n1 * n2)
  n1 <- sum(df$Professional == "Professional", na.rm = TRUE)
  n2 <- sum(df$Professional == "Non-professional", na.rm = TRUE)

  # Using rstatix for cleaner effect size
  mw_effect <- df %>%
    wilcox_effsize(DISCERN_Total ~ Professional)

  r_effect <- mw_effect$effsize
  r_magnitude <- mw_effect$magnitude

  cat(paste0("    Rank-biserial correlation: r = ", round(r_effect, 3),
             " (", r_magnitude, ")\n"))

  # ---- 5c. Breakdown by platform ----

  cat("\n  5c. DISCERN by Professional status within each platform...\n")

  prof_by_platform <- df %>%
    group_by(Platform, Professional) %>%
    summarise(
      N      = n(),
      Median = median(DISCERN_Total, na.rm = TRUE),
      IQR    = IQR(DISCERN_Total, na.rm = TRUE),
      Mean   = round(mean(DISCERN_Total, na.rm = TRUE), 2),
      .groups = "drop"
    )

  print(as.data.frame(prof_by_platform))

  # Mann-Whitney within each platform (only if both groups present
  # and n >= 3 in each)
  cat("\n  Platform-specific Mann-Whitney U tests:\n")
  platform_mw_results <- data.frame()

  for (plat in levels(df$Platform)) {
    plat_data <- df %>% filter(Platform == plat)
    n_prof <- sum(plat_data$Professional == "Professional", na.rm = TRUE)
    n_nonprof <- sum(plat_data$Professional == "Non-professional",
                     na.rm = TRUE)

    if (n_prof >= 3 & n_nonprof >= 3) {
      mw_plat <- wilcox.test(DISCERN_Total ~ Professional,
                              data = plat_data, exact = FALSE)
      eff_plat <- plat_data %>% wilcox_effsize(DISCERN_Total ~ Professional)

      platform_mw_results <- rbind(platform_mw_results, data.frame(
        Platform = plat,
        N_Professional = n_prof,
        N_NonProfessional = n_nonprof,
        W = mw_plat$statistic,
        p_value = round(mw_plat$p.value, 4),
        r = round(eff_plat$effsize, 3),
        Magnitude = as.character(eff_plat$magnitude),
        stringsAsFactors = FALSE
      ))

      cat(paste0("    ", plat, ": W = ", mw_plat$statistic,
                 ", p = ", format(mw_plat$p.value, digits = 4),
                 ", r = ", round(eff_plat$effsize, 3), "\n"))
    } else {
      cat(paste0("    ", plat, ": Insufficient group sizes (Prof=",
                 n_prof, ", Non-prof=", n_nonprof, "). Skipped.\n"))
    }
  }

  # ---- Save Table 7 ----
  table7 <- prof_desc
  table7$Test <- c("Mann-Whitney U", "")
  table7$W <- c(mw_test$statistic, NA)
  table7$p_value <- c(round(mw_test$p.value, 4), NA)
  table7$r_effect_size <- c(round(r_effect, 3), NA)
  table7$Effect_magnitude <- c(as.character(r_magnitude), NA)

  write.csv(table7, file.path(tables_dir, "table7_creator_type.csv"),
            row.names = FALSE)

  if (nrow(platform_mw_results) > 0) {
    write.csv(platform_mw_results,
              file.path(tables_dir, "table7b_creator_by_platform.csv"),
              row.names = FALSE)
  }

  write.csv(prof_by_platform,
            file.path(tables_dir, "table7c_prof_descriptive_by_platform.csv"),
            row.names = FALSE)

  # ---- Report text ----
  report_lines <<- c(report_lines,
    "----------------------------------------------------------------",
    "SECTION 5: CREATOR TYPE ANALYSIS",
    "----------------------------------------------------------------",
    "",
    paste0("Professional creators (n = ", n1,
           "): Median DISCERN = ", prof_desc$Median[1],
           " (IQR = ", prof_desc$IQR[1], ")"),
    paste0("Non-professional creators (n = ", n2,
           "): Median DISCERN = ", prof_desc$Median[2],
           " (IQR = ", prof_desc$IQR[2], ")"),
    "",
    paste0("Mann-Whitney U test: W = ", mw_test$statistic,
           ", p = ", format(mw_test$p.value, digits = 4),
           ", rank-biserial r = ", round(r_effect, 3),
           " (", r_magnitude, " effect)."),
    "",
    ifelse(mw_test$p.value < 0.05,
           "Professional creators produced significantly higher quality content.",
           "No significant difference in quality by creator professional status."),
    ""
  )

  cat("  Section 5 completed successfully.\n")
  TRUE
}, error = function(e) {
  cat(paste0("  ERROR in Section 5: ", e$message, "\n"))
  FALSE
})


# =============================================================================
# SECTION 6: ENGAGEMENT-QUALITY CORRELATION (Table 8)
# =============================================================================

cat("\n--- SECTION 6: Engagement-Quality Correlation ---\n")

section_status[["6_Engagement_Correlation"]] <- tryCatch({

  engagement_cols <- c("Views", "Likes", "Shares", "Comments")
  engagement_present <- engagement_cols[engagement_cols %in% names(df)]

  if (length(engagement_present) == 0) {
    cat("  No engagement columns found. Skipping.\n")
    report_lines <<- c(report_lines,
      "----------------------------------------------------------------",
      "SECTION 6: ENGAGEMENT-QUALITY CORRELATION",
      "----------------------------------------------------------------",
      "",
      "No engagement metric columns found in dataset. Section skipped.",
      ""
    )
    TRUE
  } else {

    # ---- 6a. Overall Spearman correlations ----

    cat("  6a. Spearman correlations (overall)...\n")

    corr_overall <- data.frame(
      Metric = character(),
      rho = numeric(),
      p_value = numeric(),
      N = integer(),
      stringsAsFactors = FALSE
    )

    for (metric in engagement_present) {
      # Remove NAs for this pair
      valid <- complete.cases(df[, c("DISCERN_Total", metric)])
      n_valid <- sum(valid)

      if (n_valid >= 5) {
        cor_test <- cor.test(df$DISCERN_Total[valid], df[[metric]][valid],
                             method = "spearman", exact = FALSE)
        corr_overall <- rbind(corr_overall, data.frame(
          Metric = metric,
          rho = round(cor_test$estimate, 3),
          p_value = round(cor_test$p.value, 4),
          N = n_valid,
          stringsAsFactors = FALSE
        ))
        cat(paste0("    DISCERN_Total vs ", metric,
                   ": rho = ", round(cor_test$estimate, 3),
                   ", p = ", format(cor_test$p.value, digits = 4),
                   " (n = ", n_valid, ")\n"))
      }
    }

    # ---- 6b. Spearman correlations by platform ----

    cat("\n  6b. Spearman correlations by platform...\n")

    corr_by_platform <- data.frame()

    for (plat in levels(df$Platform)) {
      plat_data <- df %>% filter(Platform == plat)
      for (metric in engagement_present) {
        valid <- complete.cases(plat_data[, c("DISCERN_Total", metric)])
        n_valid <- sum(valid)

        if (n_valid >= 5) {
          cor_test <- cor.test(
            plat_data$DISCERN_Total[valid],
            plat_data[[metric]][valid],
            method = "spearman", exact = FALSE
          )
          corr_by_platform <- rbind(corr_by_platform, data.frame(
            Platform = plat,
            Metric = metric,
            rho = round(cor_test$estimate, 3),
            p_value = round(cor_test$p.value, 4),
            N = n_valid,
            stringsAsFactors = FALSE
          ))
        }
      }
    }

    if (nrow(corr_by_platform) > 0) {
      cat("  Correlations by platform:\n")
      print(corr_by_platform)
    }

    # ---- Save Table 8 ----
    write.csv(corr_overall,
              file.path(tables_dir, "table8a_correlations_overall.csv"),
              row.names = FALSE)

    if (nrow(corr_by_platform) > 0) {
      write.csv(corr_by_platform,
                file.path(tables_dir, "table8b_correlations_by_platform.csv"),
                row.names = FALSE)

      # Pivot to correlation matrix format
      corr_matrix <- corr_by_platform %>%
        select(Platform, Metric, rho) %>%
        pivot_wider(names_from = Metric, values_from = rho)
      write.csv(corr_matrix,
                file.path(tables_dir, "table8c_correlation_matrix.csv"),
                row.names = FALSE)
    }

    # ---- Report text ----
    report_lines <<- c(report_lines,
      "----------------------------------------------------------------",
      "SECTION 6: ENGAGEMENT-QUALITY CORRELATION",
      "----------------------------------------------------------------",
      "",
      "Spearman rank-order correlations between DISCERN Total and engagement metrics:",
      ""
    )

    for (i in seq_len(nrow(corr_overall))) {
      sig_marker <- ifelse(corr_overall$p_value[i] < 0.05, " *", "")
      report_lines <<- c(report_lines,
        paste0("  DISCERN vs ", corr_overall$Metric[i],
               ": rho = ", corr_overall$rho[i],
               ", p = ", corr_overall$p_value[i],
               " (n = ", corr_overall$N[i], ")", sig_marker)
      )
    }
    report_lines <<- c(report_lines, "")

    cat("  Section 6 completed successfully.\n")
    TRUE
  }
}, error = function(e) {
  cat(paste0("  ERROR in Section 6: ", e$message, "\n"))
  FALSE
})


# =============================================================================
# SECTION 7: INDIVIDUAL DISCERN QUESTION ANALYSIS
# =============================================================================

cat("\n--- SECTION 7: Individual DISCERN Question Analysis ---\n")

section_status[["7_DISCERN_Questions"]] <- tryCatch({

  discern_q_cols <- paste0("DISCERN_Q", 1:16)
  discern_q_present <- discern_q_cols[discern_q_cols %in% names(df)]

  if (length(discern_q_present) == 0) {
    cat("  No individual DISCERN question columns found. Skipping.\n")
    TRUE
  } else {

    # ---- 7a. Median score per question per platform ----

    item_stats <- df %>%
      group_by(Platform) %>%
      summarise(
        across(all_of(discern_q_present),
               list(
                 Median = ~median(.x, na.rm = TRUE),
                 Mean   = ~round(mean(.x, na.rm = TRUE), 2)
               ),
               .names = "{.col}_{.fn}"),
        .groups = "drop"
      )

    # Also compute overall
    item_stats_overall <- df %>%
      summarise(
        Platform = "Overall",
        across(all_of(discern_q_present),
               list(
                 Median = ~median(.x, na.rm = TRUE),
                 Mean   = ~round(mean(.x, na.rm = TRUE), 2)
               ),
               .names = "{.col}_{.fn}")
      )

    item_stats_full <- bind_rows(item_stats, item_stats_overall)

    # Extract just medians for heatmap
    median_cols <- paste0(discern_q_present, "_Median")
    heatmap_data <- item_stats[, c("Platform", median_cols)]
    names(heatmap_data) <- c("Platform", paste0("Q", 1:length(discern_q_present)))

    cat("  Median DISCERN question scores by platform:\n")
    print(as.data.frame(heatmap_data))

    # ---- 7b. Identify lowest scoring questions ----

    # Overall lowest
    overall_medians <- sapply(discern_q_present, function(q) {
      median(df[[q]], na.rm = TRUE)
    })
    names(overall_medians) <- paste0("Q", 1:length(discern_q_present))

    cat("\n  Overall median scores per question:\n")
    print(sort(overall_medians))

    lowest_q <- names(sort(overall_medians))[1:3]
    cat(paste0("\n  Three lowest-scoring questions overall: ",
               paste(lowest_q, collapse = ", "), "\n"))

    # Per platform lowest
    cat("\n  Lowest-scoring question per platform:\n")
    for (plat in levels(df$Platform)) {
      plat_data <- df %>% filter(Platform == plat)
      plat_medians <- sapply(discern_q_present, function(q) {
        median(plat_data[[q]], na.rm = TRUE)
      })
      names(plat_medians) <- paste0("Q", 1:length(discern_q_present))
      lowest <- names(sort(plat_medians))[1]
      cat(paste0("    ", plat, ": ", lowest,
                 " (Median = ", sort(plat_medians)[1], ")\n"))
    }

    # ---- Save ----
    write.csv(item_stats_full,
              file.path(tables_dir, "table_discern_questions_detail.csv"),
              row.names = FALSE)
    write.csv(heatmap_data,
              file.path(tables_dir, "table_discern_question_medians.csv"),
              row.names = FALSE)

    # ---- Report text ----
    report_lines <<- c(report_lines,
      "----------------------------------------------------------------",
      "SECTION 7: INDIVIDUAL DISCERN QUESTION ANALYSIS",
      "----------------------------------------------------------------",
      "",
      paste0("The three lowest-scoring DISCERN questions overall were: ",
             paste(lowest_q, "=", overall_medians[lowest_q], collapse = ", "),
             "."),
      ""
    )

    cat("  Section 7 completed successfully.\n")
    TRUE
  }
}, error = function(e) {
  cat(paste0("  ERROR in Section 7: ", e$message, "\n"))
  FALSE
})


# =============================================================================
# FIGURES
# =============================================================================

cat("\n--- GENERATING FIGURES ---\n")

# ---------- FIGURE 1: Box plot of DISCERN_Total by Platform -------------------

section_status[["Fig1_DISCERN_Boxplot"]] <- tryCatch({
  cat("  Figure 1: DISCERN Total box plot by platform...\n")

  # Compute medians for labels
  medians_fig1 <- df %>%
    group_by(Platform) %>%
    summarise(Median = median(DISCERN_Total, na.rm = TRUE), .groups = "drop")

  # Build the plot
  fig1 <- ggplot(df, aes(x = Platform, y = DISCERN_Total, fill = Platform)) +
    geom_boxplot(alpha = 0.7, outlier.shape = NA, width = 0.6) +
    geom_jitter(width = 0.15, alpha = 0.35, size = 1.2, color = "grey30") +
    geom_text(data = medians_fig1,
              aes(x = Platform, y = Median, label = Median),
              vjust = -0.8, fontface = "bold", size = 3.5, color = "black") +
    scale_fill_manual(values = platform_colors) +
    labs(
      title = "DISCERN Total Scores by Platform",
      x = "Platform",
      y = "DISCERN Total Score (16-80)"
    ) +
    guides(fill = "none") +
    coord_cartesian(ylim = c(10, 85))

  # Add significance brackets if Dunn's test was run
  # (stored in dunn_results from Section 3)
  if (exists("dunn_results") && !is.null(dunn_results)) {
    sig_pairs <- dunn_results %>%
      filter(P.adj < 0.05)

    if (nrow(sig_pairs) > 0) {
      # Add significance annotations using stat_pvalue_manual from rstatix
      # Build a data frame for annotations
      bracket_y <- max(df$DISCERN_Total, na.rm = TRUE) + 2
      y_step <- 4

      for (j in seq_len(nrow(sig_pairs))) {
        # Parse comparison (format: "Group1 - Group2")
        comp_parts <- trimws(strsplit(sig_pairs$Comparison[j], " - ")[[1]])
        p_label <- ifelse(sig_pairs$P.adj[j] < 0.001, "p < .001",
                   ifelse(sig_pairs$P.adj[j] < 0.01,
                          paste0("p = ", format(round(sig_pairs$P.adj[j], 3),
                                                nsmall = 3)),
                          paste0("p = ", format(round(sig_pairs$P.adj[j], 3),
                                                nsmall = 3))))

        fig1 <- fig1 +
          annotate("segment",
                   x = which(levels(df$Platform) == comp_parts[1]),
                   xend = which(levels(df$Platform) == comp_parts[2]),
                   y = bracket_y + (j - 1) * y_step,
                   yend = bracket_y + (j - 1) * y_step,
                   linewidth = 0.4) +
          annotate("text",
                   x = mean(c(which(levels(df$Platform) == comp_parts[1]),
                              which(levels(df$Platform) == comp_parts[2]))),
                   y = bracket_y + (j - 1) * y_step + 1.5,
                   label = p_label, size = 2.8)
      }

      # Expand y-axis to accommodate brackets
      max_bracket_y <- bracket_y + nrow(sig_pairs) * y_step + 3
      fig1 <- fig1 +
        coord_cartesian(ylim = c(10, max(85, max_bracket_y)))
    }
  }

  ggsave(file.path(figures_dir, "figure1_discern_boxplot.png"),
         plot = fig1, width = 8, height = 6, dpi = 300, bg = "white")

  cat("    Figure 1 saved.\n")
  TRUE
}, error = function(e) {
  cat(paste0("  ERROR in Figure 1: ", e$message, "\n"))
  FALSE
})


# ---------- FIGURE 2: Stacked bar chart of DISCERN_Category -------------------

section_status[["Fig2_DISCERN_Categories"]] <- tryCatch({
  cat("  Figure 2: DISCERN Category stacked bar chart...\n")

  # Compute percentages
  cat_pct <- df %>%
    count(Platform, DISCERN_Category) %>%
    group_by(Platform) %>%
    mutate(Percentage = n / sum(n) * 100) %>%
    ungroup()

  discern_cat_colors <- c(
    "Very Poor" = "#D73027",
    "Poor"      = "#FC8D59",
    "Fair"      = "#FEE08B",
    "Good"      = "#91CF60",
    "Excellent" = "#1A9850"
  )

  fig2 <- ggplot(cat_pct,
                 aes(x = Platform, y = Percentage,
                     fill = DISCERN_Category)) +
    geom_bar(stat = "identity", width = 0.7) +
    geom_text(aes(label = ifelse(Percentage >= 5,
                                 paste0(round(Percentage, 0), "%"), "")),
              position = position_stack(vjust = 0.5),
              size = 3, color = "black") +
    scale_fill_manual(values = discern_cat_colors,
                      name = "DISCERN\nCategory") +
    scale_y_continuous(labels = percent_format(scale = 1)) +
    labs(
      title = "Distribution of DISCERN Quality Categories by Platform",
      x = "Platform",
      y = "Percentage (%)"
    )

  ggsave(file.path(figures_dir, "figure2_discern_categories.png"),
         plot = fig2, width = 9, height = 6, dpi = 300, bg = "white")

  cat("    Figure 2 saved.\n")
  TRUE
}, error = function(e) {
  cat(paste0("  ERROR in Figure 2: ", e$message, "\n"))
  FALSE
})


# ---------- FIGURE 3: Grouped bar chart of JAMA compliance --------------------

section_status[["Fig3_JAMA_Compliance"]] <- tryCatch({
  cat("  Figure 3: JAMA compliance grouped bar chart...\n")

  jama_criteria_names <- c("JAMA_Authorship", "JAMA_Attribution",
                           "JAMA_Disclosure", "JAMA_Currency")
  jama_criteria_labels <- c("Authorship", "Attribution",
                            "Disclosure", "Currency")

  jama_pct_data <- data.frame()
  for (i in seq_along(jama_criteria_names)) {
    jcol <- jama_criteria_names[i]
    if (jcol %in% names(df)) {
      pct <- df %>%
        group_by(Platform) %>%
        summarise(
          Pct_Yes = mean(!!sym(jcol) == "Y", na.rm = TRUE) * 100,
          .groups = "drop"
        ) %>%
        mutate(Criterion = jama_criteria_labels[i])
      jama_pct_data <- rbind(jama_pct_data, pct)
    }
  }

  fig3 <- ggplot(jama_pct_data,
                 aes(x = Criterion, y = Pct_Yes, fill = Platform)) +
    geom_bar(stat = "identity", position = position_dodge(width = 0.8),
             width = 0.7) +
    geom_text(aes(label = paste0(round(Pct_Yes, 0), "%")),
              position = position_dodge(width = 0.8),
              vjust = -0.5, size = 2.8) +
    scale_fill_manual(values = platform_colors) +
    scale_y_continuous(limits = c(0, 110),
                       labels = percent_format(scale = 1)) +
    labs(
      title = "JAMA Benchmark Compliance by Platform",
      x = "JAMA Criterion",
      y = "Percentage Meeting Criterion (%)",
      fill = "Platform"
    )

  ggsave(file.path(figures_dir, "figure3_jama_compliance.png"),
         plot = fig3, width = 9, height = 6, dpi = 300, bg = "white")

  cat("    Figure 3 saved.\n")
  TRUE
}, error = function(e) {
  cat(paste0("  ERROR in Figure 3: ", e$message, "\n"))
  FALSE
})


# ---------- FIGURE 4: Box plot DISCERN by Creator Type ------------------------

section_status[["Fig4_Creator_Type"]] <- tryCatch({
  cat("  Figure 4: DISCERN by Creator Type box plot...\n")

  prof_medians <- df %>%
    group_by(Professional) %>%
    summarise(Median = median(DISCERN_Total, na.rm = TRUE), .groups = "drop")

  fig4 <- ggplot(df, aes(x = Professional, y = DISCERN_Total,
                          fill = Professional)) +
    geom_boxplot(alpha = 0.7, outlier.shape = NA, width = 0.5) +
    geom_jitter(width = 0.12, alpha = 0.35, size = 1.2, color = "grey30") +
    geom_text(data = prof_medians,
              aes(x = Professional, y = Median,
                  label = paste0("Mdn = ", Median)),
              vjust = -1, fontface = "bold", size = 3.5) +
    scale_fill_manual(values = c("Professional" = "#2166AC",
                                 "Non-professional" = "#B2182B")) +
    labs(
      title = "DISCERN Total Scores by Creator Professional Status",
      x = "Creator Type",
      y = "DISCERN Total Score (16-80)"
    ) +
    guides(fill = "none")

  # Add significance annotation if Mann-Whitney was significant
  if (exists("mw_test") && mw_test$p.value < 0.05) {
    p_label <- ifelse(mw_test$p.value < 0.001, "p < .001",
               paste0("p = ", format(round(mw_test$p.value, 3), nsmall = 3)))

    fig4 <- fig4 +
      annotate("segment", x = 1, xend = 2,
               y = max(df$DISCERN_Total, na.rm = TRUE) + 3,
               yend = max(df$DISCERN_Total, na.rm = TRUE) + 3,
               linewidth = 0.4) +
      annotate("text", x = 1.5,
               y = max(df$DISCERN_Total, na.rm = TRUE) + 5,
               label = p_label, size = 3.2)
  }

  ggsave(file.path(figures_dir, "figure4_creator_type.png"),
         plot = fig4, width = 7, height = 6, dpi = 300, bg = "white")

  cat("    Figure 4 saved.\n")
  TRUE
}, error = function(e) {
  cat(paste0("  ERROR in Figure 4: ", e$message, "\n"))
  FALSE
})


# ---------- FIGURE 5: Scatter plots DISCERN vs log(Views+1) by Platform ------

section_status[["Fig5_Engagement_Scatter"]] <- tryCatch({
  cat("  Figure 5: Engagement scatter plots...\n")

  if ("Views" %in% names(df)) {
    df$log_Views <- log(df$Views + 1)

    fig5 <- ggplot(df, aes(x = log_Views, y = DISCERN_Total)) +
      geom_point(aes(color = Platform), alpha = 0.6, size = 1.8) +
      geom_smooth(method = "lm", se = TRUE, color = "grey30",
                  linewidth = 0.7, alpha = 0.15) +
      facet_wrap(~Platform, scales = "free_x") +
      scale_color_manual(values = platform_colors) +
      labs(
        title = "DISCERN Total Score vs. Engagement (Views) by Platform",
        x = "log(Views + 1)",
        y = "DISCERN Total Score"
      ) +
      guides(color = "none")

    ggsave(file.path(figures_dir, "figure5_engagement_scatter.png"),
           plot = fig5, width = 10, height = 7, dpi = 300, bg = "white")

    cat("    Figure 5 saved.\n")
  } else {
    cat("    Views column not found. Figure 5 skipped.\n")
  }

  TRUE
}, error = function(e) {
  cat(paste0("  ERROR in Figure 5: ", e$message, "\n"))
  FALSE
})


# ---------- FIGURE 6: Heatmap of median DISCERN Q1-Q16 by Platform ------------

section_status[["Fig6_Heatmap"]] <- tryCatch({
  cat("  Figure 6: DISCERN question heatmap...\n")

  discern_q_cols <- paste0("DISCERN_Q", 1:16)
  discern_q_present <- discern_q_cols[discern_q_cols %in% names(df)]

  if (length(discern_q_present) > 0) {
    # Build heatmap data (long format)
    heatmap_long <- df %>%
      select(Platform, all_of(discern_q_present)) %>%
      group_by(Platform) %>%
      summarise(
        across(everything(), ~median(.x, na.rm = TRUE)),
        .groups = "drop"
      ) %>%
      pivot_longer(cols = -Platform,
                   names_to = "Question",
                   values_to = "Median_Score") %>%
      mutate(
        Question = factor(
          gsub("DISCERN_Q", "Q", Question),
          levels = paste0("Q", 1:16)
        )
      )

    # DISCERN question labels for context
    q_labels <- c(
      "Q1"  = "Q1: Explicit aims",
      "Q2"  = "Q2: Aims achieved",
      "Q3"  = "Q3: Relevance",
      "Q4"  = "Q4: Sources clear",
      "Q5"  = "Q5: Information current",
      "Q6"  = "Q6: Balanced/unbiased",
      "Q7"  = "Q7: Additional sources",
      "Q8"  = "Q8: Areas of uncertainty",
      "Q9"  = "Q9: How treatment works",
      "Q10" = "Q10: Benefits of treatment",
      "Q11" = "Q11: Risks of treatment",
      "Q12" = "Q12: No treatment effects",
      "Q13" = "Q13: Quality of life",
      "Q14" = "Q14: Alternatives clear",
      "Q15" = "Q15: Shared decision-making",
      "Q16" = "Q16: Overall quality"
    )

    fig6 <- ggplot(heatmap_long,
                   aes(x = Platform, y = Question, fill = Median_Score)) +
      geom_tile(color = "white", linewidth = 0.5) +
      geom_text(aes(label = Median_Score), size = 3.2, color = "black") +
      scale_fill_gradient2(
        low = "#D73027", mid = "#FEE08B", high = "#1A9850",
        midpoint = 3, limits = c(1, 5),
        name = "Median\nScore"
      ) +
      scale_y_discrete(limits = rev(paste0("Q", 1:length(discern_q_present))),
                       labels = rev(q_labels[paste0("Q", 1:length(discern_q_present))])) +
      labs(
        title = "Median DISCERN Question Scores by Platform",
        x = "Platform",
        y = ""
      ) +
      theme(
        axis.text.y = element_text(size = 9, hjust = 1),
        panel.grid = element_blank()
      )

    ggsave(file.path(figures_dir, "figure6_discern_heatmap.png"),
           plot = fig6, width = 9, height = 8, dpi = 300, bg = "white")

    cat("    Figure 6 saved.\n")
  } else {
    cat("    Individual question columns not found. Figure 6 skipped.\n")
  }

  TRUE
}, error = function(e) {
  cat(paste0("  ERROR in Figure 6: ", e$message, "\n"))
  FALSE
})


# ---------- FIGURE 7: Sample composition bar chart ----------------------------

section_status[["Fig7_Sample_Composition"]] <- tryCatch({
  cat("  Figure 7: Sample composition bar chart...\n")

  # Panel A: Items per platform
  sample_counts <- df %>%
    count(Platform) %>%
    mutate(label = paste0("n = ", n))

  fig7a <- ggplot(sample_counts,
                  aes(x = Platform, y = n, fill = Platform)) +
    geom_bar(stat = "identity", width = 0.6) +
    geom_text(aes(label = label), vjust = -0.5, size = 3.5,
              fontface = "bold") +
    scale_fill_manual(values = platform_colors) +
    scale_y_continuous(limits = c(0, max(sample_counts$n) * 1.15)) +
    labs(
      title = "Sample Composition: Items per Platform",
      x = "Platform",
      y = "Number of Items"
    ) +
    guides(fill = "none")

  # Panel B: Creator type distribution
  creator_counts <- df %>%
    count(Platform, Creator_Type)

  fig7b <- ggplot(creator_counts,
                  aes(x = Platform, y = n, fill = Creator_Type)) +
    geom_bar(stat = "identity", position = "stack", width = 0.7) +
    scale_fill_brewer(palette = "Set2", name = "Creator Type") +
    labs(
      title = "Creator Type Distribution by Platform",
      x = "Platform",
      y = "Number of Items"
    )

  # Save both panels
  ggsave(file.path(figures_dir, "figure7a_sample_counts.png"),
         plot = fig7a, width = 7, height = 5, dpi = 300, bg = "white")
  ggsave(file.path(figures_dir, "figure7b_creator_distribution.png"),
         plot = fig7b, width = 9, height = 6, dpi = 300, bg = "white")

  # Combined figure using patchwork-style approach (cowplot or grid)
  # Using a simple approach with gridExtra if available
  if (requireNamespace("gridExtra", quietly = TRUE)) {
    library(gridExtra)
    fig7_combined <- grid.arrange(fig7a, fig7b, ncol = 2)
    ggsave(file.path(figures_dir, "figure7_sample_composition.png"),
           plot = fig7_combined, width = 16, height = 6, dpi = 300,
           bg = "white")
  }

  cat("    Figure 7 saved.\n")
  TRUE
}, error = function(e) {
  cat(paste0("  ERROR in Figure 7: ", e$message, "\n"))
  FALSE
})


# =============================================================================
# SAVE SUMMARY REPORT
# =============================================================================

cat("\n--- Saving Analysis Report ---\n")

section_status[["Report_Export"]] <- tryCatch({

  # Finalize report text
  report_lines <- c(report_lines,
    "",
    "================================================================",
    "END OF ANALYSIS REPORT",
    paste0("Generated: ", Sys.time()),
    "================================================================"
  )

  report_path <- file.path(output_dir, "analysis_report.txt")
  writeLines(report_lines, report_path)
  cat(paste0("  Report saved to: ", report_path, "\n"))

  TRUE
}, error = function(e) {
  cat(paste0("  ERROR saving report: ", e$message, "\n"))
  FALSE
})


# =============================================================================
# FINAL SUMMARY
# =============================================================================

cat("\n")
cat("================================================================\n")
cat("  ANALYSIS COMPLETE — SECTION SUMMARY\n")
cat("================================================================\n\n")

for (section_name in names(section_status)) {
  status <- ifelse(section_status[[section_name]], "COMPLETED", "FAILED")
  symbol <- ifelse(section_status[[section_name]], "[OK]", "[FAIL]")
  cat(paste0("  ", symbol, " ", gsub("_", " ", section_name), "\n"))
}

n_completed <- sum(unlist(section_status))
n_total <- length(section_status)
cat(paste0("\n  ", n_completed, " / ", n_total, " sections completed.\n"))

if (all(unlist(section_status))) {
  cat("\n  All sections completed successfully.\n")
} else {
  failed <- names(section_status)[!unlist(section_status)]
  cat(paste0("\n  Failed sections: ",
             paste(gsub("_", " ", failed), collapse = ", "), "\n"))
  cat("  Review the error messages above for details.\n")
}

cat("\nOutput locations:\n")
cat(paste0("  Tables:  ", tables_dir, "\n"))
cat(paste0("  Figures: ", figures_dir, "\n"))
cat(paste0("  Report:  ", file.path(output_dir, "analysis_report.txt"), "\n"))
cat("\n================================================================\n")
cat("  DONE\n")
cat("================================================================\n")
