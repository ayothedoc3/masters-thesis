"""
Master's Thesis Statistical Analysis — Python Implementation
=============================================================
Replaces R script (R not installed). Produces the thesis statistical tests:
  - Kruskal-Wallis H test (DISCERN across platforms)
  - Pairwise Mann-Whitney U tests with Bonferroni correction
  - Chi-square / Fisher's exact (JAMA by platform)
  - Mann-Whitney U (DISCERN by creator type)
  - Spearman's rho (engagement vs quality)
  - ICC + Cohen's kappa (inter-rater reliability)

Output: analysis/output/tables/*.csv, analysis/output/figures/*.png,
        analysis/output/analysis_report.txt
"""

import os
import re
import csv
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import kruskal, mannwhitneyu, spearmanr, chi2_contingency, fisher_exact
import pingouin as pg
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ============================================================================
# PATHS
# ============================================================================
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE), "data", "csv")
OUTPUT_DIR = os.path.join(BASE, "output")
TABLES_DIR = os.path.join(OUTPUT_DIR, "tables")
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")
REPORT_PATH = os.path.join(OUTPUT_DIR, "analysis_report.txt")

os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================
print("=" * 70)
print("  THESIS ANALYSIS — Python")
print("=" * 70)

df = pd.read_csv(os.path.join(DATA_DIR, "master_dataset_corrected.csv"))
print(f"\nLoaded {len(df)} rows, {len(df.columns)} columns")

# Ensure numeric columns
for q in range(1, 17):
    df[f"DISCERN_Q{q}"] = pd.to_numeric(df[f"DISCERN_Q{q}"], errors="coerce")

df["DISCERN_Total"] = pd.to_numeric(df["DISCERN_Total"], errors="coerce")
df["DISCERN_Section1"] = pd.to_numeric(df["DISCERN_Section1"], errors="coerce")
df["DISCERN_Section2"] = pd.to_numeric(df["DISCERN_Section2"], errors="coerce")
df["JAMA_Total"] = pd.to_numeric(df["JAMA_Total"], errors="coerce")
CONTENT_FORMAT_ALIASES = {
    "text article": "Text article",
    "long video (>5min)": "Long video (>5min)",
    "long video (>5 min)": "Long video (>5min)",
    "long-form video (>5min)": "Long video (>5min)",
    "long-form video (>5 min)": "Long video (>5min)",
    "short video (<60s)": "Short video (<60s)",
    "short video (<60 s)": "Short video (<60s)",
    "short-form video (<60s)": "Short video (<60s)",
    "short-form video (<60 s)": "Short video (<60s)",
    "image+caption": "Image+caption",
    "image + caption": "Image+caption",
    "image with caption": "Image+caption",
    "image-with-caption": "Image+caption",
    "carousel": "Carousel",
}


def normalize_content_format(value):
    if pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    if not text:
        return None
    return CONTENT_FORMAT_ALIASES.get(text.lower())
# Clean Content_Format — fix any non-standard values
df["Content_Format"] = df["Content_Format"].apply(normalize_content_format)

# Clean Creator_Type
valid_ctypes = ["Healthcare professional", "Certified fitness professional",
                "Fitness influencer", "General user", "Organization"]
df["Creator_Type"] = df["Creator_Type"].apply(lambda x: x if x in valid_ctypes else None)

df["Views"] = pd.to_numeric(df["Views"], errors="coerce")
df["Likes"] = pd.to_numeric(df["Likes"], errors="coerce")
df["Comments"] = pd.to_numeric(df["Comments"], errors="coerce")

# Binary JAMA columns
for col in ["JAMA_Authorship", "JAMA_Attribution", "JAMA_Disclosure", "JAMA_Currency"]:
    df[f"{col}_binary"] = (df[col] == "Y").astype(int)

# Platform order
platform_order = ["Website", "YouTube", "TikTok", "Instagram"]
df["Platform"] = pd.Categorical(df["Platform"], categories=platform_order, ordered=True)

# Creator type: professional vs non-professional
df["Creator_Professional"] = df["Creator_Type"].isin(
    ["Healthcare professional", "Certified fitness professional"]
).map({True: "Professional", False: "Non-professional"})

report_lines = []
def report(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode())
    report_lines.append(text)


def cramers_v(ct, chi2_stat):
    n = ct.to_numpy().sum()
    min_dim = min(ct.shape) - 1
    if n == 0 or min_dim <= 0:
        return np.nan
    return np.sqrt((chi2_stat / n) / min_dim)

