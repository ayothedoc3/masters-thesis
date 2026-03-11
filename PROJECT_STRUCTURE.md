# Project Structure

```
Masters Thesis/
|
|-- BATTLE_PLAN.md              # The 2-day execution plan (this file)
|-- PROJECT_STRUCTURE.md        # You are here
|
|-- data/
|   |-- csv/                    # Raw data exports
|   |   |-- google_results.csv      # Playwright output (50 rows)
|   |   |-- youtube_results.csv     # Playwright output (50 rows)
|   |   |-- tiktok_results.csv      # Manual entry export
|   |   |-- instagram_results.csv   # Manual entry export
|   |   |-- master_dataset.csv      # All 200 items, scored (R input)
|   |   |-- second_rater.csv        # 40-item subset for IRR
|   |
|   |-- screenshots/
|   |   |-- google/             # WEB-01.png to WEB-50.png
|   |   |-- youtube/            # YT-01.png to YT-50.png
|   |   |-- tiktok/             # TT-01.png to TT-50.png
|   |   |-- instagram/          # IG-01.png to IG-50.png
|   |
|   |-- data_collection_spreadsheet.xlsx   # Master spreadsheet (Tool 1)
|
|-- scripts/
|   |-- playwright_collector.js     # Automated Google + YouTube scraper (Tool 2)
|   |-- package.json                # Node dependencies
|
|-- analysis/
|   |-- analysis_script.R           # Full statistical analysis (Tool 4)
|   |-- output/
|       |-- tables/             # Formatted result tables
|       |-- figures/            # Box plots, bar charts, scatter plots
|
|-- scoring-guides/
|   |-- discern_quick_reference.md  # DISCERN scoring card (Tool 3)
|
|-- chapters/
|   |-- chapter1_literature_review.docx    # Existing (to revise)
|   |-- chapter2_methodology.docx          # Claude draft (Tool 5)
|   |-- chapter3_findings.docx             # Claude draft from data (Tool 6)
|   |-- chapter4_discussion.docx           # Claude draft from data (Tool 7)
|   |-- chapter5_conclusions.docx          # Claude draft (Tool 8)
|
|-- references/
|   |-- references.bib              # Bibliography file
|
|-- appendices/
|   |-- appendix_a_discern.md       # DISCERN instrument
|   |-- appendix_b_jama.md          # JAMA benchmarks
|   |-- appendix_c_data.md          # Data summary
|   |-- appendix_d_rcode.md         # R analysis code
|
|-- final/
|   |-- thesis_complete.docx        # Assembled final document
|   |-- thesis_complete.pdf         # Final PDF for submission
```

## Deliverable Tracking

| # | Deliverable | Location | Status |
|---|---|---|---|
| 1 | Data Collection Spreadsheet | `data/data_collection_spreadsheet.xlsx` | Pending |
| 2 | DISCERN Quick-Reference Card | `scoring-guides/discern_quick_reference.md` | Pending |
| 3 | Playwright Automation Script | `scripts/playwright_collector.js` | Pending |
| 4 | R Analysis Script | `analysis/analysis_script.R` | Pending |
| 5 | Chapter 2: Methodology | `chapters/chapter2_methodology.docx` | Pending |
| 6 | Chapter 3: Findings | `chapters/chapter3_findings.docx` | Pending |
| 7 | Chapter 4: Discussion | `chapters/chapter4_discussion.docx` | Pending |
| 8 | Chapter 5: Conclusions | `chapters/chapter5_conclusions.docx` | Pending |
| 9 | Final Assembly | `final/thesis_complete.docx` | Pending |
