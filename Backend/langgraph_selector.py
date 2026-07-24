from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from functools import lru_cache
import json
from pathlib import Path

class State(TypedDict):
    topic: str
    difficulty: str
    num_questions: int
    all_questions: list
    selected_questions: list

BASE_DIR = Path(__file__).resolve().parent
PAPER_FILE = BASE_DIR.parent / "generated_biology_paper.json"

with open(PAPER_FILE, "r", encoding="utf-8") as f:
    PAPER_DATA = json.load(f)

def flatten_questions(data):
    items = []
    for section in data.get("sections", []):
        subject = section.get("subject", "")
        for q in section.get("questions", []):
            items.append({
                "subject": subject,
                "question_no": q.get("question_no", ""),
                "page": q.get("page", ""),
                "question": q.get("question", ""),
                "options": q.get("options", []),
                "answer": q.get("answer", ""),
            })
    return items

ALL_QUESTIONS = flatten_questions(PAPER_DATA)

@lru_cache(maxsize=128)
def ranked_cache(topic, difficulty, num_questions):
    ranked = []
    t = topic.lower()
    d = difficulty.lower()
    for q in ALL_QUESTIONS:
        text = (q["question"] + " " + " ".join(q["options"])).lower()
        score = 0
        if t in text:
            score += 2
        if d in text:
            score += 1
        if q.get("answer"):
            score += 1
        ranked.append({**q, "score": score})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[:num_questions]

def load_questions(state: State):
    return {"all_questions": ALL_QUESTIONS}

def select_questions(state: State):
    selected = ranked_cache(state["topic"], state["difficulty"], state["num_questions"])
    return {"selected_questions": selected}

graph = StateGraph(State)
graph.add_node("load_questions", load_questions)
graph.add_node("select_questions", select_questions)
graph.add_edge(START, "load_questions")
graph.add_edge("load_questions", "select_questions")
graph.add_edge("select_questions", END)

app = graph.compile()