report("\n" + "=" * 70)
report("SECTION 1: SAMPLE CHARACTERISTICS")
report("=" * 70)

# ============================================================================
# SECTION 1: DESCRIPTIVE STATISTICS
# ============================================================================

# 1a. Platform counts
report("\n1a. Sample by Platform:")
for p in platform_order:
    n = len(df[df["Platform"] == p])
    report(f"  {p}: n = {n}")
report(f"  Total: N = {len(df)}")

# 1b. Creator type by platform
report("\n1b. Creator Type by Platform:")
ct_cross = pd.crosstab(df["Platform"], df["Creator_Type"])
ct_cross.to_csv(os.path.join(TABLES_DIR, "creator_type_by_platform.csv"))
report(ct_cross.to_string())

# 1c. Content format by platform
report("\n1c. Content Format by Platform:")
cf_cross = pd.crosstab(df["Platform"], df["Content_Format"])
cf_cross.to_csv(os.path.join(TABLES_DIR, "content_format_by_platform.csv"))
report(cf_cross.to_string())

# 1d. DISCERN descriptive stats by platform
report("\n1d. DISCERN Total — Descriptive Statistics by Platform:")
desc = df.groupby("Platform")["DISCERN_Total"].agg(
    N="count", Mean="mean", SD="std", Median="median",
    Q1=lambda x: x.quantile(0.25), Q3=lambda x: x.quantile(0.75),
    Min="min", Max="max"
).round(2)
desc["IQR"] = (desc["Q3"] - desc["Q1"]).round(2)
desc.to_csv(os.path.join(TABLES_DIR, "discern_descriptive_by_platform.csv"))
report(desc.to_string())

# Overall
overall = df["DISCERN_Total"].describe().round(2)
report(f"\n  Overall: Mean={overall['mean']}, SD={overall['std']}, Median={overall['50%']}, "
       f"Min={overall['min']}, Max={overall['max']}")

# 1e. DISCERN category distribution
report("\n1e. DISCERN Category Distribution by Platform:")
cat_order = ["Very Poor", "Poor", "Fair", "Good", "Excellent"]
cat_cross = pd.crosstab(df["Platform"], df["DISCERN_Category"])
# Reorder columns
for c in cat_order:
    if c not in cat_cross.columns:
        cat_cross[c] = 0
cat_cross = cat_cross[cat_order]
cat_cross.to_csv(os.path.join(TABLES_DIR, "discern_category_by_platform.csv"))
report(cat_cross.to_string())

# Percentages
cat_pct = cat_cross.div(cat_cross.sum(axis=1), axis=0).multiply(100).round(1)
report("\n  Percentages:")
report(cat_pct.to_string())

# 1f. JAMA descriptive by platform
report("\n1f. JAMA Total — Descriptive Statistics by Platform:")
jama_desc = df.groupby("Platform")["JAMA_Total"].agg(
    N="count", Mean="mean", SD="std", Median="median"
).round(2)
jama_desc.to_csv(os.path.join(TABLES_DIR, "jama_descriptive_by_platform.csv"))
report(jama_desc.to_string())

# JAMA criteria compliance rates
report("\n  JAMA Criteria Compliance (% Y) by Platform:")
jama_compliance = pd.DataFrame()
for col in ["JAMA_Authorship", "JAMA_Attribution", "JAMA_Disclosure", "JAMA_Currency"]:
    rates = df.groupby("Platform")[f"{col}_binary"].mean().multiply(100).round(1)
    jama_compliance[col.replace("JAMA_", "")] = rates
jama_compliance.to_csv(os.path.join(TABLES_DIR, "jama_compliance_by_platform.csv"))
report(jama_compliance.to_string())

# ============================================================================
# SECTION 2: INTER-RATER RELIABILITY
# ============================================================================

report("\n" + "=" * 70)
report("SECTION 2: INTER-RATER RELIABILITY")
report("=" * 70)

