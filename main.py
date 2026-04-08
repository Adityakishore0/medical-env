"""
main.py — FastAPI server for Medical AI Doctor OpenEnv
Endpoints: /reset /step /state /health /cases /tasks
Run: uvicorn main:app --host 0.0.0.0 --port 7860
"""
from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException, Request
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
    return {"status": "healthy", "environment": "medical-ai-doctor-v1", "cases": ENV.case_count}


@app.get("/metadata")
def metadata():
    return {
        "name": "medical-ai-doctor",
        "version": "1.0.0",
        "description": (
            "Free AI Doctor for patients who cannot afford healthcare. "
            "Trains AI agents to conduct medical consultations — asking smart "
            "follow-up questions, assessing conditions from symptoms, and giving "
            "safe treatment advice while avoiding dangerous drug recommendations."
        ),
        "domain": "healthcare",
        "modality": "text",
        "real_world_task": True,
        "tasks": ["question_quality", "assessment", "safe_advice"],
    }


@app.get("/schema")
def schema():
    return {
        "action": {
            "variants": [
                {
                    "name": "QuestionQualityAction",
                    "task": "question_quality",
                    "fields": {
                        "action_type": "string",
                        "doctor_message": "string",
                        "questions_asked": "list[string]",
                        "reasoning": "string",
                    },
                },
                {
                    "name": "AssessmentAction",
                    "task": "assessment",
                    "fields": {
                        "action_type": "string",
                        "doctor_message": "string",
                        "primary_condition": "string",
                        "possible_conditions": "list[string]",
                        "confidence": "enum[low, moderate, high]",
                        "reasoning": "string",
                    },
                },
                {
                    "name": "SafeAdviceAction",
                    "task": "safe_advice",
                    "fields": {
                        "action_type": "string",
                        "doctor_message": "string",
                        "what_to_do": "list[string]",
                        "what_to_eat": "list[string]",
                        "medicines": "list[string]",
                        "what_to_avoid": "list[string]",
                        "go_to_hospital_if": "list[string]",
                        "contraindications_checked": "bool",
                        "reasoning": "string",
                    },
                },
            ]
        },
        "observation": {
            "fields": {
                "case_id": "string",
                "patient_age": "integer",
                "patient_sex": "enum[M, F, Other]",
                "language": "enum[en, hi]",
                "chief_complaint": "string",
                "conversation_history": "list[{role, content}]",
                "current_medications": "list[string]",
                "allergies": "list[string]",
                "task_type": "enum[question_quality, assessment, safe_advice]",
                "task_description": "string",
                "step_number": "integer",
            }
        },
        "state": {
            "fields": {
                "current_case": "Observation",
                "episode_step": "integer",
                "cumulative_reward": "float",
                "task_history": "list[string]",
            }
        },
    }


@app.post("/mcp")
async def mcp(request: Request):
    """JSON-RPC 2.0 MCP endpoint for tool-based access."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    method = body.get("method", "")
    req_id = body.get("id", 1)

    if method == "tools/list":
        result = {
            "tools": [
                {
                    "name": "reset",
                    "description": "Reset the environment and get a new patient case",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "case_id": {"type": "string", "description": "Optional specific case ID"},
                            "seed": {"type": "integer", "description": "Optional random seed"},
                        },
                    },
                },
                {
                    "name": "step",
                    "description": "Submit an action for the current patient case",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "object", "description": "Action dict for current task"},
                        },
                        "required": ["action"],
                    },
                },
                {
                    "name": "state",
                    "description": "Get the current environment state",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            ]
        }
    elif method == "tools/call":
        tool_name = body.get("params", {}).get("name", "")
        tool_args = body.get("params", {}).get("arguments", {})
        if tool_name == "reset":
            obs = ENV.reset(case_id=tool_args.get("case_id"))
            result = {"content": [{"type": "text", "text": obs.model_dump_json()}]}
        elif tool_name == "step":
            step_result = ENV.step(tool_args.get("action", {}))
            result = {"content": [{"type": "text", "text": step_result.model_dump_json()}]}
        elif tool_name == "state":
            state_result = ENV.state()
            result = {"content": [{"type": "text", "text": state_result.model_dump_json()}]}
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
    else:
        result = {"tools": [], "resources": [], "prompts": []}

    return {"jsonrpc": "2.0", "id": req_id, "result": result}


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
                "has_grader": True,
                "metric": "question_coverage_safety",
                "reward_range": [0.0, 1.0],
                "n_cases": 7,
            },
            {
                "id": "assessment",
                "name": "Condition Assessment",
                "difficulty": "medium",
                "description": "Based on conversation history, identify the most likely medical condition. Partial credit for reasonable differentials.",
                "grader": "env.tasks.task2_assessment.grade",
                "has_grader": True,
                "metric": "condition_accuracy_coverage",
                "reward_range": [0.0, 1.0],
                "n_cases": 7,
            },
            {
                "id": "safe_advice",
                "name": "Safe Treatment Advice",
                "difficulty": "hard",
                "description": "Give complete safe advice including medicines, diet, and hospital warnings. Heavy penalty for recommending dangerous or contraindicated medicines.",
                "grader": "env.tasks.task3_safe_advice.grade",
                "has_grader": True,
                "metric": "completeness_safety_contraindication",
                "reward_range": [0.0, 1.0],
                "n_cases": 6,
            },
        ],
        "total": 3,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
