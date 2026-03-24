# OSF Preregistration Draft
## (Copy-paste each section into the corresponding OSF form field)

---

### 1. Title
Quality of Physical Activity Information on Traditional Websites Versus Social Media Platforms: A Cross-Sectional Content Analysis Using DISCERN and JAMA Benchmarks

---

### 2. Authors / Contributors
Ayokunle Ademola-John¹, Antanas Ūsas¹
¹ Lithuanian Sports University, Kaunas, Lithuania

---

### 3. Description / Abstract
This study evaluates the quality of physical activity (PA) information across four digital platform types—traditional websites (via Google search), YouTube, TikTok, and Instagram—using two validated instruments: the DISCERN tool (16-item scale, range 16–80) and the JAMA Benchmarks (4 binary criteria). A total of 200 content items (50 per platform) will be identified using five standardised search terms that simulate typical user queries. Each item will be independently scored, with inter-rater reliability assessed on a 20% subsample. The study addresses a gap in the literature: no single study has compared all four platform types head-to-head using both DISCERN and JAMA on physical activity content.

---

### 4. Hypotheses
**Research Question 1:** How does physical activity information quality differ between traditional websites and social media platforms as measured by DISCERN and JAMA benchmarks?
- H1a: Traditional websites will have significantly higher median DISCERN scores than social media platforms (YouTube, TikTok, Instagram).
- H1b: Traditional websites will have significantly higher JAMA benchmark compliance (total score 0–4) than social media platforms.

**Research Question 2:** Does creator type (healthcare professional vs. fitness influencer vs. general user) moderate quality scores?
- H2: Content created by healthcare professionals will score significantly higher on DISCERN and JAMA than content by fitness influencers or general users.

**Research Question 3:** What is the relationship between engagement metrics (views, likes, shares) and information quality?
- H3: There will be no significant positive correlation between engagement metrics and DISCERN/JAMA scores; higher engagement does not predict higher quality.

---

### 5. Study Type
Observational / Cross-sectional content analysis

---

### 6. Data Collection Procedures

**Search strategy:**
Five search terms simulating typical user queries will be entered into each platform:
1. "how to start exercising"
2. "best exercises to lose weight"
3. "strength training for beginners"
4. "physical activity guidelines"
5. "home workout routine"

**Platforms and sampling:**
| Platform | Search method | Sample size |
|---|---|---|
| Traditional websites | Top 10 Google results per term | 50 |
| YouTube | Top 10 results per term | 50 |
| TikTok | Top 10 results per term | 50 |
| Instagram | Top 10 results per term | 50 |
| **Total** | | **200** |

**Inclusion criteria:**
- English language
- Publicly accessible (no paywall or login required)
- Contains substantive physical activity information
- Posted or last updated within the past 3 years

**Exclusion criteria:**
- Duplicate content across platforms
- Behind a paywall or requiring account access
- Not primarily about physical activity
- Non-English language

**Data collection procedure:**
Searches will be conducted using a fresh browser session (incognito/private mode) to minimise algorithmic personalisation. For each search term on each platform, the first 10 results meeting inclusion criteria will be recorded. Metadata (title, URL, creator name, creator credentials, date, engagement metrics) and content screenshots will be captured for each item.

---

### 7. Variables

**Independent variables:**
- Platform type (4 levels: Traditional website, YouTube, TikTok, Instagram)
- Creator type (4 levels: Healthcare professional, Certified fitness professional, Fitness influencer, General user/Organization)
- Content format (5 levels: Text article, Long video >5 min, Short video <60 s, Image + caption, Carousel)

**Dependent variables:**
- DISCERN total score (16–80, continuous)
- DISCERN Section 1 subtotal: Reliability of publication (Q1–Q8, range 8–40)
- DISCERN Section 2 subtotal: Quality of treatment choice information (Q9–Q15, range 7–35)
- DISCERN Section 3: Overall quality rating (Q16, range 1–5)
- JAMA total score (0–4, ordinal)
- Individual JAMA criteria (Authorship, Attribution, Disclosure, Currency; binary Y/N each)