rater2_path = os.path.join(DATA_DIR, "second_rater_scores.csv")
if os.path.exists(rater2_path):
    df2 = pd.read_csv(rater2_path)
    df2["DISCERN_Total"] = pd.to_numeric(df2["DISCERN_Total"], errors="coerce")
    df2["JAMA_Total"] = pd.to_numeric(df2["JAMA_Total"], errors="coerce")

    # Merge on Item_ID
    merged = df[["Item_ID", "DISCERN_Total", "DISCERN_Section1", "DISCERN_Section2"]].merge(
        df2[["Item_ID", "DISCERN_Total", "DISCERN_Section1", "DISCERN_Section2"]],
        on="Item_ID", suffixes=("_r1", "_r2")
    )

    if len(merged) > 0:
        # ICC for DISCERN Total
        icc_data = merged[["DISCERN_Total_r1", "DISCERN_Total_r2"]].dropna()
        icc_result = pg.intraclass_corr(
            data=pd.DataFrame({
                "targets": list(range(len(icc_data))) * 2,
                "raters": ["R1"] * len(icc_data) + ["R2"] * len(icc_data),
                "ratings": list(icc_data["DISCERN_Total_r1"]) + list(icc_data["DISCERN_Total_r2"])
            }),
            targets="targets", raters="raters", ratings="ratings"
        )
        # Use ICC3 (two-way mixed, single measures, consistency)
        icc3 = icc_result[icc_result["Type"] == "ICC3"]
        icc_val = icc3["ICC"].values[0]
        icc_ci = (icc3["CI95"].values[0][0], icc3["CI95"].values[0][1])

        report(f"\n  ICC for DISCERN Total (ICC3, consistency):")
        report(f"    ICC = {icc_val:.3f}")
        report(f"    95% CI = [{icc_ci[0]:.3f}, {icc_ci[1]:.3f}]")

        if icc_val >= 0.75:
            report("    Interpretation: EXCELLENT agreement (>= 0.75)")
        elif icc_val >= 0.60:
            report("    Interpretation: GOOD agreement (0.60-0.74)")
        elif icc_val >= 0.40:
            report("    Interpretation: FAIR agreement (0.40-0.59)")
        else:
            report("    Interpretation: POOR agreement (< 0.40)")

        # Cohen's kappa for JAMA criteria
        report("\n  Cohen's Kappa for JAMA criteria:")
        for col in ["JAMA_Authorship", "JAMA_Attribution", "JAMA_Disclosure", "JAMA_Currency"]:
            j1 = df.loc[df["Item_ID"].isin(merged["Item_ID"]), col].values
            j2 = df2.loc[df2["Item_ID"].isin(merged["Item_ID"]), col].values
            if len(j1) == len(j2) and len(j1) > 0:
                # Convert to numeric for kappa
                j1_num = [1 if x == "Y" else 0 for x in j1]
                j2_num = [1 if x == "Y" else 0 for x in j2]
                # Check if there's variation
                if len(set(j1_num)) > 1 or len(set(j2_num)) > 1:
                    kappa = pg.compute_effsize(pd.Series(j1_num), pd.Series(j2_num), eftype="cohen")
                    # Use sklearn-style kappa instead
                    # Cohen's kappa manually
                    po = sum(1 for a, b in zip(j1_num, j2_num) if a == b) / len(j1_num)
                    p1 = sum(j1_num) / len(j1_num)
                    p2 = sum(j2_num) / len(j2_num)
                    pe = p1 * p2 + (1 - p1) * (1 - p2)
                    k = (po - pe) / (1 - pe) if pe < 1 else 1.0
                    report(f"    {col.replace('JAMA_', '')}: kappa = {k:.3f}")
                else:
                    # Perfect agreement or no variation
                    agreement = sum(1 for a, b in zip(j1_num, j2_num) if a == b) / len(j1_num)
                    report(f"    {col.replace('JAMA_', '')}: Perfect agreement ({agreement*100:.0f}%), kappa undefined (no variation)")

        # Save IRR results
        irr_df = pd.DataFrame({
            "Measure": ["DISCERN_Total_ICC3"],
            "Value": [round(icc_val, 3)],
            "CI_Lower": [round(icc_ci[0], 3)],
            "CI_Upper": [round(icc_ci[1], 3)]
        })
        irr_df.to_csv(os.path.join(TABLES_DIR, "irr_results.csv"), index=False)
    else:
        report("  WARNING: No matching items between rater 1 and rater 2.")
else:
    report("  Second rater file not found. Skipping IRR analysis.")


# ============================================================================
# SECTION 3: RQ1 — DISCERN ACROSS PLATFORMS
# ============================================================================

report("\n" + "=" * 70)
report("SECTION 3: RQ1 — DISCERN SCORES ACROSS PLATFORMS")
report("=" * 70)

