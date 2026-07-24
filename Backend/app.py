from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph_selector import app as selector_app
from langgraph_selector import PAPER_DATA

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PaperRequest(BaseModel):
    examType: str
    topic: str = "biology"
    difficulty: str = "medium"
    numQuestions: int = 10

@app.post("/generate-paper")
async def generate_paper(req: PaperRequest):
    result = selector_app.invoke({
        "topic": req.topic,
        "difficulty": req.difficulty,
        "num_questions": req.numQuestions,
        "all_questions": [],
        "selected_questions": []
    })

    return {
        "exam_id": PAPER_DATA.get("exam_id", ""),
        "paper_id": "AI_SELECTED_001",
        "questions": result["selected_questions"]
    }