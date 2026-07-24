import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

JSON_PATH = "generated_biology_paper.json"
PDF_OUTPUT = "generated_biology_paper_reportlab.pdf"

def load_paper(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_pdf(paper, output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCenter",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=12
    )
    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=10
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=16,
        leading=20,
        textColor=colors.darkblue,
        spaceBefore=10,
        spaceAfter=8
    )
    q_style = ParagraphStyle(
        "Question",
        parent=styles["BodyText"],
        fontSize=11,
        leading=14,
        spaceAfter=6
    )
    opt_style = ParagraphStyle(
        "Option",
        parent=styles["BodyText"],
        fontSize=10,
        leading=12,
        leftIndent=14,
        spaceAfter=2
    )
    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#444444"),
        spaceAfter=6
    )

    story = []
    story.append(Paragraph(paper["exam_id"], title_style))
    story.append(Paragraph(f"Paper ID: {paper['paper_id']} | Generated at: {paper['generated_at']}", meta_style))
    story.append(Spacer(1, 8))

    for idx, section in enumerate(paper.get("sections", []), start=1):
        story.append(Paragraph(f"{idx}. {section['subject']}", section_style))
        story.append(Paragraph(f"Total Questions: {section.get('total_questions', len(section.get('questions', [])))}", small_style))

        for qn, q in enumerate(section.get("questions", []), start=1):
            story.append(Paragraph(f"<b>Q{qn}.</b> {q.get('question', '')}", q_style))

            options = q.get("options", ["", "", "", ""])
            opt_labels = ["A", "B", "C", "D"]
            for label, opt in zip(opt_labels, options):
                story.append(Paragraph(f"{label}. {opt}", opt_style))

            story.append(Paragraph(f"<b>Answer:</b> {q.get('answer', '')}", small_style))
            story.append(Paragraph(f"<b>Solution:</b> {q.get('solution', '')}", small_style))
            story.append(Spacer(1, 8))

        if idx != len(paper.get("sections", [])):
            story.append(PageBreak())

    doc.build(story)

if __name__ == "__main__":
    paper = load_paper(JSON_PATH)
    build_pdf(paper, PDF_OUTPUT)
    print(f"Saved: {PDF_OUTPUT}")