# 3a. Kruskal-Wallis H test
groups = [df[df["Platform"] == p]["DISCERN_Total"].dropna().values for p in platform_order]
h_stat, h_p = kruskal(*groups)
# Effect size: eta-squared = (H - k + 1) / (N - k)
k = len(platform_order)
N = len(df)
eta_sq = (h_stat - k + 1) / (N - k)

report(f"\n3a. Kruskal-Wallis H Test:")
report(f"  H({k-1}) = {h_stat:.3f}, p = {h_p:.6f}")
report(f"  Eta-squared = {eta_sq:.4f}")
if h_p < 0.001:
    report("  Result: HIGHLY SIGNIFICANT (p < 0.001)")
elif h_p < 0.05:
    report(f"  Result: SIGNIFICANT (p = {h_p:.4f})")
else:
    report(f"  Result: NOT significant (p = {h_p:.4f})")

# 3b. Pairwise Mann-Whitney U tests with Bonferroni correction
report(f"\n3b. Pairwise Mann-Whitney U Tests (Bonferroni corrected):")
pairs = []
for i in range(len(platform_order)):
    for j in range(i + 1, len(platform_order)):
        p1, p2 = platform_order[i], platform_order[j]
        g1 = df[df["Platform"] == p1]["DISCERN_Total"].dropna()
        g2 = df[df["Platform"] == p2]["DISCERN_Total"].dropna()
        u_stat, u_p = mannwhitneyu(g1, g2, alternative="two-sided")
        # Rank-biserial correlation as effect size
        r_rb = 1 - (2 * u_stat) / (len(g1) * len(g2))
        bonf_p = min(u_p * 6, 1.0)  # 6 comparisons
        sig = "***" if bonf_p < 0.001 else "**" if bonf_p < 0.01 else "*" if bonf_p < 0.05 else "ns"
        report(f"  {p1} vs {p2}: U={u_stat:.0f}, p_adj={bonf_p:.4f} {sig}, r={r_rb:.3f}")
        pairs.append({
            "Comparison": f"{p1} vs {p2}",
            "U": u_stat, "p_unadjusted": u_p,
            "p_bonferroni": bonf_p, "rank_biserial_r": round(r_rb, 3),
            "significant": sig
        })

pd.DataFrame(pairs).to_csv(os.path.join(TABLES_DIR, "pairwise_comparisons_discern.csv"), index=False)

# 3c. DISCERN Section 1 vs Section 2 by platform
report("\n3c. DISCERN Section Scores by Platform:")
for p in platform_order:
    sub = df[df["Platform"] == p]
    s1 = sub["DISCERN_Section1"].describe()
    s2 = sub["DISCERN_Section2"].describe()
    report(f"  {p}: Section1 Mdn={sub['DISCERN_Section1'].median():.0f} "
           f"(IQR {sub['DISCERN_Section1'].quantile(0.25):.0f}-{sub['DISCERN_Section1'].quantile(0.75):.0f}), "
           f"Section2 Mdn={sub['DISCERN_Section2'].median():.0f} "
           f"(IQR {sub['DISCERN_Section2'].quantile(0.25):.0f}-{sub['DISCERN_Section2'].quantile(0.75):.0f})")


# ============================================================================
# SECTION 4: RQ1 — JAMA ACROSS PLATFORMS
# ============================================================================

report("\n" + "=" * 70)
report("SECTION 4: RQ1 — JAMA COMPLIANCE ACROSS PLATFORMS")
report("=" * 70)

# 4a. Chi-square for each JAMA criterion
report("\n4a. Chi-Square Tests for JAMA Criteria by Platform:")
jama_chi_results = []
for col in ["JAMA_Authorship", "JAMA_Attribution", "JAMA_Disclosure", "JAMA_Currency"]:
    ct = pd.crosstab(df["Platform"], df[col])
    # Check if we have both Y and N
    if ct.shape[1] < 2:
        report(f"  {col}: Only one category present, chi-square not applicable")
        continue
    chi2, p_val, dof, expected = chi2_contingency(ct)
    v_stat = cramers_v(ct, chi2)
    # Check if Fisher's exact is needed (any expected < 5)
    min_expected = expected.min()
    jama_chi_results.append({
        "criterion": col.replace("JAMA_", ""),
        "chi2": round(chi2, 3),
        "df": int(dof),
        "p_value": round(p_val, 4),
        "cramers_v": round(v_stat, 3),
        "min_expected": round(float(min_expected), 3),
        "expected_count_warning": bool(min_expected < 5),
    })
    if min_expected < 5:
        report(f"  {col}: chi2={chi2:.3f}, df={dof}, p={p_val:.4f}"
               f", Cramer's V={v_stat:.3f} "
               f"(NOTE: min expected={min_expected:.1f} < 5, interpret with caution)")
    else:
        report(f"  {col}: chi2={chi2:.3f}, df={dof}, p={p_val:.4f}, Cramer's V={v_stat:.3f}")

