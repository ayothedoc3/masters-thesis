"""
Finalize the assembled thesis in Microsoft Word:
- update TOC and all fields
- force heading styles to black after Word processing
- save the final DOCX
- export PDF
"""
from __future__ import annotations

import os
import re
import shutil
import sys
import zipfile


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX_PATH = os.path.join(ROOT, "final", "thesis_complete.docx")
PDF_PATH = os.path.join(ROOT, "final", "thesis_complete.pdf")
TEMP_DOCX_PATH = os.path.join(ROOT, "final", "thesis_complete_tmp.docx")
FIG1_PATH = os.path.join(ROOT, "analysis", "output", "figures", "fig1_discern_boxplot.png")
APPENDIX_F_PATH = os.path.join(ROOT, "appendices", "appendix_f_conference_evidence.docx")
def force_black_heading_styles(docx_path: str) -> None:
    def patch_style_block(xml_text: str, style_id: str) -> str:
        pattern = rf'(<w:style\b[^>]*w:styleId="{style_id}"[^>]*>.*?<w:rPr>)(.*?)(</w:rPr>.*?</w:style>)'

        def repl(match: re.Match[str]) -> str:
            start, middle, end = match.groups()
            middle = re.sub(r"<w:color\b[^>]*/>", "", middle)
            middle = re.sub(r'<w:rFonts\b[^>]*/>', '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>', middle)
            if "<w:rFonts" not in middle:
                middle = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>' + middle
            middle += '<w:color w:val="000000"/>'
            return start + middle + end

        return re.sub(pattern, repl, xml_text, count=1, flags=re.DOTALL)

    temp_path = f"{docx_path}.patched"
    with zipfile.ZipFile(docx_path, "r") as zin, zipfile.ZipFile(temp_path, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/styles.xml":
                text = data.decode("utf-8")
                for style_id in ("Heading1", "Heading2", "Heading3", "Heading1Char", "Heading2Char", "Heading3Char"):
                    text = patch_style_block(text, style_id)
                data = text.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(temp_path, docx_path)


def fix_image_collision(docx_path: str) -> None:
    with zipfile.ZipFile(APPENDIX_F_PATH, "r") as zf:
        cert_image_name = next(name for name in zf.namelist() if name.startswith("word/media/"))
        cert_bytes = zf.read(cert_image_name)
    fig1_bytes = open(FIG1_PATH, "rb").read()

    temp_path = f"{docx_path}.patched"
    with zipfile.ZipFile(docx_path, "r") as zin:
        docxml = zin.read("word/document.xml").decode("utf-8")
        relsxml = zin.read("word/_rels/document.xml.rels").decode("utf-8")
        media_names = [name for name in zin.namelist() if name.startswith("word/media/")]

        if docxml.count('r:embed="rId6"') != 2:
            return

        next_image_num = max(int(re.search(r"image(\d+)\.", name).group(1)) for name in media_names) + 1
        new_image_name = f"word/media/image{next_image_num}.png"
        rid_nums = [int(num) for num in re.findall(r'Relationship Id="rId(\d+)"', relsxml)]
        new_rid = f"rId{max(rid_nums) + 1}"

        docxml = re.sub(
            r'(<pic:cNvPr id="0" name="image\.png".*?<a:blip r:embed=")rId6(")',
            rf"\1{new_rid}\2",
            docxml,
            count=1,
            flags=re.DOTALL,
        )
        rel_insert = (
            f'<Relationship Id="{new_rid}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
            f'Target="media/image{next_image_num}.png"/>'
        )
        relsxml = relsxml.replace("</Relationships>", rel_insert + "</Relationships>")

        with zipfile.ZipFile(temp_path, "w") as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    data = docxml.encode("utf-8")
                elif item.filename == "word/_rels/document.xml.rels":
                    data = relsxml.encode("utf-8")
                elif item.filename == "word/media/image1.png":
                    data = fig1_bytes
                zout.writestr(item, data)
            zout.writestr(new_image_name, cert_bytes)

    shutil.move(temp_path, docx_path)


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
        for style_name in ("Normal", "Heading 1", "Heading 2", "Heading 3"):
            try:
                style = doc.Styles(style_name)
                style.Font.Name = "Times New Roman"
                style.Font.Color = 0  # wdColorBlack
            except Exception:
                pass
        seen_references = False
        in_annexes = False
        for para in doc.Paragraphs:
            text = para.Range.Text.strip().replace("\r", "").replace("\x07", "")
            try:
                style_name = str(para.Range.Style)
            except Exception:
                style_name = ""
            if style_name in ("Heading 1", "Heading 2", "Heading 3"):
                para.Range.Font.Name = "Times New Roman"
                para.Range.Font.Color = 0  # wdColorBlack
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
        pages = doc.ComputeStatistics(2)  # wdStatisticPages
        doc.Close(SaveChanges=False)
        doc = None
        shutil.move(TEMP_DOCX_PATH, DOCX_PATH)
        force_black_heading_styles(DOCX_PATH)
        fix_image_collision(DOCX_PATH)
        doc = word.Documents.Open(DOCX_PATH)
        doc.ExportAsFixedFormat(
            OutputFileName=PDF_PATH,
            ExportFormat=17,  # wdExportFormatPDF
            OpenAfterExport=False,
            OptimizeFor=0,
            CreateBookmarks=1,
        )
        doc.Close(SaveChanges=False)
        doc = None
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
