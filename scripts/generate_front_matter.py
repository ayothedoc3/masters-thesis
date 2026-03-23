"""
Generate front matter components for the thesis:
- Abstract (English)
- Acknowledgments
- List of Abbreviations
These will be incorporated into the final assembly.
"""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def set_style(doc):
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style.paragraph_format.line_spacing = 1.5
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)


def add_heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = "Times New Roman"
        run.font.color.rgb = RGBColor(0, 0, 0)
    return h


def add_para(doc, text, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
             size=Pt(12), spacing_after=None):
    p = doc.add_paragraph()
    p.alignment = align
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = size
    r.bold = bold
    r.italic = italic
    p.paragraph_format.line_spacing = 1.5
    if spacing_after is not None:
        p.paragraph_format.space_after = spacing_after
    return p


# ============================================================
# ABSTRACT
# ============================================================
def generate_abstract():
    doc = Document()
    set_style(doc)

    add_heading(doc, "ABSTRACT", level=1)
    add_para(doc, "")

    add_para(
        doc,
        "Ademola-John, A. (2026). Quality of Physical Activity Information on Traditional "
        "Websites Versus Social Media Platforms: A Cross-Sectional Content Analysis Using "
        "DISCERN and JAMA Benchmarks. Master\u2019s Thesis. Lithuanian Sports University, Kaunas.",
        italic=True,
    )
    add_para(doc, "")

    add_para(
        doc,
        "Background. The internet and social media platforms have become primary sources of "
        "physical activity (PA) information for the general public. However, the quality of "
        "this information varies considerably across platforms, and no study has simultaneously "
        "compared traditional websites, YouTube, TikTok, and Instagram using standardised "
        "quality assessment instruments.",
    )

    add_para(
        doc,
        "Objective. This study aimed to evaluate and compare the quality of PA information "
        "across four digital platform types using the DISCERN instrument and JAMA benchmarks, "
        "and to examine whether creator type and engagement metrics moderate information quality.",
    )

    add_para(
        doc,
        "Methods. A cross-sectional content analysis was conducted on 200 items (50 per platform) "
        "retrieved using five standardised search terms simulating typical user queries. Each item "
        "was assessed using the 16-item DISCERN instrument (scored 1\u20135 per question; total range "
        "16\u201380) and four binary JAMA benchmark criteria (Authorship, Attribution, Disclosure, "
        "Currency). Inter-rater reliability was established on 20% of the sample (n = 40). "
        "Statistical analyses included Kruskal\u2013Wallis H tests, Dunn\u2019s post-hoc comparisons "
        "with Bonferroni correction, Chi-square tests, Mann\u2013Whitney U tests, and Spearman "
        "correlations.",
    )

    add_para(
        doc,
        "Results. A significant quality gradient was observed across platforms, H(3) = 93.49, "
        "p < .001, \u03b7\u00b2 \u2248 .47 (large effect). Traditional websites scored highest "
        "(Mdn = 48.5, Fair), followed by YouTube (Mdn = 42.0, Fair), TikTok (Mdn = 35.0, Poor), "
        "and Instagram (Mdn = 27.5, Poor\u2013Very Poor). All six pairwise comparisons were "
        "statistically significant (p < .05), though the website\u2013YouTube contrast was more "
        "modest (p = .038). JAMA compliance was universally low (M = 1.4/4 criteria met). "
        "Both the binary professional versus non-professional comparison (p = .036) and the "
        "five-category creator type analysis (H[4] = 12.76, p = .012) were significant, "
        "with healthcare professionals scoring highest (Mdn = 45.0) and general users lowest "
        "(Mdn = 33.0). Within YouTube, views and likes showed significant negative correlations "
        "with quality (rho = \u22120.340, p = .016; rho = \u22120.286, p = .044), while other "
        "within-platform correlations were non-significant. Inter-rater reliability was excellent "
        "(ICC = 0.932, 95% CI [0.870, 0.960]).",
    )

    add_para(
        doc,
        "Conclusions. Physical activity information quality differs substantially across digital "
        "platforms, with short-form social media\u2014particularly Instagram and TikTok\u2014providing "
        "lower-quality content than traditional websites. Engagement metrics do not appear to "
        "reliably indicate information quality within platforms, suggesting that popular content "
        "is not necessarily accurate content. These findings highlight the need for multi-stakeholder "
        "interventions targeting platform design, creator education, and consumer health literacy "
        "to improve the quality of PA information in the digital ecosystem.",
    )

    add_para(doc, "")
    add_para(
        doc,
        "Keywords: physical activity, health information quality, DISCERN, JAMA benchmarks, "
        "social media, content analysis, digital health, health literacy",
        italic=True,
    )

    path = os.path.join(ROOT, "chapters", "abstract.docx")
    doc.save(path)
    print(f"Abstract saved to {path}")