pd.DataFrame(jama_chi_results).to_csv(
    os.path.join(TABLES_DIR, "jama_chi_square_results.csv"), index=False
)

# 4b. Chi-square for JAMA Total (categorized)
report("\n4b. JAMA Total Distribution by Platform:")
jama_dist = pd.crosstab(df["Platform"], df["JAMA_Total"])
jama_dist.to_csv(os.path.join(TABLES_DIR, "jama_total_distribution.csv"))
report(jama_dist.to_string())

# Kruskal-Wallis on JAMA Total
jama_groups = [df[df["Platform"] == p]["JAMA_Total"].dropna().values for p in platform_order]
h_jama, p_jama = kruskal(*jama_groups)
report(f"\n  Kruskal-Wallis on JAMA Total: H({k-1}) = {h_jama:.3f}, p = {p_jama:.6f}")


# ============================================================================
# SECTION 5: RQ2 — CREATOR TYPE MODERATING QUALITY
# ============================================================================

report("\n" + "=" * 70)
report("SECTION 5: RQ2 — CREATOR TYPE AND QUALITY SCORES")
report("=" * 70)

# 5a. Professional vs non-professional
report("\n5a. DISCERN by Creator Professional Status:")
prof = df[df["Creator_Professional"] == "Professional"]["DISCERN_Total"].dropna()
non_prof = df[df["Creator_Professional"] == "Non-professional"]["DISCERN_Total"].dropna()
report(f"  Professional: n={len(prof)}, Mdn={prof.median():.1f}, "
       f"IQR={prof.quantile(0.25):.1f}-{prof.quantile(0.75):.1f}")
report(f"  Non-professional: n={len(non_prof)}, Mdn={non_prof.median():.1f}, "
       f"IQR={non_prof.quantile(0.25):.1f}-{non_prof.quantile(0.75):.1f}")

u_stat, u_p = mannwhitneyu(prof, non_prof, alternative="two-sided")
r_rb = 1 - (2 * u_stat) / (len(prof) * len(non_prof))
report(f"  Mann-Whitney U = {u_stat:.0f}, p = {u_p:.6f}, r = {r_rb:.3f}")

# 5b. By individual creator type
report("\n5b. DISCERN by Individual Creator Type:")
creator_types = df["Creator_Type"].dropna().unique()
for ct in sorted(creator_types):
    sub = df[df["Creator_Type"] == ct]["DISCERN_Total"].dropna()
    report(f"  {ct}: n={len(sub)}, Mdn={sub.median():.1f}, "
           f"Mean={sub.mean():.1f}, SD={sub.std():.1f}")

# Kruskal-Wallis by creator type
ct_groups = [df[df["Creator_Type"] == ct]["DISCERN_Total"].dropna().values
             for ct in sorted(creator_types) if len(df[df["Creator_Type"] == ct]) > 0]
h_ct, p_ct = kruskal(*ct_groups)
report(f"\n  Kruskal-Wallis by Creator Type: H = {h_ct:.3f}, p = {p_ct:.6f}")

# 5c. JAMA by creator professional status
report("\n5c. JAMA Total by Creator Professional Status:")
prof_jama = df[df["Creator_Professional"] == "Professional"]["JAMA_Total"].dropna()
non_prof_jama = df[df["Creator_Professional"] == "Non-professional"]["JAMA_Total"].dropna()
report(f"  Professional: Mdn={prof_jama.median():.1f}, Mean={prof_jama.mean():.2f}")
report(f"  Non-professional: Mdn={non_prof_jama.median():.1f}, Mean={non_prof_jama.mean():.2f}")
u_j, p_j = mannwhitneyu(prof_jama, non_prof_jama, alternative="two-sided")
report(f"  Mann-Whitney U = {u_j:.0f}, p = {p_j:.6f}")


# ============================================================================
# SECTION 6: RQ3 — ENGAGEMENT VS QUALITY
# ============================================================================

