import pandas as pd
import re
from pathlib import Path

INPUT_CSV = "questions.csv"
OUTPUT_CSV = "cleaned_questions.csv"

EXPECTED_COLS = [
    "exam_id", "source_pdf", "question_no", "page", "subject",
    "question_type", "question", "option_a", "option_b",
    "option_c", "option_d", "answer", "solution"
]

def normalize_text(x):
    if pd.isna(x):
        return ""
    s = str(x).replace("\u00a0", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s

def normalize_subject(s):
    s = normalize_text(s).lower()
    if "botany" in s:
        return "Botany"
    if "zoology" in s:
        return "Zoology"
    if "biology" in s:
        return "Biology"
    return normalize_text(s)

def normalize_exam_id(s):
    s = normalize_text(s)
    s = s.replace(" ", "_")
    s = s.replace("-", "_")
    return s.upper()

def row_quality_ok(row):
    needed = ["exam_id", "subject", "question", "option_a", "option_b", "option_c", "option_d"]
    for c in needed:
        if not normalize_text(row.get(c, "")):
            return False
    return True

def clean_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv, dtype=str, keep_default_na=False, encoding="utf-8", on_bad_lines="skip")
    df.columns = [normalize_text(c) for c in df.columns]

    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = ""

    df = df[EXPECTED_COLS].copy()

    for col in df.columns:
        df[col] = df[col].map(normalize_text)

    df["exam_id"] = df["exam_id"].map(normalize_exam_id)
    df["subject"] = df["subject"].map(normalize_subject)
    df["question_type"] = df["question_type"].str.lower().replace({"": "mcq"})

    df = df[df.apply(row_quality_ok, axis=1)].copy()
    df = df.drop_duplicates(subset=["exam_id", "subject", "question_no", "question"], keep="first")

    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    return df

if __name__ == "__main__":
    cleaned = clean_csv(INPUT_CSV, OUTPUT_CSV)
    print(f"Saved: {OUTPUT_CSV} | rows={len(cleaned)}")