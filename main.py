"""
main.py — FastAPI server for Medical AI Doctor OpenEnv
Endpoints: /reset /step /state /health /cases /tasks
Run: uvicorn main:app --host 0.0.0.0 --port 7860
"""
from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from env.environment import MedicalAIDoctorEnvironment
from env.models import StepResponse, StateResponse, Observation

app = FastAPI(
    title="Medical AI Doctor — Free Healthcare for Everyone",
    description="OpenEnv-compliant AI doctor environment. Trains AI to ask smart questions, assess conditions, and give safe advice to patients who cannot afford healthcare.",
    version="1.0.0",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

ENV = MedicalAIDoctorEnvironment(seed=42)


class ResetRequest(BaseModel):
    case_id: Optional[str] = None
    seed: Optional[int] = None


class StepRequest(BaseModel):
    action: dict


@app.get("/health")
def health():
    return {"status": "ok", "environment": "medical-ai-doctor-v1", "cases": ENV.case_count}


@app.post("/reset", response_model=Observation)
def reset(req: ResetRequest = ResetRequest()):
    global ENV
    if req.seed is not None:
        ENV = MedicalAIDoctorEnvironment(seed=req.seed)
    try:
        return ENV.reset(case_id=req.case_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/step", response_model=StepResponse)
def step(req: StepRequest):
    try:
        return ENV.step(req.action)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid action: {e}")


@app.get("/state", response_model=StateResponse)
def state():
    try:
        return ENV.state()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/cases")
def list_cases():
    return {"cases": ENV.list_cases(), "total": ENV.case_count}


@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {
                "id": "question_quality",
                "name": "Smart Question Asking",
                "difficulty": "easy",
                "description": "Given a patient complaint, ask the right follow-up questions like a real doctor. Score based on completeness and relevance of questions.",
                "grader": "env.tasks.task1_question_quality.grade",
                "metric": "question_coverage_safety",
                "reward_range": [0.0, 1.0],
            },
            {
                "id": "assessment",
                "name": "Condition Assessment",
                "difficulty": "medium",
                "description": "Based on conversation history, identify the most likely medical condition. Partial credit for reasonable differentials.",
                "grader": "env.tasks.task2_assessment.grade",
                "metric": "condition_accuracy_coverage",
                "reward_range": [0.0, 1.0],
            },
            {
                "id": "safe_advice",
                "name": "Safe Treatment Advice",
                "difficulty": "hard",
                "description": "Give complete safe advice including medicines, diet, and hospital warnings. Heavy penalty for recommending dangerous or contraindicated medicines.",
                "grader": "env.tasks.task3_safe_advice.grade",
                "metric": "completeness_safety_contraindication",
                "reward_range": [0.0, 1.0],
            },
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
