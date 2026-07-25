import json

Exam_registry = {
    "NEET_UG_2027": {
        "exam_name": "National Eligibility Entrance Test (UG) 2027",
        "exam_id": "NEET",
        "mode": "CBT",
        "question_type": "MCQ",
        "exam_duration_minutes": 180,
        "total_questions": 180,
        "subjects": [
            {
                "subject_id": "PHY",
                "subject_name": "Physics",
                "sections": [
                    {"section_id": "Section_A", "target_questions": 35, "max_hard": 5},
                    {"section_id": "Section_B", "target_questions": 10, "max_hard": 5}
                ]
            },
            {
                "subject_id": "CHEM",
                "subject_name": "Chemistry",
                "sections": [
                    {"section_id": "Section_A", "target_questions": 35, "max_hard": 5},
                    {"section_id": "Section_B", "target_questions": 10, "max_hard": 5}
                ]
            },
            {
                "subject_id": "BIO",
                "subject_name": "Biology",
                "sections": [
                    {"section_id": "Botany", "target_questions": 45, "max_hard": 10},
                    {"section_id": "Zoology", "target_questions": 45, "max_hard": 10}
                ]
            }
        ],
        "marks_per_question": 4,
        "negative_marks_per_question": -1,
        "unanswered_question": 0,
        "total_marks": 720,
        "language": ["English", "Hindi"],
        "rules": {
            "easy": 0.3,
            "medium": 0.5,
            "hard": 0.2
        }
    },

    "JEE_Main_2027": {
        "exam_name": "Joint Entrance Exam (Main) 2027",
        "exam_id": "JEE",
        "mode": "CBT",
        "question_type": "MCQ + Numerical",
        "exam_duration_minutes": 180,
        "total_questions": 90,
        "subjects": [
            {
                "subject_id": "PHY",
                "subject_name": "Physics",
                "sections": [
                    {"section_id": "MCQ", "target_questions": 20, "max_hard": 5, "negative_marks": -1},
                    {"section_id": "Numerical", "target_questions": 5, "max_hard": 2, "negative_marks": 0}
                ]
            },
            {
                "subject_id": "CHEM",
                "subject_name": "Chemistry",
                "sections": [
                    {"section_id": "MCQ", "target_questions": 20, "max_hard": 5, "negative_marks": -1},
                    {"section_id": "Numerical", "target_questions": 5, "max_hard": 2, "negative_marks": 0}
                ]
            },
            {
                "subject_id": "MAT",
                "subject_name": "Mathematics",
                "sections": [
                    {"section_id": "MCQ", "target_questions": 20, "max_hard": 5, "negative_marks": -1},
                    {"section_id": "Numerical", "target_questions": 5, "max_hard": 2, "negative_marks": 0}
                ]
            }
        ],
        "marks_per_question": 4,
        "negative_marks_per_question": -1,
        "unanswered_question": 0,
        "total_marks": 360,
        "language": ["English", "Hindi"],
        "rules": {
            "easy": 0.3,
            "medium": 0.5,
            "hard": 0.2
        }
    },

    "CUET_2027": {
        "exam_name": "Common University Entrance Test (UG) 2027",
        "exam_id": "CUET",
        "mode": "CBT",
        "question_type": "MCQ",
        "exam_duration_minutes": 180,
        "total_questions": 150,
        "subjects": [
            {
                "subject_id": "LANG",
                "subject_name": "Language",
                "sections": [
                    {"section_id": "Section_A", "target_questions": 50, "max_hard": 10}
                ]
            },
            {
                "subject_id": "GEN",
                "subject_name": "General Test",
                "sections": [
                    {"section_id": "Section_A", "target_questions": 50, "max_hard": 10}
                ]
            },
            {
                "subject_id": "DOM",
                "subject_name": "Domain Subjects",
                "sections": [
                    {"section_id": "Section_A", "target_questions": 50, "max_hard": 10}
                ]
            }
        ],
        "marks_per_question": 4,
        "negative_marks_per_question": -1,
        "unanswered_question": 0,
        "total_marks": 600,
        "language": ["English", "Hindi"],
        "rules": {
            "easy": 0.3,
            "medium": 0.5,
            "hard": 0.2
        }
    }
}

with open("Exam_registry.json", "w", encoding="utf-8") as file:
    json.dump(Exam_registry, file, indent=4, ensure_ascii=False)