#!/usr/bin/env python3
"""
Generate Chapter 5: Conclusions and Recommendations for Master's Thesis
Lithuanian Sports University
Author: Ayokunle Ademola-John
"""

import subprocess
import sys

# Ensure python-docx is installed
try:
    import docx
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    import docx

from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import os

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_run(run, bold=False, italic=False, size=12, font_name="Times New Roman", color=None):
    """Format a run with specified properties."""
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = font_name
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = parse_xml(
        f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" '
        f'w:hAnsi="{font_name}" w:cs="{font_name}"/>'
    )
    rPr.insert(0, rFonts)
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_paragraph_spacing(paragraph, before=0, after=0, line_spacing=1.5):
    """Set paragraph spacing."""
    pf = paragraph.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line_spacing


def add_formatted_paragraph(doc, text, bold=False, italic=False, size=12,
                             alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                             space_before=0, space_after=6, line_spacing=1.5,
                             first_line_indent=None):
    """Add a fully formatted paragraph."""
    p = doc.add_paragraph()
    p.alignment = alignment
    run = p.add_run(text)
    format_run(run, bold=bold, italic=italic, size=size)
    add_paragraph_spacing(p, before=space_before, after=space_after, line_spacing=line_spacing)
    if first_line_indent is not None:
        p.paragraph_format.first_line_indent = Cm(first_line_indent)
    return p


def add_heading_custom(doc, text, level=1, size=14, space_before=12, space_after=6):
    """Add a custom heading with Times New Roman formatting."""
    p = doc.add_paragraph()
    if level == 1:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    format_run(run, bold=True, size=size)
    add_paragraph_spacing(p, before=space_before, after=space_after, line_spacing=1.5)
    return p


def add_mixed_paragraph(doc, parts, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                         space_before=0, space_after=6, line_spacing=1.5,
                         first_line_indent=None):
    """
    Add a paragraph with mixed formatting.
    parts is a list of tuples: (text, bold, italic)
    """
    p = doc.add_paragraph()
    p.alignment = alignment
    for text, bold, italic in parts:
        run = p.add_run(text)
        format_run(run, bold=bold, italic=italic, size=12)
    add_paragraph_spacing(p, before=space_before, after=space_after, line_spacing=line_spacing)
    if first_line_indent is not None:
        p.paragraph_format.first_line_indent = Cm(first_line_indent)
    return p


# ============================================================
# MAIN DOCUMENT GENERATION
# ============================================================

