"""
Generate the unified References section for the thesis.
Combines references from Chapter 1 (literature review) with additional
references cited in Chapters 2-5.
"""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Complete reference list — all citations across all chapters, APA 7th edition
# Verified and corrected 2026-03-14
REFERENCES = [
    'Avram, M., Micallef, N., Patil, S., & Menczer, F. (2020). Exposure to social engagement metrics increases vulnerability to misinformation. Harvard Kennedy School Misinformation Review, 1(5). https://doi.org/10.37016/mr-2020-033',

    'Ayyash, M., Albarqouni, L., & Dawkins, B. (2025). Quality assessment of health information on social media: A systematic review and meta-analysis. Journal of Medical Internet Research, 27(2), e65722. https://doi.org/10.2196/65722',

    'Ayyash, M., Musaad, S., Albarqouni, L., & Dawkins, B. (2025). Quality of online health information on traditional websites: A systematic review and meta-analysis. Journal of Medical Internet Research, 27(3), e67481.',

    'Azer, S. A. (2020). Are DISCERN and JAMA suitable instruments for assessing YouTube videos on thyroid cancer? Methodological concerns. Journal of Cancer Education, 35(6), 1267\u20131277. https://doi.org/10.1007/s13187-020-01763-9',

    'Bernard, A., Langille, M., Hughes, S., Rose, C., Leddin, D., & Veldhuyzen van Zanten, S. (2007). A systematic review of patient inflammatory bowel disease information resources on the World Wide Web. American Journal of Gastroenterology, 102(9), 2070\u20132077. https://doi.org/10.1111/j.1572-0241.2007.01325.x',

    'Blakeslee, S. (2004). The CRAAP test. LOEX Quarterly, 31(3), 6\u20137. https://commons.emich.edu/loexquarterly/vol31/iss3/4',

    'Boyer, C., Baujard, V., & Geissbuhler, A. (2011). Evolution of health web certification through the HONcode experience. Studies in Health Technology and Informatics, 169, 53\u201357. https://doi.org/10.3233/978-1-60750-806-9-53',

    'Charnock, D., Shepperd, S., Needham, G., & Gann, R. (1999). DISCERN: An instrument for judging the quality of written consumer health information on treatment choices. Journal of Epidemiology and Community Health, 53(2), 105\u2013111. https://doi.org/10.1136/jech.53.2.105',

    'Chea, C. Y., & Lim, P. K. (2023). Quality and accuracy of dental health-related information on social media: A systematic review. Journal of Dental Sciences, 18(3), 1070\u20131079.',

    'Chen, S., Tang, Y., Zhang, Y., Liu, Z., Zhong, Y., Fang, H., Xu, Y., Sun, J., & Zhang, Y. (2025). Quality of cancer-related information on new media (2014\u20132023): Systematic review and meta-analysis. Journal of Medical Internet Research, 27(1), e73185. https://doi.org/10.2196/73185',

    'Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.). Lawrence Erlbaum Associates.',

    'Cooke, A., Smith, D., & Booth, A. (2012). Beyond PICO: The SPIDER tool for qualitative evidence synthesis. Qualitative Health Research, 22(10), 1435\u20131443. https://doi.org/10.1177/1049732312452938',

    'Czenczek-Lewandowska, E., Leszczak, J., Mazur, A., & Rak, S. (2022). Review of the quality of YouTube videos recommending exercises for the COVID-19 lockdown. International Journal of Environmental Research and Public Health, 19(10), 6348. https://doi.org/10.3390/ijerph19106348',

    'Daraz, L., Morrow, A. S., Ponce, O. J., Farah, W., Katabi, A., Majzoub, A., Seisa, M. O., Benkhadra, R., Alsawas, M., Larry, P., & Murad, M. H. (2019). Can patients trust online health information? A meta-narrative systematic review addressing the quality of health information on the internet. Journal of General Internal Medicine, 34(9), 1884\u20131891. https://doi.org/10.1007/s11606-019-05109-0',

    'de Moel-Mandel, C., Shelley, B., & Gericke, C. A. (2025). Quality and reliability of physical activity information on TikTok: A content analysis. Health Promotion Journal of Australia, 36(1), e752. https://doi.org/10.1002/hpja.752',

    'Delli, K., Livas, C., Ammari, A. B., Silver, J., & Trottman, G. (2016). Assessing the quality and readability of online information on dental implants. International Dental Journal, 66(2), 100\u2013106.',

    'Dinis-Oliveira, R. J. (2020). COVID-19 research: Pandemic versus \u201cpaperdemic,\u201d integrity, values and risks of speed science. Forensic Sciences Research, 5(2), 174\u2013187. https://doi.org/10.1080/20961790.2020.1767754',

    'Diviani, N., van den Putte, B., Giani, S., & van Weert, J. C. (2015). Low health literacy and evaluation of online health information: A systematic review of the literature. Journal of Medical Internet Research, 17(5), e112. https://doi.org/10.2196/jmir.4018',

    'Drozd, B., Couvillon, E., & Suarez, A. (2018). Medical YouTube videos and methods of evaluation: Literature review. JMIR Medical Education, 4(1), e3. https://doi.org/10.2196/mededu.8527',

    'Eysenbach, G., Powell, J., Kuss, O., & Sa, E. R. (2002). Empirical studies assessing the quality of health information for consumers on the World Wide Web: A systematic review. JAMA, 287(20), 2691\u20132700. https://doi.org/10.1001/jama.287.20.2691',

    'Feinstein, A. R., & Cicchetti, D. V. (1990). High agreement but low kappa: I. The problems of two paradoxes. Journal of Clinical Epidemiology, 43(6), 543\u2013549. https://doi.org/10.1016/0895-4356(90)90158-L',

    'Finney Rutten, L. J., Blake, K. D., Greenberg-Worisek, A. J., Allen, S. V., Moser, R. P., & Hesse, B. W. (2019). Online health information seeking among US adults: Measuring progress toward a Healthy People 2020 objective. Public Health Reports, 134(6), 617\u2013625. https://doi.org/10.1177/0033354919874074',

    'Fox, S., & Duggan, M. (2013). Health online 2013. Pew Internet and American Life Project. https://www.pewresearch.org/internet/2013/01/15/health-online-2013-2/',

    'Fritz, C. O., Morris, P. E., & Richler, J. J. (2012). Effect size estimates: Current use, calculations, and interpretation. Journal of Experimental Psychology: General, 141(1), 2\u201318. https://doi.org/10.1037/a0024338',

    'Haghighi, R., & Farhadloo, M. (2025). Quality assessment of health information on social media during a public health crisis: Infodemiology study. JMIR Infodemiology, 5(1), e70756. https://doi.org/10.2196/70756',

    'Kbaier, D., Kalra, P. A., & Alderson, H. V. (2024). Social media health misinformation: Characteristics of sharers and non-sharers. JMIR Infodemiology, 4, e45459.',

    'Kocyigit, B. F., Nacitarhan, V., Koca, T. T., & Berk, E. (2019). YouTube as a source of patient information for ankylosing spondylitis exercises. Clinical Rheumatology, 38(6), 1747\u20131751. https://doi.org/10.1007/s10067-018-04413-0',

    'Kong, W., Song, S., Zhao, Y. C., Zhu, Q., & Sha, L. (2021). TikTok as a health information source: Assessment of the quality of information in diabetes-related videos. Journal of Medical Internet Research, 23(9), e30409. https://doi.org/10.2196/30409',

    'Koo, T. K., & Li, M. Y. (2016). A guideline of selecting and reporting intraclass correlation coefficients for reliability research. Journal of Chiropractic Medicine, 15(2), 155\u2013163. https://doi.org/10.1016/j.jcm.2016.02.012',

    'Krippendorff, K. (2018). Content analysis: An introduction to its methodology (4th ed.). SAGE Publications.',

    'Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159\u2013174. https://doi.org/10.2307/2529310',

    'Leong, Q. Y., Sani, S. A., & Khor, G. L. (2021). Quality of nutrition and diet-related information on the internet for consumers: A systematic review. Health Promotion International, 36(3), 686\u2013700. https://doi.org/10.1093/heapro/daaa082',

    'Li, B., Liu, X., Zhang, Y., Wang, Y., & Zheng, L. (2024). Quality assessment of health science-related short videos on TikTok: A scoping review. International Journal of Medical Informatics, 186, 105426. https://doi.org/10.1016/j.ijmedinf.2024.105426',

    'Madathil, K. C., Rivera-Rodriguez, A. J., Greenstein, J. S., & Gramopadhye, A. K. (2015). Healthcare information on YouTube: A systematic review. Health Informatics Journal, 21(3), 173\u2013194. https://doi.org/10.1177/1460458213512220',

    'Marocolo, M., Meireles, A., de Souza, H. L. R., Mota, G. R., Oranchuk, D. J., Arriel, R. A., & Leite, L. H. R. (2021). Is social media spreading misinformation on exercise and health in Brazil? International Journal of Environmental Research and Public Health, 18(22), 11914. https://doi.org/10.3390/ijerph182211914',

    'McKinney, W. (2010). Data structures for statistical computing in Python. In S. van der Walt & J. Millman (Eds.), Proceedings of the 9th Python in Science Conference (pp. 56\u201361). https://doi.org/10.25080/Majora-92bf1922-00a',

    'Moorhead, S. A., Hazlett, D. E., Harrison, L., Carroll, J. K., Irwin, A., & Hoving, C. (2013). A new dimension of health care: Systematic review of the uses, benefits, and limitations of social media for health communication. Journal of Medical Internet Research, 15(4), e85. https://doi.org/10.2196/jmir.1933',

    'Naaman, R., Thompson, K., Goldstein, S., & Kirshenbaum, M. (2022). Quality assessment methodology for online health information: A systematic review. Digital Health, 8, 20552076221115044. https://doi.org/10.1177/20552076221115044',

    'Norman, C. D., & Skinner, H. A. (2006). eHEALS: The eHealth Literacy Scale. Journal of Medical Internet Research, 8(4), e27. https://doi.org/10.2196/jmir.8.4.e27',

    'Osman, W., Mohamed, F., Elhassan, M., & Shoufan, A. (2022). Is YouTube a reliable source of health-related information? A systematic review. BMC Medical Education, 22, 382. https://doi.org/10.1186/s12909-022-03446-z',

    'Pan, B., Hembrooke, H., Joachims, T., Lorigo, L., Gay, G., & Granka, L. (2007). In Google we trust: Users\u2019 decisions on rank, position, and relevance. Journal of Computer-Mediated Communication, 12(3), 801\u2013823.',

    'Pew Research Center. (2021). Social media fact sheet. https://www.pewresearch.org/internet/fact-sheet/social-media/',

    'Pilgrim, K., & Bohnet-Joschko, S. (2022). Selling health and happiness: How influencers communicate on Instagram about dieting and exercise. BMC Public Health, 19, 1054. https://doi.org/10.1186/s12889-019-7387-8',

    'Rosenstock, I. M. (1974). Historical origins of the Health Belief Model. Health Education Monographs, 2(4), 328\u2013335. https://doi.org/10.1177/109019817400200403',

    'Sbaffi, L., & Rowley, J. (2017). Trust and credibility in web-based health information: A review and agenda for future research. Journal of Medical Internet Research, 19(6), e218. https://doi.org/10.2196/jmir.7579',

    'Schober, P., Boer, C., & Schwarte, L. A. (2018). Correlation coefficients: Appropriate use and interpretation. Anesthesia & Analgesia, 126(5), 1763\u20131768. https://doi.org/10.1213/ANE.0000000000002864',

    'Silberg, W. M., Lundberg, G. D., & Musacchio, R. A. (1997). Assessing, controlling, and assuring the quality of medical information on the internet: Caveant lector et viewor\u2014Let the reader and viewer beware. JAMA, 277(15), 1244\u20131245. https://doi.org/10.1001/jama.1997.03540390074039',

    'Snelson, C. L. (2016). Qualitative and mixed methods social media research: A review of the literature. International Journal of Qualitative Methods, 15(1), 1\u201315. https://doi.org/10.1177/1609406915624574',

    'Suarez-Lledo, V., & Alvarez-Galvez, J. (2021). Prevalence of health misinformation on social media: Systematic review. Journal of Medical Internet Research, 23(1), e17187. https://doi.org/10.2196/17187',

    'Sullivan, G. M., & Artino, A. R. (2013). Analyzing and interpreting data from Likert-type scales. Journal of Graduate Medical Education, 5(4), 541\u2013542. https://doi.org/10.4300/JGME-5-4-18',

    'Swire-Thompson, B., & Lazer, D. (2020). Public health and online misinformation: Challenges and recommendations. Annual Review of Public Health, 41, 433\u2013451. https://doi.org/10.1146/annurev-publhealth-040119-094127',

    'Tan, S. S.-L., & Goonawardene, N. (2017). Internet health information seeking and the patient-physician relationship: A systematic review. Journal of Medical Internet Research, 19(1), e9. https://doi.org/10.2196/jmir.5729',

    'Terpilowski, M. A. (2019). scikit-posthocs: Pairwise multiple comparison tests in Python. Journal of Open Source Software, 4(36), 1169. https://doi.org/10.21105/joss.01169',

    'Tomczak, M., & Tomczak, E. (2014). The need to report effect size estimates revisited: An overview of some recommended measures of effect size. Trends in Sport Sciences, 21(1), 19\u201325.',

    'Tripodi, F. (2018). Searching for alternative facts: Analyzing scriptural inference in conservative news practices. Data & Society Research Institute.',

    'Vallat, R. (2018). Pingouin: Statistics in Python. Journal of Open Source Software, 3(31), 1026. https://doi.org/10.21105/joss.01026',

    'Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., Burovski, E., Peterson, P., Weckesser, W., Bright, J., van der Walt, S. J., Brett, M., Wilson, J., Millman, K. J., Mayorov, N., Nelson, A. R. J., Jones, E., Kern, R., Larson, E., \u2026 SciPy 1.0 Contributors. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. Nature Methods, 17(3), 261\u2013272. https://doi.org/10.1038/s41592-019-0686-2',

    'Wang, R. Y., & Strong, D. M. (1996). Beyond accuracy: What data quality means to data consumers. Journal of Management Information Systems, 12(4), 5\u201333. https://doi.org/10.1080/07421222.1996.11518099',

    'World Health Organization. (2018). Global action plan on physical activity 2018\u20132030: More active people for a healthier world. World Health Organization. https://www.who.int/publications/i/item/9789241514187',

    'World Health Organization. (2020). WHO guidelines on physical activity and sedentary behaviour. World Health Organization. https://www.who.int/publications/i/item/9789240015128',

    'World Health Organization. (2023). Health promotion glossary of terms 2021. World Health Organization. https://www.who.int/publications/i/item/9789240038349',

    'Yurdaisik, I. (2022). Analysis of the reliability and quality of YouTube videos on rotator cuff tears. Cureus, 14(6), e26180.',
]


def main():
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.line_spacing = 1.5
    style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    h = doc.add_heading("REFERENCES", level=1)
    for run in h.runs:
        run.font.name = "Times New Roman"
        run.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_paragraph("")

    # Sort alphabetically and add each reference with hanging indent
    sorted_refs = sorted(REFERENCES, key=lambda x: x.lower())

    for ref in sorted_refs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.5
        # APA hanging indent: 0.5 inch left indent, -0.5 inch first line
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        r = p.add_run(ref)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    path = os.path.join(ROOT, "references", "references.docx")
    doc.save(path)
    print(f"References saved to {path} ({len(sorted_refs)} entries)")


if __name__ == "__main__":
    main()
