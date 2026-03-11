# 2-Day Thesis Completion Battle Plan

## Reality Check
---
**Total work hours available:** ~32 hours (two 16-hour days)

**The bottleneck:** DISCERN scoring 200 items manually = ~20 hours at 6 min/item (experienced pace). This is non-negotiable — it IS the research.

**Everything else** (data collection, writing, analysis) will be automated or AI-assisted around the scoring.

---

## PRE-DAY 1: Night Before (1-2 hours prep)

### YOU DO (30 min)
- [ ] Confirm with supervisor that the pivot to cross-sectional study is approved (WhatsApp/email — even informal "yes" works)
- [ ] Identify a second rater (classmate, friend with health background) — message them now asking for ~3 hours of their time in Day 2
- [ ] Install Node.js if not already installed (`node -v` to check)
- [ ] Install Playwright: `npm install playwright` then `npx playwright install chromium`
- [ ] Print or have open: DISCERN handbook (https://www.discern.org.uk/discern_instrument.php)

### CLAUDE BUILDS (while you prep)
- [ ] **Tool 1:** Data collection spreadsheet (Excel) — 200 rows, all columns, dropdown validations, auto-calculations
- [ ] **Tool 2:** Playwright automation script — Google + YouTube search, screenshot, metadata extraction
- [ ] **Tool 3:** DISCERN Quick-Reference Scoring Card — decision tree for each of the 16 questions adapted for web/social media
- [ ] **Tool 4:** R analysis script — ready to run once data is entered
- [ ] **Tool 5:** Chapter 2 (Methodology) — complete rewrite for cross-sectional design

---

## DAY 1: Data Collection + Scoring Sprint

### BLOCK 1: 06:00 - 08:00 | Automated Data Collection (Google + YouTube)

**AUTOMATION RUNS (you supervise)**

Run the Playwright script. It will:
1. Open incognito Chromium browser
2. Search each of the 5 terms on Google -> capture top 10 results each
3. Search each of the 5 terms on YouTube -> capture top 10 results each
4. For each result, extract and save to CSV:
   - URL, title, author/channel, date, engagement metrics
   - Screenshot (saved as PNG with item ID)
5. Output: `google_results.csv` (50 rows) + `youtube_results.csv` (50 rows) + 100 screenshots

**Your active time: ~20 min** (launch script, spot-check results, fix any blocked searches)

**While script runs:** Review the DISCERN Quick-Reference Card. Practice-score 2-3 random health websites to calibrate yourself. This warm-up is critical for consistent scoring.

### BLOCK 2: 08:00 - 09:30 | Manual Data Collection (TikTok + Instagram)

**YOU DO (manual, no automation possible)**

**TikTok (50 items) - 45 min:**
1. Open TikTok in incognito browser (no login needed for search)
2. Search each of the 5 terms
3. For each term, record the top 10 results in the spreadsheet:
   - Copy URL from share button
   - Title/caption (first line)
   - Creator name + whether they claim credentials in bio
   - View count, likes, comments
   - Screenshot
4. Mark creator type: professional / fitness influencer / general user / organization

**Instagram (50 items) - 45 min:**
1. Open Instagram web in incognito (can browse without login via search)
2. Search each of the 5 terms via hashtag or explore
3. Record top 10 Reels/posts per term (same fields as TikTok)
4. Note: Instagram may limit results without login — if blocked, log in on a secondary/throwaway account

**Speed tip:** Don't read content deeply yet. Just capture metadata + screenshot. You'll score quality in the next block.

### BLOCK 3: 09:30 - 10:00 | Data Consolidation

**SEMI-AUTOMATED**

1. Import the Playwright CSVs into the master spreadsheet
2. Verify all 200 rows are populated with metadata
3. Quick scan: remove any duplicates, replace excluded items with next result in search ranking
4. Fill in any missing fields from manual collection
5. Assign Item IDs: `WEB-01` to `WEB-50`, `YT-01` to `YT-50`, `TT-01` to `TT-50`, `IG-01` to `IG-50`

**Checkpoint: You should have 200 rows with complete metadata. Zero DISCERN/JAMA scores yet.**

### BLOCK 4: 10:00 - 13:00 | DISCERN + JAMA Scoring - Websites (50 items)

**YOU DO (this is the core research — no shortcuts)**

**Pace: 6 minutes per item = 5 hours for 50 items (with breaks)**

For each website:
1. Open the URL (or use the screenshot for quick reference)
2. Read/scan the content (you're assessing quality, not memorizing)
3. Score DISCERN Q1-Q16 using the Quick-Reference Card:
   - Q1: Are aims clear? -> 1-5
   - Q2: Does it achieve its aims? -> 1-5
   - Q3-Q8: Reliability section -> 1-5 each
   - Q9-Q15: Treatment choices section -> 1-5 each
   - Q16: Overall quality rating -> 1-5
4. Score JAMA 4 criteria (Y/N each):
   - Authorship identified? Y/N
   - Sources/references cited? Y/N
   - Disclosure of conflicts? Y/N
   - Date provided? Y/N
5. Note creator type (already captured) and any observations in the Notes column
6. **Enter directly into the spreadsheet** — don't use paper

**Target: 50 websites scored by 13:00**

### BLOCK 5: 13:00 - 13:30 | Lunch Break
Eat. Step away from the screen. You need to stay sharp for 200 judgments.

### BLOCK 6: 13:30 - 16:30 | DISCERN + JAMA Scoring - YouTube (50 items)

**YOU DO**

**YouTube scoring adjustments:**
- You do NOT need to watch entire videos. Watch first 2-3 minutes + scan through for structure
- For longer videos (>10 min): check intro, one middle section, conclusion
- DISCERN Q1 (aims clear): Does the title/intro state what they'll cover?
- DISCERN Q3 (relevance): Is this actually about what the search term asked?
- JAMA Authorship: Check video description + channel "About" page for credentials
- JAMA Attribution: Do they cite studies? Show references on screen?

**Target: 50 YouTube videos scored by 16:30**

### BLOCK 7: 16:30 - 17:00 | Break + Data Backup

- Save spreadsheet to cloud (Google Drive / OneDrive)
- Quick sanity check: are any DISCERN totals outside 16-80 range? Fix errors now
- Stretch, coffee, fresh air

### BLOCK 8: 17:00 - 19:30 | DISCERN + JAMA Scoring - TikTok (50 items)

**YOU DO**

**TikTok scoring adjustments (these are SHORT — fastest to score):**
- Most TikToks are 15-60 seconds — you can watch in full
- DISCERN will naturally score LOW for most (limited depth = low scores on Q2, Q9-Q15)
- Don't overthink: if a 30-second video doesn't discuss treatment alternatives (Q10), it's a 1
- JAMA Currency: always YES (post date visible)
- JAMA Authorship: check bio for credentials
- Many will score 1-2 on most DISCERN items — that IS the finding

**Target: 50 TikTok items scored by 19:30**

### BLOCK 9: 19:30 - 22:00 | DISCERN + JAMA Scoring - Instagram (50 items)

**YOU DO**

**Instagram scoring adjustments:**
- Reels: treat like TikTok (watch in full, mostly short)
- Carousel posts: swipe through all slides
- Image + caption posts: read full caption
- DISCERN will vary more here — some accounts post detailed infographics
- JAMA Attribution: check if caption cites sources (common in medical IG accounts)

**Target: ALL 200 items scored by 22:00**

### BLOCK 10: 22:00 - 23:00 | Day 1 Wrap-Up

**CLAUDE DOES (you review)**

While you were scoring all day, Claude should have already prepared:
- [ ] Chapter 2 (Methodology) — complete draft
- [ ] R analysis script — tested and ready
- [ ] DISCERN scoring guide document

**YOU DO (30 min):**
- [ ] Final data backup
- [ ] Send 40 randomly selected items (10 per platform) to your second rater with instructions and the scoring guide
- [ ] Quick review of Chapter 2 draft — flag any issues for morning

**Day 1 End State: All 200 items scored. Second rater has their 40 items. Chapter 2 drafted.**

---

## DAY 2: Analysis + Writing Sprint

### BLOCK 11: 06:00 - 07:00 | Run Statistical Analysis

**FULLY AUTOMATED (R script)**

1. Export spreadsheet data as CSV
2. Run the R script Claude built — it will:
   - Calculate descriptive statistics (median, IQR per platform for DISCERN; frequencies for JAMA)
   - Run Kruskal-Wallis H test (DISCERN across 4 platforms)
   - Run Dunn's post-hoc with Bonferroni correction
   - Run Chi-square tests (JAMA compliance by platform)
   - Run Mann-Whitney U (DISCERN by creator type: professional vs non-professional)
   - Run Spearman's rho (engagement metrics vs DISCERN scores)
   - Generate all tables and figures (box plots, bar charts, scatter plots)
   - Export results as formatted tables + PNG figures
3. Review output for sanity (are the numbers plausible?)

**Your active time: ~15 min** (run script, review output)

**While R runs:** Start reviewing Chapter 2 methodology draft from last night.

### BLOCK 12: 07:00 - 08:00 | Inter-Rater Reliability

**Two scenarios:**

**Scenario A: Second rater completed their 40 items overnight/early morning**
- Import their scores
- Run ICC (DISCERN) and Cohen's kappa (JAMA) calculations (built into R script)
- Document results: ICC >= 0.75 = good; kappa >= 0.61 = substantial
- If agreement is low on specific items: discuss and resolve discrepancies, report both pre- and post-discussion values

**Scenario B: No second rater available**
- Score 20 items yourself again (without looking at original scores) — "test-retest reliability"
- Calculate ICC on your own repeated scores
- Acknowledge single-rater limitation explicitly in methodology and discussion
- This is honest and acceptable for a master's thesis — just be transparent about it

### BLOCK 13: 08:00 - 10:00 | Write Chapter 3 (Findings)

**CLAUDE DRAFTS -> YOU REVIEW AND EDIT**

**Process:**
1. Feed Claude your actual statistical output (tables, p-values, figures)
2. Claude writes Chapter 3 sections based on YOUR real data:
   - 3.1 Sample Characteristics (flow diagram, content type breakdown)
   - 3.2 Inter-Rater Reliability (ICC and kappa results)
   - 3.3 DISCERN Scores by Platform (descriptive stats, Kruskal-Wallis, post-hoc)
   - 3.4 JAMA Compliance by Platform (frequencies, chi-square)
   - 3.5 Creator Type Analysis (Mann-Whitney U)
   - 3.6 Engagement-Quality Relationship (Spearman correlations)
3. You review every sentence for accuracy against your data
4. You add your own interpretation where Claude's phrasing doesn't match your understanding
5. Insert figures and tables at appropriate locations

**Claude drafts: ~30 min. Your review/editing: ~1.5 hours.**

**CRITICAL: Every number in Chapter 3 must match your spreadsheet. Spot-check at least 5 statistics against the raw data.**

### BLOCK 14: 10:00 - 10:15 | Break

### BLOCK 15: 10:15 - 12:30 | Write Chapter 4 (Discussion)

**CLAUDE DRAFTS -> YOU REVIEW AND EDIT**

**Process:**
1. Claude compares YOUR findings to existing literature:
   - Your DISCERN scores vs. JMIR 2025 meta-analysis pooled estimate (43.58/100)
   - Your JAMA compliance vs. Haghighi & Farhadloo 2025 (95% met <=2/4 criteria)
   - Your PA-specific findings vs. JMIR Infodemiology 2025 PA misinformation review
   - Your cross-platform comparison — what's NEW that no one else has shown?
2. Discuss practical implications:
   - What should consumers know?
   - What should content creators do differently?
   - What should platforms consider?
   - What should health educators learn from this?
3. Limitations section (be honest):
   - Single rater for 80% of sample (or test-retest if no second rater)
   - English-only content
   - Snapshot in time (search results change daily)
   - Search algorithm personalization (mitigated by incognito)
   - DISCERN was designed for health treatment info — adaptation to fitness content is a limitation
   - Engagement metrics != actual reach/impact
4. Future research directions

**Claude drafts: ~30 min. Your review/editing: ~1.5 hours.**

### BLOCK 16: 12:30 - 13:00 | Lunch

### BLOCK 17: 13:00 - 14:00 | Write Chapter 5 (Conclusions)

**CLAUDE DRAFTS -> YOU REVIEW AND EDIT**

Shortest chapter. Based on YOUR findings:
- Summary of key findings (1-2 paragraphs)
- Practical recommendations (for consumers, creators, platforms, educators)
- Final synthesis connecting back to your research questions

**Claude drafts: ~15 min. Your review/editing: ~45 min.**

### BLOCK 18: 14:00 - 15:30 | Revise Chapter 1 (Literature Review) + Chapter 2 (Methodology)

**YOU DO (with Claude's help)**

**Chapter 1 updates needed:**
- Add paragraph on cross-sectional content analysis as a methodology in health info research
- Update any language that assumed systematic review methodology
- Ensure all cited existing reviews (JMIR 2025 etc.) are properly referenced
- Add any new references discovered during the study

**Chapter 2 finalization:**
- Review Claude's draft from Day 1
- Ensure it accurately describes EXACTLY what you did (not what you planned)
- Update any details that changed during actual data collection (e.g., if Instagram required login, note that)
- Verify all statistical tests match what was actually run

### BLOCK 19: 15:30 - 17:30 | Assembly + Formatting

**CLAUDE BUILDS -> YOU REVIEW**

1. Assemble all 5 chapters into a single document
2. Format according to LSU thesis requirements:
   - Title page
   - Table of contents
   - List of tables
   - List of figures
   - Abstract (write LAST — 250 words summarizing the entire study)
   - References (ensure all citations are complete and consistent)
   - Appendices:
     - A: DISCERN scoring instrument
     - B: JAMA Benchmarks criteria
     - C: Complete data collection spreadsheet (or summary)
     - D: R analysis code
3. Consistent formatting: headings, fonts, spacing, margins per university guidelines
4. Number all tables and figures sequentially
5. Cross-check all in-text references to tables/figures

### BLOCK 20: 17:30 - 19:00 | Quality Control Pass

**YOU DO (non-negotiable)**

1. **Read the entire thesis start to finish** — does it flow logically?
2. **Check every statistic:** Does Chapter 3 match R output? Does Chapter 4 reference Chapter 3 numbers correctly?
3. **Check every table/figure:** Is it labeled? Referenced in text? Numbers correct?
4. **Check references:** Every citation in text has a reference entry and vice versa
5. **Grammar/spelling:** Quick pass (or use Grammarly)
6. **Abstract:** Does it accurately summarize what you found?

### BLOCK 21: 19:00 - 20:00 | Final Fixes + Submission Prep

- Fix any issues found in QC pass
- Generate final PDF
- Final backup to cloud
- Prepare submission email/upload

**Day 2 End State: Complete thesis ready for submission.**

---

## What Claude Builds For You (request these in order)

| # | Deliverable | When to Request | Estimated Build Time |
|---|---|---|---|
| 1 | **Data Collection Spreadsheet** (Excel) | NOW | 20 min |
| 2 | **DISCERN Quick-Reference Scoring Card** | NOW | 15 min |
| 3 | **Playwright Automation Script** | NOW | 30 min |
| 4 | **Chapter 2: Methodology** (complete draft) | NOW | 30 min |
| 5 | **R Analysis Script** | After Block 2 | 20 min |
| 6 | **Chapter 3: Findings** (from your data) | Day 2, Block 13 | 30 min |
| 7 | **Chapter 4: Discussion** (from your data) | Day 2, Block 15 | 30 min |
| 8 | **Chapter 5: Conclusions** | Day 2, Block 17 | 15 min |
| 9 | **Final Assembly + Formatting** | Day 2, Block 19 | 45 min |

---

## Time Budget Summary

| Activity | Hours | Who |
|---|---|---|
| Automated data collection (Google + YouTube) | 2.0 | Script (you supervise 20 min) |
| Manual data collection (TikTok + Instagram) | 1.5 | You |
| DISCERN + JAMA scoring (200 items) | 10.0 | You (the core research) |
| Statistical analysis | 1.0 | R script (you review 15 min) |
| Inter-rater reliability | 1.0 | You + second rater |
| Writing Chapters 3-5 | 4.0 | Claude drafts, You edit |
| Revising Chapters 1-2 | 1.5 | You (Claude assists) |
| Assembly + formatting | 2.0 | Claude builds, You review |
| Quality control | 1.5 | You |
| Breaks + buffers | 3.0 | Rest |
| **TOTAL** | **~27.5** | **Fits in 32 hours** |

---

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| TikTok blocks browsing without login | Use phone browser, screenshot and record manually |
| Instagram limits search results | Log in with secondary account, or reduce to 40 IG items and increase others |
| Scoring takes longer than 6 min/item | Skip notes column, use the Quick-Reference Card strictly, don't deliberate — first instinct is usually right |
| No second rater available | Do test-retest reliability on 20 items yourself (score them again 24 hours later) |
| R script errors | Claude debugs in real-time; SPSS or jamovi as backup |
| Supervisor wants changes to methodology | The design is standard — cross-sectional content analysis with DISCERN/JAMA is well-established in the literature |
| You hit a wall mentally | The scoring is repetitive — listen to music/podcasts while doing it. Take 5-min breaks every 25 items (Pomodoro) |

---

## Non-Negotiable Quality Standards

Even in a sprint, these cannot be skipped:

1. **Every DISCERN score is YOUR genuine assessment** — not guessed, not auto-generated
2. **Inter-rater reliability is calculated** — even if test-retest, it must exist
3. **Every statistic in the thesis matches the data** — no rounding errors, no wrong p-values
4. **Limitations are honestly stated** — academic integrity matters more than impressive results
5. **All references are real and correctly cited** — no fabricated sources
6. **The abstract accurately reflects the study** — reviewers read this first