report("\n" + "=" * 70)
report("SECTION 6: RQ3 — ENGAGEMENT METRICS VS QUALITY")
report("=" * 70)

# Only social media platforms have engagement data
sm = df[df["Platform"].isin(["YouTube", "TikTok", "Instagram"])].copy()

report(f"\n  Social media items with engagement data: {len(sm)}")

engagement_cols = ["Views", "Likes", "Comments"]
for eng_col in engagement_cols:
    valid = sm[[eng_col, "DISCERN_Total"]].dropna()
    if len(valid) > 5:
        rho, p_val = spearmanr(valid[eng_col], valid["DISCERN_Total"])
        report(f"\n  {eng_col} vs DISCERN Total:")
        report(f"    n = {len(valid)}, Spearman's rho = {rho:.3f}, p = {p_val:.4f}")
        if abs(rho) < 0.1:
            report("    Interpretation: Negligible correlation")
        elif abs(rho) < 0.3:
            report("    Interpretation: Weak correlation")
        elif abs(rho) < 0.5:
            report("    Interpretation: Moderate correlation")
        else:
            report("    Interpretation: Strong correlation")

# By platform
report("\n  Engagement-Quality correlations by platform:")
for p in ["YouTube", "TikTok", "Instagram"]:
    sub = sm[sm["Platform"] == p]
    for eng_col in engagement_cols:
        valid = sub[[eng_col, "DISCERN_Total"]].dropna()
        if len(valid) > 5:
            rho, p_val = spearmanr(valid[eng_col], valid["DISCERN_Total"])
            sig = "*" if p_val < 0.05 else ""
            report(f"    {p} — {eng_col}: rho={rho:.3f}, p={p_val:.4f} {sig}")

# Engagement vs JAMA
report("\n  Engagement vs JAMA Total:")
for eng_col in engagement_cols:
    valid = sm[[eng_col, "JAMA_Total"]].dropna()
    if len(valid) > 5:
        rho, p_val = spearmanr(valid[eng_col], valid["JAMA_Total"])
        report(f"    {eng_col}: rho={rho:.3f}, p={p_val:.4f}")


# ============================================================================
# SECTION 7: FIGURES
# ============================================================================

report("\n" + "=" * 70)
report("SECTION 7: GENERATING FIGURES")
report("=" * 70)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight"
})

colors = {"Website": "#4472C4", "YouTube": "#FF6B6B", "TikTok": "#54C45E", "Instagram": "#9B59B6"}

# Figure 1: DISCERN Total boxplot by platform
fig1, ax1 = plt.subplots(figsize=(8, 6))
data_box = [df[df["Platform"] == p]["DISCERN_Total"].dropna().values for p in platform_order]
bp = ax1.boxplot(data_box, labels=platform_order, patch_artist=True, widths=0.6,
                 medianprops=dict(color="black", linewidth=2))
for patch, p in zip(bp["boxes"], platform_order):
    patch.set_facecolor(colors[p])
    patch.set_alpha(0.7)
ax1.set_ylabel("DISCERN Total Score (16-80)")
ax1.set_title("DISCERN Total Scores by Platform")
ax1.axhline(y=26, color="red", linestyle="--", alpha=0.5, label="Very Poor/Poor cutoff")
ax1.axhline(y=38, color="orange", linestyle="--", alpha=0.5, label="Poor/Fair cutoff")
ax1.axhline(y=50, color="green", linestyle="--", alpha=0.5, label="Fair/Good cutoff")
ax1.legend(fontsize=8, loc="upper right")
ax1.set_ylim(10, 85)
fig1.savefig(os.path.join(FIGURES_DIR, "fig1_discern_boxplot.png"))
plt.close(fig1)
report("  Fig 1: DISCERN boxplot saved")

# Figure 2: DISCERN category stacked bar
fig2, ax2 = plt.subplots(figsize=(8, 6))
cat_colors = {"Very Poor": "#FF0000", "Poor": "#FF8C00", "Fair": "#FFD700",
              "Good": "#90EE90", "Excellent": "#228B22"}
cat_pct_plot = cat_pct.reindex(platform_order)
bottom = np.zeros(len(platform_order))
for cat in cat_order:
    vals = cat_pct_plot[cat].values
    ax2.bar(platform_order, vals, bottom=bottom, label=cat,
            color=cat_colors[cat], edgecolor="white", linewidth=0.5)
    bottom += vals
