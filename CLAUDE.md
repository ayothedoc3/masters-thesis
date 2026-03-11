# CLAUDE.md — Thesis Project Context

## Student
- **Name:** Ayokunle Ademola-John
- **University:** Lithuanian Sports University (LSU), Kaunas
- **Degree:** Master of Public Health (MPH), expected 2026
- **Supervisor:** Dr. Antanas Ūsas
- **Contact:** ayothedoc3@gmail.com

## Thesis Title (Working)
**Quality of Physical Activity Information on Traditional Websites Versus Social Media Platforms: A Cross-Sectional Content Analysis Using DISCERN and JAMA Benchmarks**

## Research Questions
1. How does physical activity information quality differ between traditional websites and social media platforms as measured by DISCERN and JAMA benchmarks?
2. Does creator type (healthcare professional vs fitness influencer vs general user) moderate quality scores?
3. What is the relationship between engagement metrics (views, likes, shares) and information quality?

## Study Design
- **Type:** Cross-sectional content analysis with standardized quality assessment
- **Pivoted from:** Systematic review (existing 2025 publications already cover that ground)
- **Gap this fills:** No single study compares all 4 platform types head-to-head using DISCERN + JAMA on PA content
- **PROSPERO registration:** CRD420251051953 (originally for systematic review)

## Search Terms (5 terms simulating typical user queries)
1. "how to start exercising"
2. "best exercises to lose weight"
3. "strength training for beginners"
4. "physical activity guidelines"
5. "home workout routine"

## Platforms & Sample
| Platform | Method | Sample | IDs |
|----------|--------|--------|-----|
| Traditional websites | Top 10 Google results per term | 50 | WEB-01 to WEB-50 |
| YouTube | Top 10 results per term | 50 | YT-01 to YT-50 |
| TikTok | Top 10 results per term | 50 | TT-01 to TT-50 |
| Instagram | Top 10 results per term | 50 | IG-01 to IG-50 |
| **TOTAL** | | **200** | |

## Inclusion/Exclusion Criteria
**Include:** English language, publicly accessible, substantive PA info, posted/updated within last 3 years
**Exclude:** Duplicates across platforms, paywalled, not primarily about PA, non-English

## Quality Assessment Instruments

### DISCERN (16 items, scored 1-5 each)
- Section 1 (Q1-8): Reliability of publication
- Section 2 (Q9-15): Quality of treatment choice information
- Section 3 (Q16): Overall quality rating
- Score range: 16-80
- Interpretation: 16-26 very poor, 27-38 poor, 39-50 fair, 51-62 good, 63-80 excellent

### JAMA Benchmarks (4 criteria, binary Y/N)
1. **Authorship:** Authors and credentials identified?
2. **Attribution:** References/sources cited?
3. **Disclosure:** Sponsorship/conflicts declared?
4. **Currency:** Date of creation/update provided?

**Social media operationalization:**
- Authorship: Bio states credentials OR verified professional account
- Attribution: Cites studies/sources in caption/description OR shows references on screen
- Disclosure: States sponsorships/partnerships OR #ad tags
- Currency: Post date visible (always YES for social media)

## Data Fields Per Item
**Metadata:** Item ID, Platform, Search term, URL, Title/caption, Creator name, Creator credentials, Date, Views, Likes, Shares, Comments, Creator type (Healthcare professional / Certified fitness professional / Fitness influencer / General user / Organization), Content format (Text article / Long video >5min / Short video <60s / Image+caption / Carousel)

**Scores:** DISCERN Q1-Q16, DISCERN Total, Section 1 subtotal (Q1-8), Section 2 subtotal (Q9-15), JAMA 4 criteria (Y/N each), JAMA Total (0-4), Notes

