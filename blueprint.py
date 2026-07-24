import json

def build_blueprint(exam_id: str, exam_registry: dict) -> dict:
    if exam_id not in exam_registry:
        raise ValueError(f"Exam_id '{exam_id}' not found in the registry.")

    pattern = exam_registry[exam_id]

    blueprint = {
        "exam_id": pattern.get("exam_id", exam_id),
        "exam_name": pattern.get("exam_name"),
        "mode": pattern.get("mode"),
        "question_type": pattern.get("question_type"),
        "exam_duration_minutes": pattern.get("exam_duration_minutes"),
        "total_questions": pattern.get("total_questions"),
        "subjects": [],
        "marks_per_question": pattern.get("marks_per_question"),
        "negative_marks_per_question": pattern.get("negative_marks_per_question"),
        "unanswered_question": pattern.get("unanswered_question"),
        "total_marks": pattern.get("total_marks"),
        "language": pattern.get("language"),
        "rules": pattern.get("rules", {})
    }

    for subject in pattern.get("subjects", []):
        subject_entry = {
            "subject_id": subject.get("subject_id"),
            "subject_name": subject.get("subject_name"),
            "sections": []
        }

        for section in subject.get("sections", []):
            section_entry = {
                "section_id": section.get("section_id"),
                "target_questions": section.get("target_questions"),
                "max_hard": section.get("max_hard")
            }

            if "negative_marks" in section:
                section_entry["negative_marks"] = section.get("negative_marks")

            if "difficulty_mix" in section:
                section_entry["difficulty_mix"] = section.get("difficulty_mix")

            subject_entry["sections"].append(section_entry)

        blueprint["subjects"].append(subject_entry)

    return blueprint


with open("Exam_registry.json", "r", encoding="utf-8") as file:
    Exam_registry = json.load(file)

exam_ids = ["NEET_UG_2027", "JEE_Main_2027", "CUET_2027"]

all_blueprints = {}

for exam_id in exam_ids:
    if exam_id in Exam_registry:
        all_blueprints[exam_id] = build_blueprint(exam_id, Exam_registry)

with open("blueprint.json", "w", encoding="utf-8") as file:
    json.dump(all_blueprints, file, indent=4, ensure_ascii=False)