ax2.set_ylabel("Percentage (%)")
ax2.set_title("DISCERN Quality Category Distribution by Platform")
ax2.legend(title="Category", bbox_to_anchor=(1.02, 1), loc="upper left")
fig2.savefig(os.path.join(FIGURES_DIR, "fig2_discern_categories.png"))
plt.close(fig2)
report("  Fig 2: DISCERN categories stacked bar saved")

# Figure 3: JAMA compliance heatmap
fig3, ax3 = plt.subplots(figsize=(8, 5))
jama_heat = jama_compliance.reindex(platform_order)
im = ax3.imshow(jama_heat.values, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)
ax3.set_xticks(range(len(jama_heat.columns)))
ax3.set_xticklabels(jama_heat.columns, rotation=45, ha="right")
ax3.set_yticks(range(len(jama_heat.index)))
ax3.set_yticklabels(jama_heat.index)
# Add text annotations
for i in range(len(jama_heat.index)):
    for j in range(len(jama_heat.columns)):
        val = jama_heat.values[i, j]
        color = "white" if val < 20 or val > 80 else "black"
        ax3.text(j, i, f"{val:.0f}%", ha="center", va="center", color=color, fontsize=12)
plt.colorbar(im, ax=ax3, label="Compliance (%)")
ax3.set_title("JAMA Benchmark Compliance by Platform")
fig3.savefig(os.path.join(FIGURES_DIR, "fig3_jama_heatmap.png"))
plt.close(fig3)
report("  Fig 3: JAMA heatmap saved")

# Figure 4: Creator type vs DISCERN
fig4, ax4 = plt.subplots(figsize=(10, 6))
ct_data = df.groupby("Creator_Type")["DISCERN_Total"].apply(list).to_dict()
ct_sorted = sorted(ct_data.keys(), key=lambda x: np.median(ct_data[x]), reverse=True)
ct_vals = [ct_data[ct] for ct in ct_sorted]
bp4 = ax4.boxplot(ct_vals, labels=[ct.replace(" ", "\n") for ct in ct_sorted],
                  patch_artist=True, widths=0.6, medianprops=dict(color="black", linewidth=2))
for patch in bp4["boxes"]:
    patch.set_facecolor("#4472C4")
    patch.set_alpha(0.7)
ax4.set_ylabel("DISCERN Total Score")
ax4.set_title("DISCERN Scores by Creator Type")
ax4.tick_params(axis="x", labelsize=9)
fig4.savefig(os.path.join(FIGURES_DIR, "fig4_creator_type_discern.png"))
plt.close(fig4)
report("  Fig 4: Creator type boxplot saved")

# Figure 5: Engagement vs quality scatter
# Row 1: Views vs DISCERN (YouTube and TikTok only — Instagram lacks view counts)
# Row 2: Likes vs DISCERN (all three platforms)
fig5, axes5 = plt.subplots(2, 3, figsize=(15, 10))

# Top row: Views
for idx, p in enumerate(["YouTube", "TikTok", "Instagram"]):
    ax = axes5[0][idx]
    sub = sm[sm["Platform"] == p][["Views", "DISCERN_Total"]].dropna()
    if len(sub) > 2:
        ax.scatter(sub["Views"], sub["DISCERN_Total"], alpha=0.6,
                   color=colors[p], edgecolor="black", linewidth=0.5, s=60)
        ax.set_xlabel("Views")
        ax.set_ylabel("DISCERN Total")
        ax.set_title(f"{p} — Views")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K" if x >= 1e3 else f"{x:.0f}"))
        z = np.polyfit(sub["Views"], sub["DISCERN_Total"], 1)
        x_line = np.linspace(sub["Views"].min(), sub["Views"].max(), 100)
        ax.plot(x_line, np.polyval(z, x_line), "r--", alpha=0.5)
    else:
        ax.set_title(f"{p} — Views")
        ax.text(0.5, 0.5, "Insufficient data\n(platform does not\nexpose view counts)",
                ha="center", va="center", transform=ax.transAxes, fontsize=11, color="grey")
        ax.set_xlabel("Views")
        ax.set_ylabel("DISCERN Total")

