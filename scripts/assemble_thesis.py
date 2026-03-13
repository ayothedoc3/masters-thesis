"""
Assemble the complete thesis from all components into a single .docx file.
Order:
  1. Title Page
  2. Abstract
  3. Acknowledgments
  4. Table of Contents (placeholder)
  5. List of Abbreviations
  6. Chapter 1: Literature Review
  7. Chapter 2: Methodology
  8. Chapter 3: Findings
  9. Chapter 4: Discussion
  10. Chapter 5: Conclusions
  11. References
  12. Appendix A: DISCERN Instrument
  13. Appendix B: JAMA Benchmarks
  14. Appendix C: Data Summary Tables
  15. Appendix D: Analysis Code

LSU Formatting: Times New Roman 12pt, A4, 1" margins, 1.5 spacing, justified.
"""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "final", "thesis_complete.docx")
os.makedirs(os.path.join(ROOT, "final"), exist_ok=True)


def setup_doc():
    doc = Document()
    # Normal style
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style.font.color.rgb = RGBColor(0, 0, 0)
    pf = style.paragraph_format
    pf.line_spacing = 1.5
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.space_after = Pt(0)
    pf.space_before = Pt(0)

    # Heading styles
    for level in range(1, 4):
        hs = doc.styles[f"Heading {level}"]
        hs.font.name = "Times New Roman"
        hs.font.color.rgb = RGBColor(0, 0, 0)
        hs.font.bold = True
        if level == 1:
            hs.font.size = Pt(14)
        elif level == 2:
            hs.font.size = Pt(13)
        else:
            hs.font.size = Pt(12)
        hs.paragraph_format.line_spacing = 1.5
        hs.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        hs.paragraph_format.space_before = Pt(12)
        hs.paragraph_format.space_after = Pt(6)

    # Page setup
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    return doc


def apply_formatting(paragraph):
    """Ensure LSU formatting on a paragraph."""
    for run in paragraph.runs:
        run.font.name = "Times New Roman"
        if not run.bold:
            run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0, 0, 0)
    paragraph.paragraph_format.line_spacing = 1.5


def detect_heading_level(text, style_name):
    """Detect if a paragraph is a heading and what level."""
    if style_name and style_name.startswith("Heading"):
        try:
            return int(style_name.split()[-1])
        except ValueError:
            return 1

    # Chapter titles: "1. LITERATURE REVIEW", "CHAPTER 1.", etc.
    if re.match(r"^(CHAPTER\s+)?\d+\.\s+", text) and len(text) < 80:
        return 1

    # Section headings: "1.1 ", "2.3 ", "C.1 ", "D.2 " etc.
    if re.match(r"^[A-Z0-9]+\.\d+\s", text) and len(text) < 100:
        return 2

    # Subsection: e.g. "Section 1:", "Scoring and Interpretation"
    if style_name and "Heading" in style_name:
        return 2

    return 0


def append_docx(doc, source_path, label=""):
    """Append all paragraphs and tables from a source docx into doc.

    Handles images by copying the binary image parts from the source
    document and creating new relationships in the target document.
    """
    print(f"  Appending: {label or source_path}")
    src = Document(source_path)
    from copy import deepcopy
    from docx.oxml.ns import qn

    # Build a mapping from source relationship IDs to target relationship IDs
    # for any image parts that need to be copied
    rel_map = {}

    # First pass: find all image relationships in the source
    for rel in src.part.rels.values():
        if "image" in rel.reltype:
            # Copy the image part to the target document
            image_part = rel.target_part
            # Add the image to the target document's package
            new_rel = doc.part.relate_to(image_part, rel.reltype)
            rel_map[rel.rId] = new_rel

    # Now copy elements, updating relationship IDs for images
    for element in src.element.body:
        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

        if tag in ("p", "tbl"):
            new_elem = deepcopy(element)

            # Update any image relationship IDs in the copied element
            if rel_map:
                # Find all blip elements (embedded images)
                nsmap = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
                         "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
                for blip in new_elem.iter(qn("a:blip")):
                    embed = blip.get(qn("r:embed"))
                    if embed and embed in rel_map:
                        blip.set(qn("r:embed"), rel_map[embed])

            doc.element.body.append(new_elem)


def add_title_page(doc):
    """Create the title page."""
    for _ in range(6):
        doc.add_paragraph("")

    # Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run(
        "QUALITY OF PHYSICAL ACTIVITY INFORMATION ON TRADITIONAL WEBSITES "
        "VERSUS SOCIAL MEDIA PLATFORMS:\nA CROSS-SECTIONAL CONTENT ANALYSIS "
        "USING DISCERN AND JAMA BENCHMARKS"
    )
    run.bold = True
    run.font.size = Pt(16)
    run.font.name = "Times New Roman"

    doc.add_paragraph("")
    doc.add_paragraph("")

    lines = [
        "Master\u2019s Thesis",
        "",
        "Ayokunle Ademola-John",
        "Master of Public Health Programme",
        "",
        "Supervisor: Dr. Antanas \u016asas",
        "",
        "Lithuanian Sports University",
        "Faculty of Sport Medicine",
        "Kaunas, 2026",
    ]
    for line in lines:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(line)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    doc.add_page_break()


