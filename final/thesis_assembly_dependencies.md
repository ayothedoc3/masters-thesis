# Thesis Assembly Dependencies

The final thesis document is built by running:

```powershell
python scripts/assemble_thesis.py
```

The script writes the assembled file to:

- `final/thesis_complete.docx`

It pulls content from these source files, in this order:

1. `chapters/abstract.docx`
2. `chapters/acknowledgments.docx`
3. `chapters/abbreviations.docx`
4. `chapters/chapter1_literature_review.docx`
5. `chapters/chapter2_methodology.docx`
6. `chapters/chapter3_findings.docx`
7. `chapters/chapter4_discussion.docx`
8. `chapters/chapter5_conclusions.docx`
9. `references/references.docx`
10. `appendices/appendix_a_discern.docx`
11. `appendices/appendix_b_jama.docx`
12. `appendices/appendix_c_data_summary.docx`
13. `appendices/appendix_d_analysis_code.docx`

Supporting analysis inputs and outputs used by the chapter and appendix generators:

- `data/csv/master_dataset_corrected.csv`
- `data/csv/second_rater_scores.csv`
- `analysis/run_analysis.py`
- `analysis/output/analysis_report.txt`
- `analysis/output/tables/`
- `analysis/output/figures/`

Notes:

- `scripts/assemble_thesis.py` inserts a manual table-of-contents placeholder, not an auto-updating Word TOC field.
- If any chapter or appendix file changes, rerun `python scripts/assemble_thesis.py` before submission.