## Statistical Analysis Plan
| Research Question | Test |
|---|---|
| DISCERN across 4 platforms | Kruskal-Wallis H |
| Pairwise platform comparisons | Dunn's post-hoc + Bonferroni |
| JAMA compliance by platform | Chi-square (or Fisher's exact if n<5) |
| DISCERN by creator type | Mann-Whitney U |
| Engagement vs quality | Spearman's rho |
| Inter-rater reliability | ICC + Cohen's kappa |

**Descriptive:** Median, IQR, range (DISCERN); frequency/% (JAMA)
**Software:** R (packages: irr, FSA, ggplot2) or SPSS

## Inter-Rater Reliability
- Second rater scores 20% (40 items, 10 per platform)
- ICC for DISCERN, Cohen's kappa for JAMA
- Target: ICC >= 0.75, kappa >= 0.61
- Fallback: Test-retest (re-score 20 items after 24h gap)

## Key Comparison Benchmarks
- DISCERN pooled: 43.58/100 (95% CI 37.80-49.35) — JMIR 2025 meta-analysis
- GQS pooled: 49.91 (95% CI 43.31-56.50)
- JAMA-BC pooled: 46.13 (95% CI 38.87-53.39)
- Heterogeneity: I² = 93.22%
- Twitter JAMA: 81% low quality, 95% met only 2/4 criteria — Haghighi & Farhadloo 2025
- TikTok DISCERN: Only 10% by medical professionals — de Moel-Mandel et al. 2025

## Thesis Structure (LSU Requirements)

### Chapter 1: Literature Review (max 4,000 words) — EXISTS (3,062 words)
- 1.1 Digital Transformation of Health Information Seeking
- 1.2 Theoretical Frameworks (IQ Framework, eHEALS, CRAAP, Health Belief Model)
- 1.3 Traditional Websites as Sources of Health and PA Information
- 1.4 Social Media Platforms as Sources of Health Information
- 1.5 Quality Assessment Tools and Cross-Platform Applicability
- 1.6 Evidence for the Quality Gap and Moderating Factors
- 1.7 Summary and Rationale for the Present Study
- **Needs:** Minor updates to reflect pivot from systematic review to cross-sectional

### Chapter 2: Research Methodology — NEEDS COMPLETE REWRITE
Required subsections per LSU regulation:
- 2.1 Research Object
- 2.2 Research Strategy and Logic
- 2.3 Nature of Research
- 2.4 Contingent of Research Subjects
- 2.5 Research Methods
- 2.6 Research Organisation
- 2.7 Methods of Statistical Analysis

### Chapter 3: Research Findings (max 3,000 words) — AFTER DATA COLLECTION
- 3.1 Sample Characteristics
- 3.2 Inter-Rater Reliability
- 3.3 DISCERN Scores by Platform
- 3.4 JAMA Compliance by Platform
- 3.5 Creator Type Analysis
- 3.6 Engagement-Quality Relationship
- 3.7 Content Format Patterns

### Chapter 4: Discussion (max 2,000 words) — AFTER FINDINGS

### Chapter 5: Conclusions and Recommendations — LAST

## LSU Formatting Requirements
- **Font:** Times New Roman, 12pt
- **Page size:** A4
- **Margins:** 1 inch all sides
- **Line spacing:** 1.5
- **Alignment:** Justified
- **Citations:** APA 7th edition
- **Language:** English (Lithuanian abstract may be required)

## LSU Regulation Key Points (from Masters_regulation-3-3.pdf)
- Final thesis = independent analytical work based on independent applied research
- Cannot be entirely theoretical (must have primary data)
- Must be placed in ETD IS (electronic thesis system)
- Reviewed by 2 reviewers appointed by Study Programme Director
- Presentation: up to 10 minutes to committee of 3-5 members
- Assessment weighted: Scientific level 0.80, Integrity/design 0.20
- Student must provide evidence of presenting findings at a scientific conference
- Ethics Committee permission required (Note: this study uses publicly available content, no human subjects)
- Plagiarism detection required by supervisor

## Project File Structure
```
Masters Thesis/
├── BATTLE_PLAN.md           # 2-day execution plan
├── CLAUDE.md                # This file
├── PROJECT_STRUCTURE.md     # Directory map
├── data/                    # Raw data (csv, screenshots, spreadsheet)
├── scripts/                 # Playwright automation
├── analysis/                # R scripts and output
├── scoring-guides/          # DISCERN quick-reference
├── chapters/                # Chapter drafts
├── references/              # Bibliography
├── appendices/              # Thesis appendices
└── final/                   # Assembled thesis
```

## Deliverables Claude Builds
1. Data collection spreadsheet (Excel) — `data/data_collection_spreadsheet.xlsx`
2. DISCERN Quick-Reference Scoring Card — `scoring-guides/discern_quick_reference.md`
3. Playwright automation script — `scripts/playwright_collector.js`
4. R analysis script — `analysis/analysis_script.R`
5. Chapter 2 Methodology — `chapters/chapter2_methodology.docx`
6. Chapter 3 Findings (after data) — `chapters/chapter3_findings.docx`
7. Chapter 4 Discussion (after data) — `chapters/chapter4_discussion.docx`
8. Chapter 5 Conclusions (after data) — `chapters/chapter5_conclusions.docx`
9. Final assembly — `final/thesis_complete.docx`

## Key References (from Chapter 1)
Eysenbach (2002), Fox & Duggan (2013), Charnock et al. (1999), Silberg et al. (1997), Boyer et al. (2011), Kbaier et al. (2024), WHO (2023), Moorhead et al. (2013), Norman & Skinner (2006)