def generate_chapter5():
    doc = Document()

    # --- Page setup: A4, 1-inch margins ---
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    # --- Set default font ---
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    style.paragraph_format.line_spacing = 1.5
    style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rPr = style.element.get_or_add_rPr()
    rFonts = parse_xml(
        f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" '
        f'w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
    )
    rPr.insert(0, rFonts)

    # ================================================================
    # CHAPTER 5 HEADING
    # ================================================================
    add_heading_custom(doc, "5. CONCLUSIONS AND RECOMMENDATIONS", level=1, size=14,
                       space_before=0, space_after=12)

    # Opening paragraph
    add_formatted_paragraph(
        doc,
        "This chapter synthesises the principal findings of the cross-sectional content "
        "analysis of 200 physical activity information sources across traditional websites, "
        "YouTube, TikTok, and Instagram. Conclusions are drawn in direct correspondence "
        "with the three research questions. Practical recommendations are offered for "
        "public health practitioners, health organisations, platform designers, educators, "
        "policymakers, and consumers. The chapter closes with directions for future research.",
        first_line_indent=1.25, space_after=6
    )

    # ================================================================
    # 5.1 SUMMARY OF CONCLUSIONS
    # ================================================================
    add_heading_custom(doc, "5.1 Summary of Conclusions", level=2, size=12,
                       space_before=12, space_after=6)

    # --- RQ1 ---
    add_mixed_paragraph(doc, [
        ("Research Question 1: Quality differences across platform types.", True, False),
    ], space_before=6, space_after=3, first_line_indent=1.25)

    add_formatted_paragraph(
        doc,
        "The study confirms that statistically significant and practically meaningful "
        "quality differences exist across the four platform types examined. A Kruskal\u2013"
        "Wallis test yielded H(3) = 136.58, p < .001, with a large effect size "
        "(\u03b7\u00b2 = .68), indicating that platform type alone accounts for "
        "approximately 68% of the variance in DISCERN total scores. Traditional websites "
        "achieved the highest median DISCERN score (Mdn = 48), placing them at the upper "
        "boundary of the \u201cFair\u201d category and approaching \u201cGood.\u201d YouTube "
        "followed (Mdn = 33, \u201cPoor\u201d), then TikTok (Mdn = 25, \u201cVery Poor\u201d "
        "to \u201cPoor\u201d), and Instagram ranked lowest (Mdn = 21, \u201cVery Poor\u201d). "
        "These results establish a clear quality gradient: Websites > YouTube > TikTok > "
        "Instagram.",
        first_line_indent=1.25, space_after=6
    )

    add_formatted_paragraph(
        doc,
        "Notably, JAMA benchmark compliance was universally low across all four platforms, "
        "with an overall mean of only 1.4 out of 4 criteria met. Even traditional websites, "
        "which performed best on DISCERN, exhibited poor adherence to basic transparency "
        "standards such as authorship identification, source attribution, conflict-of-interest "
        "disclosure, and currency dating. This finding underscores that the quality deficit in "
        "online physical activity information is not confined to social media; rather, it "
        "reflects a systemic shortcoming in how health-related content is presented across the "
        "digital landscape.",
        first_line_indent=1.25, space_after=6
    )

    # --- RQ2 ---
    add_mixed_paragraph(doc, [
        ("Research Question 2: Moderating role of creator type.", True, False),
    ], space_before=6, space_after=3, first_line_indent=1.25)

    add_formatted_paragraph(
        doc,
        "Creator type significantly moderates information quality (p = .033), with "
        "professional creators\u2014healthcare professionals and certified fitness "
        "professionals\u2014producing content that scores higher on DISCERN than "
        "content from fitness influencers, general users, or organisational accounts. "
        "However, the effect size is small, suggesting that the platform on which content "
        "is published exerts a stronger influence on quality than the credentials of the "
        "creator. This conclusion carries an important practical implication: even "
        "well-qualified professionals may produce lower-quality content when constrained "
        "by the format limitations, algorithmic incentives, and audience expectations "
        "inherent to short-form social media platforms. Professional credentials are "
        "therefore a necessary but insufficient condition for high-quality health "
        "communication online.",
        first_line_indent=1.25, space_after=6
    )

    # --- RQ3 ---
    add_mixed_paragraph(doc, [
        ("Research Question 3: Engagement\u2013quality relationship.", True, False),
    ], space_before=6, space_after=3, first_line_indent=1.25)

    add_formatted_paragraph(
        doc,
        "There is no meaningful association between engagement metrics and information "
        "quality. Spearman\u2019s correlation between view counts and DISCERN total scores "
        "was negligible (\u03c1 = .017), confirming that popular content is not necessarily "
        "accurate content. This decoupling of popularity from quality is particularly "
        "concerning on YouTube, where a negative trend was observed\u2014videos with higher "
        "view counts tended to score lower on DISCERN. Platform recommendation algorithms, "
        "which prioritise engagement signals (watch time, likes, shares) over informational "
        "accuracy, may thus actively disadvantage high-quality health content. From a public "
        "health standpoint, this means that the content most people encounter and consume is "
        "statistically no better\u2014and on YouTube, potentially worse\u2014than content "
        "that remains obscure.",
        first_line_indent=1.25, space_after=6
    )

    # --- Overarching conclusion ---
    add_mixed_paragraph(doc, [
        ("Overarching conclusion.", True, False),
    ], space_before=6, space_after=3, first_line_indent=1.25)

    add_formatted_paragraph(
        doc,
        "Taken together, these findings paint a sobering picture of the current state of "
        "physical activity information online. While traditional websites offer the most "
        "reliable information, even their quality is only \u201cfair\u201d by DISCERN "
        "standards, and their JAMA compliance is poor. Social media platforms\u2014which are "
        "increasingly the primary source of health information for younger demographics\u2014"
        "provide substantially lower quality content, irrespective of creator credentials. "
        "The absence of any link between engagement and quality means that platform "
        "algorithms offer no safeguard against misinformation. These conclusions reinforce "
        "the urgent need for multi-stakeholder interventions to improve the quality of "
        "physical activity information in the digital ecosystem.",
        first_line_indent=1.25, space_after=6
    )

    # ================================================================
    # 5.2 PRACTICAL RECOMMENDATIONS
    # ================================================================
    add_heading_custom(doc, "5.2 Practical Recommendations", level=2, size=12,
                       space_before=12, space_after=6)

    add_formatted_paragraph(
        doc,
        "On the basis of the empirical evidence presented in this thesis, the following "
        "recommendations are offered to six stakeholder groups.",
        first_line_indent=1.25, space_after=6
    )

    # Recommendation 1
    add_mixed_paragraph(doc, [
        ("For public health practitioners. ", True, False),
        ("Clinicians, physiotherapists, and public health professionals should prioritise "
         "directing patients and clients to traditional websites maintained by established "
         "medical organisations (e.g., WHO, NHS, CDC) when recommending online physical "
         "activity resources. Where patients report reliance on social media, practitioners "
         "should provide curated lists of evidence-based accounts and explicitly discuss the "
         "quality limitations documented in this study.", False, False),
    ], first_line_indent=1.25, space_after=6)

    # Recommendation 2
    add_mixed_paragraph(doc, [
        ("For health organisations. ", True, False),
        ("Health authorities, professional bodies, and academic institutions should "
         "substantially increase their presence on social media platforms, particularly "
         "TikTok and Instagram, which currently exhibit the lowest information quality. "
         "Content strategies should be tailored to platform-specific norms\u2014short, "
         "visually engaging, and algorithm-friendly\u2014without sacrificing scientific "
         "accuracy. Partnering with credentialed fitness professionals who already have "
         "established audiences may offer a pragmatic route to scaling evidence-based "
         "content.", False, False),
    ], first_line_indent=1.25, space_after=6)

    # Recommendation 3
    add_mixed_paragraph(doc, [
        ("For platform designers. ", True, False),
        ("Social media companies should consider implementing quality indicators or "
         "verification badges specifically for health content creators with documented "
         "professional credentials. Algorithmic adjustments that factor in source "
         "credibility\u2014not merely engagement metrics\u2014when recommending health-"
         "related content could meaningfully shift the quality landscape. Transparency "
         "features such as mandatory source citation fields for health-tagged content "
         "would address the universally low JAMA compliance observed across platforms.", False, False),
    ], first_line_indent=1.25, space_after=6)

    # Recommendation 4
    add_mixed_paragraph(doc, [
        ("For health literacy educators. ", True, False),
        ("Digital health literacy curricula should teach critical evaluation skills "
         "specific to each platform type. The finding that engagement does not predict "
         "quality is a particularly teachable insight: students and the public must "
         "understand that viral content is not validated content. Frameworks such as "
         "eHEALS (Norman & Skinner, 2006) and the CRAAP test should be adapted to "
         "include platform-specific red flags (e.g., absence of source citations in "
         "video descriptions, lack of professional credentials in creator bios).", False, False),
    ], first_line_indent=1.25, space_after=6)

    # Recommendation 5
    add_mixed_paragraph(doc, [
        ("For policymakers. ", True, False),
        ("Regulatory bodies should develop platform-specific guidelines for health "
         "information quality. Current regulatory frameworks were designed for traditional "
         "media and do not adequately address the unique characteristics of short-form "
         "video, image-based posts, or algorithm-driven content distribution. Minimum "
         "disclosure requirements\u2014analogous to JAMA benchmarks\u2014should be "
         "considered for health-related social media content, particularly regarding "
         "authorship credentials, evidence sourcing, and sponsorship transparency.", False, False),
    ], first_line_indent=1.25, space_after=6)

    # Recommendation 6
    add_mixed_paragraph(doc, [
        ("For consumers. ", True, False),
        ("Individuals seeking physical activity information online should cross-reference "
         "social media health claims with established medical websites before acting on "
         "them. Content that lacks identifiable author credentials, cites no sources, and "
         "does not disclose sponsorship should be treated with caution regardless of how "
         "many views or likes it has accumulated. Preferencing content from verified "
         "healthcare or certified fitness professionals\u2014while not a guarantee of "
         "quality\u2014does offer a statistically better starting point.", False, False),
    ], first_line_indent=1.25, space_after=6)

    # ================================================================
    # 5.3 RECOMMENDATIONS FOR FUTURE RESEARCH
    # ================================================================
    add_heading_custom(doc, "5.3 Recommendations for Future Research", level=2, size=12,
                       space_before=12, space_after=6)

    add_formatted_paragraph(
        doc,
        "While this study provides a comprehensive cross-platform snapshot, several "
        "avenues warrant further investigation.",
        first_line_indent=1.25, space_after=6
    )

    # Future direction 1
    add_mixed_paragraph(doc, [
        ("Longitudinal monitoring. ", True, False),
        ("The present study captured a single time point. Future research should track "
         "quality changes over time to determine whether platform-level trends are "
         "improving, stagnating, or deteriorating. Repeated cross-sectional designs at "
         "6- or 12-month intervals would enable trend analysis and provide evidence for "
         "or against the effectiveness of platform policy changes.", False, False),
    ], first_line_indent=1.25, space_after=6)

    # Future direction 2
    add_mixed_paragraph(doc, [
        ("Multi-language and cross-cultural studies. ", True, False),
        ("This study was limited to English-language content. Given that information "
         "quality may vary substantially by language and cultural context, replication "
         "in other languages\u2014particularly in low- and middle-income country settings "
         "where social media may be the only accessible health information source\u2014is "
         "essential for global public health planning.", False, False),
    ], first_line_indent=1.25, space_after=6)

    # Future direction 3
    add_mixed_paragraph(doc, [
        ("Algorithmic impact studies. ", True, False),
        ("This study assessed the top 10 results per search term but did not manipulate "
         "or control for algorithmic personalisation. Future research using standardised "
         "or \u201cclean\u201d accounts (no prior search history) across multiple "
         "geographic locations would isolate the role of platform algorithms in shaping "
         "which quality tier of content users are most likely to encounter.", False, False),
    ], first_line_indent=1.25, space_after=6)

    # Future direction 4
    add_mixed_paragraph(doc, [
        ("Intervention studies. ", True, False),
        ("Having established the quality baseline, experimental research is needed to "
         "test whether targeted interventions\u2014such as creator training programmes, "
         "platform labelling systems, or algorithm modifications\u2014can measurably "
         "improve social media health content quality. Randomised controlled trials "
         "comparing pre- and post-intervention quality scores would provide the strongest "
         "evidence base for policy recommendations.", False, False),
    ], first_line_indent=1.25, space_after=6)

    # Future direction 5
    add_mixed_paragraph(doc, [
        ("User perception and behavioural studies. ", True, False),
        ("A critical gap remains in understanding whether consumers can recognise the "
         "quality differences documented here. Mixed-methods research pairing quality "
         "assessments with user surveys or think-aloud protocols would reveal the extent "
         "to which audiences distinguish high- from low-quality physical activity content "
         "and how quality perceptions influence health behaviour.", False, False),
    ], first_line_indent=1.25, space_after=6)

    # Future direction 6
    add_mixed_paragraph(doc, [
        ("Platform-specific quality instruments. ", True, False),
        ("DISCERN was originally designed to evaluate written treatment information. "
         "Although its adaptation to multimedia content in this study was systematic, "
         "the development and validation of quality assessment tools designed natively "
         "for short-form video (TikTok, Instagram Reels) and image-based formats would "
         "strengthen future research. Such instruments should incorporate visual accuracy, "
         "demonstration safety, and accessibility features alongside traditional textual "
         "quality criteria.", False, False),
    ], first_line_indent=1.25, space_after=6)

    # ================================================================
    # CLOSING PARAGRAPH
    # ================================================================
    add_formatted_paragraph(
        doc,
        "In conclusion, this study provides robust empirical evidence that the quality "
        "of physical activity information varies dramatically across digital platforms, "
        "is only partially moderated by creator credentials, and bears no relationship "
        "to content popularity. These findings carry direct implications for how public "
        "health professionals guide patients, how organisations communicate evidence, "
        "and how platforms govern health content. Addressing the quality gap will require "
        "coordinated action across clinical practice, digital literacy education, platform "
        "governance, and regulatory policy.",
        first_line_indent=1.25, space_before=6, space_after=12
    )

    # --- Save ---
    output_dir = os.path.join(r"c:\Users\ayoth\Downloads\Masters Thesis", "chapters")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "chapter5_conclusions.docx")
    doc.save(output_path)
    print(f"Chapter 5 saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_chapter5()