# Bottom row: Likes
for idx, p in enumerate(["YouTube", "TikTok", "Instagram"]):
    ax = axes5[1][idx]
    sub = sm[sm["Platform"] == p][["Likes", "DISCERN_Total"]].dropna()
    if len(sub) > 2:
        ax.scatter(sub["Likes"], sub["DISCERN_Total"], alpha=0.6,
                   color=colors[p], edgecolor="black", linewidth=0.5, s=60)
        ax.set_xlabel("Likes")
        ax.set_ylabel("DISCERN Total")
        ax.set_title(f"{p} — Likes")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K" if x >= 1e3 else f"{x:.0f}"))
        z = np.polyfit(sub["Likes"], sub["DISCERN_Total"], 1)
        x_line = np.linspace(sub["Likes"].min(), sub["Likes"].max(), 100)
        ax.plot(x_line, np.polyval(z, x_line), "r--", alpha=0.5)
    else:
        ax.set_title(f"{p} — Likes")
        ax.text(0.5, 0.5, "Insufficient data", ha="center", va="center",
                transform=ax.transAxes, fontsize=11, color="grey")
        ax.set_xlabel("Likes")
        ax.set_ylabel("DISCERN Total")

fig5.suptitle("Engagement Metrics vs DISCERN Quality Score (Social Media)", y=1.02, fontsize=14)
fig5.tight_layout()
fig5.savefig(os.path.join(FIGURES_DIR, "fig5_engagement_vs_quality.png"), dpi=150, bbox_inches="tight")
plt.close(fig5)
report("  Fig 5: Engagement scatter plots saved")

# Figure 6: DISCERN Q1-Q16 heatmap by platform (mean scores)
fig6, ax6 = plt.subplots(figsize=(12, 5))
q_means = df.groupby("Platform")[[f"DISCERN_Q{q}" for q in range(1, 17)]].mean()
q_means = q_means.reindex(platform_order)
q_means.columns = [f"Q{q}" for q in range(1, 17)]
im6 = ax6.imshow(q_means.values, cmap="RdYlGn", aspect="auto", vmin=1, vmax=5)
ax6.set_xticks(range(16))
ax6.set_xticklabels(q_means.columns, fontsize=9)
ax6.set_yticks(range(4))
ax6.set_yticklabels(q_means.index)
for i in range(4):
    for j in range(16):
        val = q_means.values[i, j]
        color = "white" if val < 2 or val > 4 else "black"
        ax6.text(j, i, f"{val:.1f}", ha="center", va="center", color=color, fontsize=8)
plt.colorbar(im6, ax=ax6, label="Mean Score (1-5)")
ax6.set_title("Mean DISCERN Question Scores by Platform")
fig6.savefig(os.path.join(FIGURES_DIR, "fig6_discern_questions_heatmap.png"))
plt.close(fig6)
report("  Fig 6: DISCERN questions heatmap saved")

# Save Q means table
q_means.round(2).to_csv(os.path.join(TABLES_DIR, "discern_question_means_by_platform.csv"))

# ============================================================================
# SECTION 8: ADDITIONAL ANALYSES
# ============================================================================

report("\n" + "=" * 70)
report("SECTION 8: ADDITIONAL ANALYSES")
report("=" * 70)

# 8a. Search term effect
report("\n8a. DISCERN by Search Term:")
for term in df["Search_Term"].unique():
    sub = df[df["Search_Term"] == term]["DISCERN_Total"].dropna()
    report(f"  '{term}': n={len(sub)}, Mdn={sub.median():.1f}, Mean={sub.mean():.1f}")

# Kruskal-Wallis by search term
term_groups = [df[df["Search_Term"] == t]["DISCERN_Total"].dropna().values
               for t in df["Search_Term"].unique()]
h_t, p_t = kruskal(*term_groups)
report(f"  Kruskal-Wallis: H = {h_t:.3f}, p = {p_t:.4f}")

# 8b. Content format effect
report("\n8b. DISCERN by Content Format:")
for fmt in df["Content_Format"].dropna().unique():
    sub = df[df["Content_Format"] == fmt]["DISCERN_Total"].dropna()
    if len(sub) > 0:
        report(f"  '{fmt}': n={len(sub)}, Mdn={sub.median():.1f}, Mean={sub.mean():.1f}")


# ============================================================================
# SAVE REPORT
# ============================================================================

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"\n{'=' * 70}")
print(f"  ANALYSIS COMPLETE")
print(f"  Report: {REPORT_PATH}")
print(f"  Tables: {TABLES_DIR}")
print(f"  Figures: {FIGURES_DIR}")
print(f"{'=' * 70}")