def add_toc_placeholder(doc):
    """Add a table of contents placeholder page."""
    h = doc.add_heading("TABLE OF CONTENTS", level=1)
    for run in h.runs:
        run.font.name = "Times New Roman"
        run.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_paragraph("")

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(
        "[To generate the Table of Contents in Microsoft Word:\n"
        "1. Place cursor here\n"
        "2. Go to References > Table of Contents\n"
        "3. Select a style\n"
        "4. The TOC will auto-populate from Heading styles]"
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(128, 128, 128)
    r.italic = True

    doc.add_paragraph("")

    # Manual TOC as fallback
    toc_entries = [
        ("ABSTRACT", ""),
        ("ACKNOWLEDGMENTS", ""),
        ("LIST OF ABBREVIATIONS", ""),
        ("1. LITERATURE REVIEW", ""),
        ("    1.1 Digital Transformation of Health Information Seeking", ""),
        ("    1.2 Theoretical Frameworks", ""),
        ("    1.3 Traditional Websites as Sources of Health and PA Information", ""),
        ("    1.4 Social Media Platforms as Sources of Health Information", ""),
        ("    1.5 Quality Assessment Tools and Cross-Platform Applicability", ""),
        ("    1.6 Evidence for the Quality Gap and Moderating Factors", ""),
        ("    1.7 Summary and Rationale for the Present Study", ""),
        ("2. RESEARCH METHODOLOGY", ""),
        ("    2.1 Research Object", ""),
        ("    2.2 Research Strategy and Logic", ""),
        ("    2.3 Nature of Research", ""),
        ("    2.4 Contingent of Research Subjects", ""),
        ("    2.5 Research Methods", ""),
        ("    2.6 Research Organisation", ""),
        ("    2.7 Methods of Statistical Analysis", ""),
        ("3. RESEARCH FINDINGS", ""),
        ("4. DISCUSSION", ""),
        ("5. CONCLUSIONS AND RECOMMENDATIONS", ""),
        ("REFERENCES", ""),
        ("APPENDIX A: DISCERN INSTRUMENT", ""),
        ("APPENDIX B: JAMA BENCHMARKS", ""),
        ("APPENDIX C: DATA SUMMARY TABLES", ""),
        ("APPENDIX D: STATISTICAL ANALYSIS CODE", ""),
    ]

    for entry, _ in toc_entries:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(entry)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        p.paragraph_format.line_spacing = 1.5

    doc.add_page_break()


def main():
    print("=" * 60)
    print("ASSEMBLING COMPLETE THESIS")
    print("=" * 60)

    doc = setup_doc()

    # 1. Title Page
    print("\n1. Title Page")
    add_title_page(doc)

    # 2. Abstract
    print("2. Abstract")
    append_docx(doc, os.path.join(ROOT, "chapters", "abstract.docx"), "Abstract")
    doc.add_page_break()

    # 3. Acknowledgments
    print("3. Acknowledgments")
    append_docx(doc, os.path.join(ROOT, "chapters", "acknowledgments.docx"), "Acknowledgments")
    doc.add_page_break()

    # 4. Table of Contents
    print("4. Table of Contents")
    add_toc_placeholder(doc)

    # 5. List of Abbreviations
    print("5. List of Abbreviations")
    append_docx(doc, os.path.join(ROOT, "chapters", "abbreviations.docx"), "Abbreviations")
    doc.add_page_break()

    # 6. Chapter 1
    print("6. Chapter 1: Literature Review")
    append_docx(doc, os.path.join(ROOT, "chapters", "chapter1_literature_review.docx"), "Chapter 1")
    doc.add_page_break()

    # 7. Chapter 2
    print("7. Chapter 2: Methodology")
    append_docx(doc, os.path.join(ROOT, "chapters", "chapter2_methodology.docx"), "Chapter 2")
    doc.add_page_break()

    # 8. Chapter 3
    print("8. Chapter 3: Findings")
    append_docx(doc, os.path.join(ROOT, "chapters", "chapter3_findings.docx"), "Chapter 3")
    doc.add_page_break()

    # 9. Chapter 4
    print("9. Chapter 4: Discussion")
    append_docx(doc, os.path.join(ROOT, "chapters", "chapter4_discussion.docx"), "Chapter 4")
    doc.add_page_break()

    # 10. Chapter 5
    print("10. Chapter 5: Conclusions")
    append_docx(doc, os.path.join(ROOT, "chapters", "chapter5_conclusions.docx"), "Chapter 5")
    doc.add_page_break()

    # 11. References
    print("11. References")
    append_docx(doc, os.path.join(ROOT, "references", "references.docx"), "References")
    doc.add_page_break()

    # 12-15. Appendices
    appendices = [
        ("appendix_a_discern.docx", "Appendix A: DISCERN"),
        ("appendix_b_jama.docx", "Appendix B: JAMA"),
        ("appendix_c_data_summary.docx", "Appendix C: Data Summary"),
        ("appendix_d_analysis_code.docx", "Appendix D: Analysis Code"),
    ]
    for i, (fname, label) in enumerate(appendices, 12):
        print(f"{i}. {label}")
        append_docx(doc, os.path.join(ROOT, "appendices", fname), label)
        if i < 15:
            doc.add_page_break()

    # Save
    doc.save(OUTPUT)
    print(f"\n{'=' * 60}")
    print(f"COMPLETE THESIS SAVED: {OUTPUT}")
    print(f"{'=' * 60}")

    # Verify
    verify = Document(OUTPUT)
    total_paras = sum(1 for p in verify.paragraphs if p.text.strip())
    print(f"Total non-empty paragraphs: {total_paras}")
    print(f"Total sections: {len(verify.sections)}")


if __name__ == "__main__":
    main()
