# Master's Thesis Repository

## Title

**Quality of Physical Activity Information on Traditional Websites Versus Social Media Platforms: A Cross-Sectional Content Analysis Using DISCERN and JAMA Benchmarks**

Author: Ayokunle Ademola-John  
Institution: Lithuanian Sports University  
Degree: Master of Public Health

## Repository Purpose

This repository contains the thesis writing files, audited dataset, analysis code, appendix-generation scripts, and final submission outputs for the cross-sectional content analysis.

The project compares the quality of physical activity information across:

- Traditional websites
- YouTube
- TikTok
- Instagram

Quality was assessed using:

- DISCERN
- JAMA Benchmarks

## Final Submission Files

The final submission artifacts are in [`final/`](final):

- [`final/thesis_complete.docx`](final/thesis_complete.docx)
- [`final/thesis_complete.pdf`](final/thesis_complete.pdf)

## Final Audited Data and Analysis

The final audited input files are:

- [`data/csv/master_dataset_corrected.csv`](data/csv/master_dataset_corrected.csv)
- [`data/csv/second_rater_scores.csv`](data/csv/second_rater_scores.csv)

The authoritative final analysis script is:

- [`analysis/run_analysis.py`](analysis/run_analysis.py)

Legacy or development-stage files are retained for transparency but were not used as the final reporting source where a corrected replacement exists.

## Reproducing the Analysis

### Environment

The thesis analysis was run with Python 3.13 and the following packages:

- `pandas`
- `scipy`
- `pingouin`
- `scikit-posthocs`
- `matplotlib`
- `seaborn`

### Run

From the project root:

```powershell
python analysis/run_analysis.py
```

This writes refreshed outputs to:

- [`analysis/output/analysis_report.txt`](analysis/output/analysis_report.txt)
- [`analysis/output/tables/`](analysis/output/tables)
- [`analysis/output/figures/`](analysis/output/figures)

## Thesis Assembly

The thesis can be reassembled from the chapter and appendix source files with:

```powershell
python scripts/assemble_thesis.py
```

Important note:

- The assembly script rebuilds the thesis body from source files, but the final submitted Word file required a manual Word pass to insert a live table of contents, update fields, and export the PDF.
- The submission-ready files are therefore the versions already stored in [`final/`](final), not a freshly assembled file without the Word pass.

## Audit Trail

Audit and verification materials are included for transparency:

- [`audit/verification_fields.csv`](audit/verification_fields.csv)
- [`audit/verification_items.csv`](audit/verification_items.csv)
- [`scripts/apply_audit.py`](scripts/apply_audit.py)

These files document the verification and correction workflow used to produce the final audited dataset.

## Repository Structure

- [`chapters/`](chapters): thesis chapter source files
- [`appendices/`](appendices): appendix files
- [`analysis/`](analysis): analysis code and generated statistical outputs
- [`data/`](data): datasets, screenshots, and spreadsheet assets
- [`scripts/`](scripts): chapter, appendix, audit, and assembly scripts
- [`final/`](final): final submission outputs and submission notes

## Notes

- This repository contains a reproducible record of the submitted thesis at the time of submission.
- Some platform URLs or public online content referenced in the dataset may change or disappear over time.