**Covariates / engagement metrics:**
- Views, Likes, Shares, Comments (continuous, log-transformed if skewed)

---

### 8. Quality Assessment Instruments

**DISCERN (Charnock et al., 1999):**
A validated 16-item instrument for evaluating the quality of written consumer health information. Each item scored 1 (definite no) to 5 (definite yes). Total score range: 16–80. Interpretation bands: 16–26 very poor, 27–38 poor, 39–50 fair, 51–62 good, 63–80 excellent.

**JAMA Benchmarks (Silberg et al., 1997):**
Four binary criteria for health information quality:
1. Authorship — Authors and credentials identified
2. Attribution — References or sources cited
3. Disclosure — Sponsorship or conflicts of interest declared
4. Currency — Date of creation or update provided

**Social media operationalisation of JAMA criteria:**
- Authorship: Bio states credentials OR verified professional account
- Attribution: Cites studies/sources in caption/description OR shows references on screen
- Disclosure: States sponsorships/partnerships OR uses #ad tags
- Currency: Post date visible (always YES for social media platforms that display post dates)

---

### 9. Analysis Plan

**Descriptive statistics:**
- DISCERN scores: Median, interquartile range (IQR), range per platform
- JAMA scores: Frequencies and percentages per criterion per platform
- Creator type and content format distributions per platform

**RQ1 — DISCERN across platforms:**
- Kruskal-Wallis H test (non-parametric; DISCERN scores unlikely to be normally distributed)
- If significant (p < .05): Dunn's post-hoc pairwise comparisons with Bonferroni correction

**RQ1 — JAMA compliance across platforms:**
- Chi-square test of independence (or Fisher's exact test if expected cell count < 5)
- Separate tests for each JAMA criterion and for total JAMA score categories

**RQ2 — Creator type as moderator:**
- Mann-Whitney U test comparing DISCERN scores between healthcare professionals and non-healthcare professionals
- Subgroup analyses by creator type category

**RQ3 — Engagement vs. quality:**
- Spearman's rank correlation (ρ) between engagement metrics (views, likes, shares) and DISCERN total score / JAMA total score
- Correlations computed per platform and overall

**Inter-rater reliability:**
- Intraclass correlation coefficient (ICC, two-way mixed, absolute agreement) for DISCERN scores
- Cohen's kappa (κ) for each binary JAMA criterion
- Assessed on 20% subsample (n = 40 items, 10 per platform)
- Acceptable thresholds: ICC ≥ 0.75 (good), κ ≥ 0.61 (substantial agreement)

**Software:** R (packages: irr, FSA, ggplot2, dplyr)

**Significance level:** α = .05 for all tests

---

### 10. Other — Existing Registrations
This study was originally conceived as a systematic review and registered on PROSPERO (CRD420251051953). The design was subsequently pivoted to a cross-sectional content analysis because recent 2025 publications already cover the systematic review ground. This OSF preregistration documents the actual study design being conducted.

---

### 11. Other — Ethics Statement
This study analyses publicly available online content and does not involve human participants, personal data, or interaction with individuals. No ethics committee approval is required. All content analysed is freely accessible without login or paywall. Creator names are recorded for classification purposes only and will not be reported individually in the thesis.

---

### 12. Other — Timeline
- **March 2025:** Preregistration and instrument preparation
- **March–April 2025:** Data collection (search, screen, record 200 items)
- **April 2025:** Quality scoring (DISCERN + JAMA) and inter-rater reliability assessment
- **April–May 2025:** Statistical analysis and write-up
- **May–June 2025:** Thesis submission

---

### 13. Other — Conflict of Interest
The authors declare no conflicts of interest. This research is conducted as part of a Master of Public Health thesis at Lithuanian Sports University and receives no external funding.
