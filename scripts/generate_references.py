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
REFERENCES = [
    'Avram, M., Micallef, N., Patil, S., & Menczer, F. (2020). Exposure to social engagement metrics increases vulnerability to misinformation. Harvard Kennedy School Misinformation Review, 1(5). https://doi.org/10.37016/mr-2020-033',

    'Azer, S. A. (2020). Are DISCERN and JAMA suitable instruments for assessing YouTube videos on thyroid cancer? Methodological concerns. Journal of Cancer Education, 35(6), 1267\u20131277.',

    'Bernard, A., Langille, M., Hughes, S., Rose, C., Leddin, D., & Veldhuyzen van Zanten, S. (2007). A systematic review of patient inflammatory bowel disease information resources on the World Wide Web. American Journal of Gastroenterology, 102(9), 2070\u20132077. https://doi.org/10.1111/j.1572-0241.2007.01325.x',

    'Blakeslee, S. (2004). The CRAAP test. LOEX Quarterly, 31(3), 6\u20137. https://commons.emich.edu/loexquarterly/vol31/iss3/4',

    'Boyer, C., Baujard, V., & Geissbuhler, A. (2011). Evolution of health web certification through the HONcode experience. Studies in Health Technology and Informatics, 169, 53\u201357. https://doi.org/10.3233/978-1-60750-806-9-53',

    'Charnock, D., Shepperd, S., Needham, G., & Gann, R. (1999). DISCERN: An instrument for judging the quality of written consumer health information on treatment choices. Journal of Epidemiology and Community Health, 53(2), 105\u2013111. https://doi.org/10.1136/jech.53.2.105',

    'Chea, C. Y., & Lim, P. K. (2023). Quality and accuracy of dental health-related information on social media: A systematic review. Journal of Dental Sciences, 18(3), 1070\u20131079.',

    'Chen, S., Tang, Y., Zhang, Y., Liu, Z., Zhong, Y., Fang, H., Xu, Y., Sun, J., & Zhang, Y. (2025). Quality of cancer-related information on new media (2014\u20132023): Systematic review and meta-analysis. Journal of Medical Internet Research, 27(1), e73185. https://doi.org/10.2196/73185',

    'Cooke, A., Smith, D., & Booth, A. (2012). Beyond PICO: The SPIDER tool for qualitative evidence synthesis. Qualitative Health Research, 22(10), 1435\u20131443. https://doi.org/10.1177/1049732312452938',

    'Czenczek-Lewandowska, E., Leszczak, J., Mazur, A., & Rak, S. (2022). Review of the quality of YouTube videos recommending exercises for the COVID-19 lockdown. International Journal of Environmental Research and Public Health, 19(10), 6348. https://doi.org/10.3390/ijerph19106348',

    'Daraz, L., Morrow, A. S., Ponce, O. J., Farah, W., Katabi, A., Majzoub, A., Seisa, M. O., Benkhadra, R., Alsawas, M., Larry, P., & Murad, M. H. (2019). Can patients trust online health information? A meta-narrative systematic review addressing the quality of health information on the internet. Journal of General Internal Medicine, 34(9), 1884\u20131891. https://doi.org/10.1007/s11606-019-05109-0',

    'Dinis-Oliveira, R. J. (2020). COVID-19 research: Pandemic versus \u201cpaperdemic,\u201d integrity, values and risks of the \u201cpublish or perish\u201d pressure. Forensic Sciences Research, 5(4), 279\u2013284.',

    'Diviani, N., van den Putte, B., Giani, S., & van Weert, J. C. (2015). Low health literacy and evaluation of online health information: A systematic review of the literature. Journal of Medical Internet Research, 17(5), e112. https://doi.org/10.2196/jmir.4018',

    'Dos Santos, M. A., Grosso, A. R., & Almeida, C. F. (2021). Is social media spreading misinformation on exercise and health in Brazil? International Journal of Environmental Research and Public Health, 18(22), 11914. https://doi.org/10.3390/ijerph182211914',

    'Eysenbach, G., Powell, J., Kuss, O., & Sa, E. R. (2002). Empirical studies assessing the quality of health information for consumers on the World Wide Web: A systematic review. JAMA, 287(20), 2691\u20132700. https://doi.org/10.1001/jama.287.20.2691',

    'Finney Rutten, L. J., Blake, K. D., Greenberg-Worisek, A. J., Allen, S. V., Moser, R. P., & Hesse, B. W. (2019). Online health information seeking among US adults: Measuring progress toward a Healthy People 2020 objective. Public Health Reports, 134(6), 617\u2013625. https://doi.org/10.1177/0033354919874074',

    'Fox, S., & Duggan, M. (2013). Health online 2013. Pew Internet and American Life Project. https://www.pewresearch.org/internet/2013/01/15/health-online-2013-2/',

    'Haghighi, R., & Farhadloo, M. (2025). Quality assessment of health information on social media during a public health crisis: Infodemiology study. JMIR Infodemiology, 5(1), e70756. https://doi.org/10.2196/70756',

    'Kbaier, D., Kalra, P. A., & Alderson, H. V. (2024). Social media health misinformation: Characteristics of sharers and non-sharers. JMIR Infodemiology, 4, e45459.',

    'Kocyigit, B. F., Akyol, A., & Gundogdu, A. A. (2024). YouTube as a source of information about ankylosing spondylitis exercises. Journal of Education and Health Promotion, 13, 23.',

    'Kong, W., Song, S., Zhao, Y. C., Zhu, Q., & Sha, L. (2024). TikTok as a health information source: Assessment of the quality of information in diabetes-related videos. Journal of Medical Internet Research, 26, e49592.',

    'Koo, T. K., & Li, M. Y. (2016). A guideline of selecting and reporting intraclass correlation coefficients for reliability research. Journal of Chiropractic Medicine, 15(2), 155\u2013163. https://doi.org/10.1016/j.jcm.2016.02.012',

    'Krippendorff, K. (2018). Content analysis: An introduction to its methodology (4th ed.). SAGE Publications.',

    'Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159\u2013174. https://doi.org/10.2307/2529310',

    'Li, B., Liu, X., Zhang, Y., Wang, Y., & Zheng, L. (2024). Quality assessment of health science-related short videos on TikTok: A scoping review. International Journal of Medical Informatics, 186, 105424. https://doi.org/10.1016/j.ijmedinf.2024.105424',

    'Moorhead, S. A., Hazlett, D. E., Harrison, L., Carroll, J. K., Irwin, A., & Hoving, C. (2013). A new dimension of health care: Systematic review of the uses, benefits, and limitations of social media for health communication. Journal of Medical Internet Research, 15(4), e85. https://doi.org/10.2196/jmir.1933',

    'Norman, C. D., & Skinner, H. A. (2006). eHEALS: The eHealth Literacy Scale. Journal of Medical Internet Research, 8(4), e27. https://doi.org/10.2196/jmir.8.4.e27',

    'Pan, B., Hembrooke, H., Joachims, T., Lorigo, L., Gay, G., & Granka, L. (2007). In Google we trust: Users\u2019 decisions on rank, position, and relevance. Journal of Computer-Mediated Communication, 12(3), 801\u2013823.',

    'Pew Research Center. (2021). Social media fact sheet. https://www.pewresearch.org/internet/fact-sheet/social-media/',

    'Pilgrim, K., & Bohnet-Joschko, S. (2022). Selling health and happiness: How influencers communicate on Instagram about dieting and exercise. BMC Public Health, 19, 1054. https://doi.org/10.1186/s12889-019-7387-8',

    'Rosenstock, I. M. (1974). Historical origins of the Health Belief Model. Health Education Monographs, 2(4), 328\u2013335. https://doi.org/10.1177/109019817400200403',

    'Sbaffi, L., & Rowley, J. (2017). Trust and credibility in web-based health information: A review and agenda for future research. Journal of Medical Internet Research, 19(6), e218. https://doi.org/10.2196/jmir.7579',

    'Silberg, W. M., Lundberg, G. D., & Musacchio, R. A. (1997). Assessing, controlling, and assuring the quality of medical information on the internet: Caveant lector et viewor\u2014Let the reader and viewer beware. JAMA, 277(15), 1244\u20131245. https://doi.org/10.1001/jama.1997.03540390074039',

    'Snelson, C. L. (2016). Qualitative and mixed methods social media research: A review of the literature. International Journal of Qualitative Methods, 15(1), 1\u201315. https://doi.org/10.1177/1609406915624574',

    'Suarez-Lledo, V., & Alvarez-Galvez, J. (2021). Prevalence of health misinformation on social media: Systematic review. Journal of Medical Internet Research, 23(1), e17187. https://doi.org/10.2196/17187',

    'Swire-Thompson, B., & Lazer, D. (2020). Public health and online misinformation: Challenges and recommendations. Annual Review of Public Health, 41, 433\u2013451. https://doi.org/10.1146/annurev-publhealth-040119-094127',

    'Tan, S. S.-L., & Goonawardene, N. (2017). Internet health information seeking and the patient-physician relationship: A systematic review. Journal of Medical Internet Research, 19(1), e9. https://doi.org/10.2196/jmir.5729',

    'Tripodi, F. (2018). Searching for alternative facts: Analyzing scriptural inference in conservative news practices. Data & Society Research Institute.',

    'Wang, R. Y., & Strong, D. M. (1996). Beyond accuracy: What data quality means to data consumers. Journal of Management Information Systems, 12(4), 5\u201333. https://doi.org/10.1080/07421222.1996.11518099',

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
