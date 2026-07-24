from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from pathlib import Path
import pandas as pd

class State(TypedDict):
    question: str
    topic: str
    difficulty: str
    watson_context: str
    validated: bool
    mcq: dict
    output: dict

def tag_topic(state: State):
    q = state["question"].lower()
    if "plant" in q or "flower" in q or "botany" in q:
        return {"topic": "Botany"}
    if "animal" in q or "zoology" in q:
        return {"topic": "Zoology"}
    return {"topic": "General Biology"}

def score_difficulty(state: State):
    q = state["question"]
    if len(q) > 180:
        diff = "hard"
    elif len(q) > 90:
        diff = "medium"
    else:
        diff = "easy"
    return {"difficulty": diff}

def mock_watson_node(state: State):
    context = f"Mock Watson context for {state['topic']}: focus on definitions, key facts, and figure clues."
    return {"watson_context": context}

def validate_node(state: State):
    ok = bool(state["question"].strip()) and bool(state["topic"].strip())
    return {"validated": ok}

def route_by_difficulty(state: State):
    if state["difficulty"] == "hard":
        return "hard"
    elif state["difficulty"] == "medium":
        return "medium"
    return "easy"

def generate_mcq_easy(state: State):
    return {
        "mcq": {
            "stem": state["question"],
            "options": {
                "A": "Correct easy answer",
                "B": "Distractor 1",
                "C": "Distractor 2",
                "D": "Distractor 3",
            },
            "answer": "A",
            "explanation": f"Easy-level clue from {state['watson_context']}",
        }
    }

def generate_mcq_medium(state: State):
    return {
        "mcq": {
            "stem": state["question"],
            "options": {
                "A": "Correct medium answer",
                "B": "Distractor 1",
                "C": "Distractor 2",
                "D": "Distractor 3",
            },
            "answer": "A",
            "explanation": f"Medium-level clue from {state['watson_context']}",
        }
    }

def review_hard_node(state: State):
    return {
        "mcq": {
            "stem": state["question"],
            "options": {
                "A": "Correct hard answer",
                "B": "Distractor 1",
                "C": "Distractor 2",
                "D": "Distractor 3",
            },
            "answer": "A",
            "explanation": f"Hard-level review based on {state['watson_context']}",
        }
    }

def export_node(state: State):
    return {
        "output": {
            "question": state["question"],
            "topic": state["topic"],
            "difficulty": state["difficulty"],
            "watson_context": state["watson_context"],
            "validated": state["validated"],
            "options": state["mcq"]["options"],
            "answer": state["mcq"]["answer"],
            "explanation": state["mcq"]["explanation"],
        }
    }

graph = StateGraph(State)
graph.add_node("tag_topic", tag_topic)
graph.add_node("score_difficulty", score_difficulty)
graph.add_node("mock_watson_node", mock_watson_node)
graph.add_node("validate_node", validate_node)
graph.add_node("generate_mcq_easy", generate_mcq_easy)
graph.add_node("generate_mcq_medium", generate_mcq_medium)
graph.add_node("review_hard_node", review_hard_node)
graph.add_node("export_node", export_node)

graph.add_edge(START, "tag_topic")
graph.add_edge("tag_topic", "score_difficulty")
graph.add_edge("score_difficulty", "mock_watson_node")
graph.add_edge("mock_watson_node", "validate_node")

graph.add_conditional_edges(
    "validate_node",
    route_by_difficulty,
    {
        "easy": "generate_mcq_easy",
        "medium": "generate_mcq_medium",
        "hard": "review_hard_node",
    }
)

graph.add_edge("generate_mcq_easy", "export_node")
graph.add_edge("generate_mcq_medium", "export_node")
graph.add_edge("review_hard_node", "export_node")
graph.add_edge("export_node", END)

app = graph.compile()

base_dir = Path(r"C:\Users\HP\OneDrive\Desktop\SecureAI Exam paper Generator\AI")
csv_path = base_dir / "input_questions.csv"
output_dir = base_dir / "output"
output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(csv_path)
results = []

for _, row in df.iterrows():
    q = str(row["question"])
    result = app.invoke({
        "question": q,
        "topic": "",
        "difficulty": "",
        "watson_context": "",
        "validated": False,
        "mcq": {},
        "output": {}
    })
    results.append(result["output"])

out_df = pd.DataFrame(results)
out_df.to_csv(output_dir / "routed_mcq_results.csv", index=False)
print("Saved to output/routed_mcq_results.csv")