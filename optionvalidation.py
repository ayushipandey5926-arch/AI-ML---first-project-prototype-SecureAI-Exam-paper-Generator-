import pandas as pd
import re

def norm(x):
    return "" if pd.isna(x) else re.sub(r"\s+", " ", str(x)).strip()

def validate_csv(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    df.columns = [norm(c) for c in df.columns]

    print("Rows:", len(df))
    print("Exam IDs:", sorted(set(df["exam_id"].map(norm))))
    print("Subjects:", sorted(set(df["subject"].map(norm))))
    print("Question types:", sorted(set(df["question_type"].map(norm))))
    print("Blank questions:", (df["question"].map(norm) == "").sum())
    print("Blank option_a:", (df["option_a"].map(norm) == "").sum())
    print("Blank option_b:", (df["option_b"].map(norm) == "").sum())
    print("Blank option_c:", (df["option_c"].map(norm) == "").sum())
    print("Blank option_d:", (df["option_d"].map(norm) == "").sum())

if __name__ == "__main__":
    validate_csv("cleaned_questions.csv")