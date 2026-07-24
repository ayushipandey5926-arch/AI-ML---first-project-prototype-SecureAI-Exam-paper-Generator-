import json
import pandas as pd
from pathlib import Path

json_files = [
    Path("neet_question_bank.json"),
]

rows = []

for jf in json_files:
    with open(jf, "r", encoding="utf-8") as file:
        data = json.load(file)

    exam_id = data.get("exam_id", "")
    source_pdf = data.get("source_pdf", "")
    questions = data.get("questions", [])

    for q in questions:
        opts = q.get("options", {})
        rows.append({
            "exam_id": exam_id,
            "source_pdf": source_pdf,
            "question_no": q.get("question_no", ""),
            "page": q.get("page", ""),
            "subject": q.get("subject", ""),
            "question_type": q.get("question_type", ""),
            "question": q.get("question", ""),
            "option_a": opts.get("a", ""),
            "option_b": opts.get("b", ""),
            "option_c": opts.get("c", ""),
            "option_d": opts.get("d", ""),
            "answer": q.get("answer", ""),
            "solution": q.get("solution", "")
        })

df = pd.DataFrame(rows)
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
df.to_csv(output_dir / "all_questions.csv", index=False, encoding="utf-8-sig")
print("CSV saved")