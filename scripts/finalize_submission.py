"""
Finalize the assembled thesis in Microsoft Word:
- update TOC and all fields
- save the final DOCX
- export PDF
"""
from __future__ import annotations

import os
import shutil
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX_PATH = os.path.join(ROOT, "final", "thesis_complete.docx")
PDF_PATH = os.path.join(ROOT, "final", "thesis_complete.pdf")
TEMP_DOCX_PATH = os.path.join(ROOT, "final", "thesis_complete_tmp.docx")


def main() -> int:
    backup_path = os.path.join(ROOT, "final", "thesis_complete_pre_word_pass_regulation_fix.docx")
    if os.path.exists(DOCX_PATH):
        shutil.copy2(DOCX_PATH, backup_path)

    try:
        import win32com.client  # type: ignore
    except ImportError as exc:
        print(f"pywin32 is required to finalize the thesis in Word: {exc}")
        return 1

    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        doc = word.Documents.Open(DOCX_PATH)
        seen_references = False
        in_annexes = False
        for para in doc.Paragraphs:
            text = para.Range.Text.strip().replace("\r", "").replace("\x07", "")
            if text == "REFERENCES":
                seen_references = True
            if seen_references and text == "ANNEXES":
                in_annexes = True
                continue
            if in_annexes:
                para.Range.Style = "Normal"
                para.OutlineLevel = 10
        if doc.TablesOfContents.Count >= 1:
            doc.TablesOfContents(1).Update()
        doc.Fields.Update()
        doc.Repaginate()
        doc.SaveAs2(TEMP_DOCX_PATH)
        doc.ExportAsFixedFormat(
            OutputFileName=PDF_PATH,
            ExportFormat=17,  # wdExportFormatPDF
            OpenAfterExport=False,
            OptimizeFor=0,
            CreateBookmarks=1,
        )
        pages = doc.ComputeStatistics(2)  # wdStatisticPages
        doc.Close(SaveChanges=False)
        doc = None
        shutil.move(TEMP_DOCX_PATH, DOCX_PATH)
        print(f"Finalized Word file: {DOCX_PATH}")
        print(f"Exported PDF: {PDF_PATH}")
        print(f"Page count: {pages}")
        return 0
    finally:
        if doc is not None:
            doc.Close(SaveChanges=False)
        word.Quit()


if __name__ == "__main__":
    sys.exit(main())