# ============================================================
# ACKNOWLEDGMENTS
# ============================================================
def generate_acknowledgments():
    doc = Document()
    set_style(doc)

    add_heading(doc, "ACKNOWLEDGMENTS", level=1)
    add_para(doc, "")

    add_para(
        doc,
        "I would like to express my sincere gratitude to my supervisor, Dr. Antanas \u016asas, "
        "for his guidance, expertise, and encouragement throughout this research project. His "
        "constructive feedback and scholarly insight were invaluable in shaping this thesis.",
    )

    add_para(
        doc,
        "I am grateful to the faculty and staff of the Master of Public Health programme at "
        "Lithuanian Sports University for providing a stimulating academic environment and the "
        "resources necessary to complete this work.",
    )

    add_para(
        doc,
        "I also wish to thank my family and friends for their unwavering support and patience "
        "during the course of my studies. Their encouragement sustained me through the challenges "
        "of graduate research.",
    )

    add_para(
        doc,
        "Finally, I acknowledge that this study analysed publicly available online content and "
        "did not involve human participants. No external funding was received for this research.",
    )

    path = os.path.join(ROOT, "chapters", "acknowledgments.docx")
    doc.save(path)
    print(f"Acknowledgments saved to {path}")


# ============================================================
# LIST OF ABBREVIATIONS
# ============================================================
def generate_abbreviations():
    doc = Document()
    set_style(doc)

    add_heading(doc, "LIST OF ABBREVIATIONS", level=1)
    add_para(doc, "")

    abbreviations = [
        ("APA", "American Psychological Association"),
        ("CDC", "Centers for Disease Control and Prevention"),
        ("CI", "Confidence Interval"),
        ("CRAAP", "Currency, Relevance, Authority, Accuracy, Purpose"),
        ("DISCERN", "Quality criteria for consumer health information (instrument name)"),
        ("eHEALS", "eHealth Literacy Scale"),
        ("GQS", "Global Quality Scale"),
        ("HONcode", "Health on the Net Foundation Code of Conduct"),
        ("ICC", "Intraclass Correlation Coefficient"),
        ("IG", "Instagram"),
        ("IQ", "Information Quality"),
        ("IQR", "Interquartile Range"),
        ("JAMA", "Journal of the American Medical Association"),
        ("Mdn", "Median"),
        ("MPH", "Master of Public Health"),
        ("NHS", "National Health Service"),
        ("PA", "Physical Activity"),
        ("RQ", "Research Question"),
        ("SD", "Standard Deviation"),
        ("TT", "TikTok"),
        ("WHO", "World Health Organization"),
        ("WEB", "Traditional Website"),
        ("YT", "YouTube"),
    ]

    table = doc.add_table(rows=len(abbreviations) + 1, cols=2)
    table.style = "Table Grid"
    # Header
    table.rows[0].cells[0].text = "Abbreviation"
    table.rows[0].cells[1].text = "Full Term"
    for cell in table.rows[0].cells:
        for p in cell.paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)

    for i, (abbr, full) in enumerate(abbreviations):
        table.rows[i + 1].cells[0].text = abbr
        table.rows[i + 1].cells[1].text = full
        for cell in table.rows[i + 1].cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(12)

    path = os.path.join(ROOT, "chapters", "abbreviations.docx")
    doc.save(path)
    print(f"Abbreviations saved to {path}")


if __name__ == "__main__":
    generate_abstract()
    generate_acknowledgments()
    generate_abbreviations()
    print("\nAll front matter generated successfully.")
