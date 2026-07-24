import json
import pandas as pd
import re
from datetime import datetime

EXAM_ID = "NEET_2024"
INPUT_CSV = "cleaned_questions.csv"
BLUEPRINT_JSON = "blueprint.json"
OUTPUT_JSON = "generated_biology_paper.json"

def normalize_text(x):
    if pd.isna(x):
        return ""
    s = str(x).replace("\u00a0", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s

def load_blueprint(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_questions_csv(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")

def make_options(row):
    return [
        normalize_text(row.get("option_a", "")),
        normalize_text(row.get("option_b", "")),
        normalize_text(row.get("option_c", "")),
        normalize_text(row.get("option_d", ""))
    ]

def subject_match(series, target):
    s = series.astype(str).str.lower()
    return s.str.contains(target.lower(), na=False)

def build_section(df, subject, seed=42):
    sub = df[df["subject"].astype(str).str.lower().str.contains(subject.lower(), na=False)].copy()
    sub = sub.drop_duplicates(subset=["question"], keep="first")

    section = {
        "subject": subject,
        "total_questions": len(sub),
        "questions": []
    }

    sub = sub.sample(n=len(sub), random_state=seed) if len(sub) > 0 else sub

    for _, row in sub.iterrows():
        section["questions"].append({
            "question_no": normalize_text(row.get("question_no", "")),
            "page": normalize_text(row.get("page", "")),
            "question_type": normalize_text(row.get("question_type", "")),
            "question": normalize_text(row.get("question", "")),
            "options": make_options(row),
            "answer": normalize_text(row.get("answer", "")),
            "solution": normalize_text(row.get("solution", "")),
            "source_pdf": normalize_text(row.get("source_pdf", ""))
        })

    return section

def build_paper(blueprint, df):
    exam_id = normalize_text(blueprint.get("exam_id", EXAM_ID)).upper().replace(" ", "_").replace("-", "_")

    df = df.copy()
    df["exam_id"] = df["exam_id"].astype(str).str.strip().str.upper().str.replace(" ", "_", regex=False).str.replace("-", "_", regex=False)
    df["subject"] = df["subject"].astype(str).str.strip()

    exam_df = df[df["exam_id"] == exam_id].copy()

    paper = {
        "exam_id": exam_id,
        "paper_id": f"{exam_id}_001",
        "generated_at": datetime.now().isoformat(),
        "sections": []
    }

    for subject in ["Botany", "Zoology"]:
        subject_df = exam_df[subject_match(exam_df["subject"], subject)].copy()
        if len(subject_df) > 0:
            paper["sections"].append(build_section(subject_df, subject))

    return paper

def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    blueprint = load_blueprint(BLUEPRINT_JSON)
    if "exam_id" not in blueprint:
        blueprint["exam_id"] = EXAM_ID
    df = load_questions_csv(INPUT_CSV)
    paper = build_paper(blueprint, df)
    save_json(paper, OUTPUT_JSON)
    print(f"Saved: {OUTPUT_JSON}")