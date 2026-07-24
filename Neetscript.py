import re
import json
from pathlib import Path
import pdfplumber

pdf_path = "00_NEET 2024 Paper.pdf"
out_path = "question_bank.json"

def clean_text(t):
    t = t.replace("\x00", " ")
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

def extract_pages(pdf_path):
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append({"page": i, "text": text})
    return pages

def split_questions(text):
    text = text.replace("CLIK HERE To Discover more", " ")
    text = re.sub(r'==Start of OCR.*?==', ' ', text)
    pattern = r'(?m)(?=^\s*\d{1,3}\.\s)'
    parts = re.split(pattern, text)
    questions = []
    for part in parts:
        part = part.strip()
        m = re.match(r'^(\d{1,3})\.\s*(.*)$', part, re.S)
        if m:
            qno = int(m.group(1))
            body = m.group(2).strip()
            questions.append((qno, body))
    return questions

def parse_question_body(body):
    body = re.sub(r'\s+', ' ', body).strip()

    options = {}
    opt_pattern = r'(?=\b[a-d]\.\s)'
    chunks = re.split(opt_pattern, body)
    head = chunks[0].strip()

    opt_matches = re.findall(r'\b([a-d])\.\s*(.*?)(?=\s+[a-d]\.\s|$)', body)
    for k, v in opt_matches:
        options[k] = clean_text(v)

    question_text = head
    question_text = re.sub(r'\s*\[Image of.*?\]', '', question_text, flags=re.I)
    question_text = clean_text(question_text)

    return question_text, options

def detect_fields(question_text):
    subject = None
    section = None
    topic = None
    question_type = "mcq"

    if "Statement I" in question_text or "Assertion A" in question_text:
        question_type = "assertion_reason"
    elif "Match List-I" in question_text or "Match List-I with List-II" in question_text:
        question_type = "match"
    elif re.search(r'Following are the stages|Arrange them in correct sequence', question_text, re.I):
        question_type = "sequence"

    return subject, section, topic, question_type

def build_answer_map():
    return {
        1: "d", 2: "c", 3: "b", 4: "d", 5: "c", 6: "c", 7: "b", 8: "b",
        9: "c", 10: "a", 11: "c", 12: "d", 13: "d", 14: "c", 15: "b", 16: "a"
    }

pages = extract_pages(pdf_path)
answer_map = build_answer_map()
records = []

current_subject = None
current_section = None
current_topic = None

for p in pages:
    qs = split_questions(p["text"])
    for qno, body in qs:
        question_text, options = parse_question_body(body)
        subject, section, topic, question_type = detect_fields(question_text)

        if "Botany" in p["text"]:
            current_subject = "Botany"
        elif "Zoology" in p["text"]:
            current_subject = "Zoology"

        rec = {
            "exam_id": "NEET_2024",
            "page": p["page"],
            "question_no": qno,
            "subject": current_subject,
            "section": current_section,
            "topic": current_topic,
            "question_type": question_type,
            "question": question_text,
            "options": options,
            "answer": answer_map.get(qno),
            "solution": "",
            "source_pdf": Path(pdf_path).name
        }
        records.append(rec)

with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"exam_id": "NEET_2024", "questions": records}, f, ensure_ascii=False, indent=2)

print(f"Saved {len(records)} questions to {out_path}")