"""
inference.py — Medical AI Doctor Baseline Agent
================================================
Runs a free open-source LLM against all 3 tasks in the Medical AI Doctor
environment.  Emits one [START]…[END] episode block per task so the
hackathon validator can confirm that each grader produces a score in [0,1].

Required env vars:
  API_BASE_URL  — HuggingFace or compatible endpoint
  MODEL_NAME    — Model identifier
  HF_TOKEN      — Your HuggingFace token

Run:
  python inference.py
  python inference.py --task question_quality
  python inference.py --seed 42
"""

from __future__ import annotations
import argparse
import json
import os
import time
from typing import Optional, List

import httpx
from openai import OpenAI

# ── env vars ──────────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "mistralai/Mistral-7B-Instruct-v0.3")
HF_TOKEN     = os.getenv("HF_TOKEN",     "")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
BENCHMARK    = "medical-ai-doctor"

# All three tasks the validator must see individually
ALL_TASKS = ["question_quality", "assessment", "safe_advice"]

SYSTEM_PROMPT = """You are Dr. Arogya, a compassionate doctor who helps poor patients.
CRITICAL SAFETY RULES:
- NEVER recommend ibuprofen/NSAIDs for stomach pain
- NEVER recommend medicines the patient is allergic to
- ALWAYS include when to go to hospital
- ALWAYS add disclaimer this is guidance not replacement for real doctor
You must respond ONLY with valid JSON. No extra text.
"""


# ── logging helpers ────────────────────────────────────────────────────────────
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    reward    = max(0.00, min(1.00, float(reward)))
    error_val = error if error else "null"
    done_val  = str(done).lower()
    action_short = action[:80].replace("\n", " ")
    print(
        f"[STEP] step={step} action={action_short} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    score       = max(0.00, min(1.00, float(score)))
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# ── LLM action generation ─────────────────────────────────────────────────────
def get_action_for_task(client: OpenAI, observation: dict, task_type: str) -> dict:
    complaint   = observation.get("chief_complaint", "")
    age         = observation.get("patient_age", 0)
    sex         = observation.get("patient_sex", "M")
    medications = observation.get("current_medications", [])
    allergies   = observation.get("allergies", [])
    history     = observation.get("conversation_history", [])
    history_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history])

    if task_type == "question_quality":
        user_prompt = f"""Patient: Age {age}, Sex {sex}, Complaint: {complaint}
Medications: {medications} | Allergies: {allergies}
Conversation:\n{history_text}

Ask the single most important follow-up question.
Respond ONLY with this JSON:
{{"action_type":"question_quality","doctor_message":"Your question","questions_asked":["topic"],"reasoning":"why"}}"""

    elif task_type == "assessment":
        user_prompt = f"""Patient: Age {age}, Sex {sex}, Complaint: {complaint}
Medications: {medications} | Allergies: {allergies}
Conversation:\n{history_text}

Assess the most likely condition.
Respond ONLY with this JSON:
{{"action_type":"assessment","doctor_message":"Your assessment","primary_condition":"condition","possible_conditions":["alt1","alt2"],"confidence":"moderate","reasoning":"why"}}"""

    else:  # safe_advice
        user_prompt = f"""Patient: Age {age}, Sex {sex}, Complaint: {complaint}
Medications: {medications} | Allergies: {allergies}
Conversation:\n{history_text}

Give complete safe treatment advice. Check allergies carefully.
Respond ONLY with this JSON:
{{"action_type":"safe_advice","doctor_message":"Your advice","what_to_do":["step1"],"what_to_eat":["food1"],"medicines":["safe med"],"what_to_avoid":["avoid1"],"go_to_hospital_if":["sign1","sign2"],"contraindications_checked":true,"reasoning":"why safe"}}"""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=600,
        )
        text = (completion.choices[0].message.content or "").strip()
        for marker in ["```json", "```"]:
            if marker in text:
                text = text.split(marker)[1].split("```")[0].strip()
                break
        return json.loads(text)
    except Exception:
        return _fallback_action(task_type, complaint)


def _fallback_action(task_type: str, complaint: str) -> dict:
    if task_type == "question_quality":
        return {"action_type":"question_quality","doctor_message":f"How long have you had {complaint}? Any fever?","questions_asked":["duration","fever"],"reasoning":"basic triage"}
    elif task_type == "assessment":
        return {"action_type":"assessment","doctor_message":"Please consult a doctor for proper diagnosis.","primary_condition":"requires evaluation","possible_conditions":["viral","stress"],"confidence":"low","reasoning":"insufficient info"}
    else:
        return {"action_type":"safe_advice","doctor_message":"Rest, drink water, consult a doctor. Do not self-medicate.","what_to_do":["rest","hydrate","see doctor"],"what_to_eat":["light food","fluids"],"medicines":["paracetamol 500mg if not allergic"],"what_to_avoid":["self medication"],"go_to_hospital_if":["worsening","high fever","severe pain","difficulty breathing"],"contraindications_checked":True,"reasoning":"generic safe advice"}


# ── single task episode ────────────────────────────────────────────────────────
def run_task_episode(
    http_client: httpx.Client,
    llm_client:  OpenAI,
    task_name:   str,
    seed:        int,
) -> None:
    """
    Run one complete episode for a single task type.
    Emits exactly one [START]...[STEP]...[END] block.
    The validator checks each task's score independently.
    """
    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    rewards:  List[float] = []
    step_num  = 0
    score     = 0.001
    success   = False

    try:
        # Seed for reproducibility
        http_client.post("/reset", json={"seed": seed})

        # Find a case of the right task type
        cases_resp = http_client.get("/cases")
        cases      = cases_resp.json().get("cases", [])
        task_cases = [c for c in cases if c.get("task_type") == task_name]

        if not task_cases:
            log_step(step=1, action="no_case_found", reward=0.001, done=True,
                     error=f"no cases for task={task_name}")
            log_end(success=False, steps=1, score=0.001, rewards=[0.001])
            return

        case_id = task_cases[0]["case_id"]

        # Reset to this specific case
        r = http_client.post("/reset", json={"case_id": case_id})
        r.raise_for_status()
        observation = r.json()

        # LLM generates action
        action = get_action_for_task(llm_client, observation, task_name)

        # Environment step — grader runs here
        r = http_client.post("/step", json={"action": action})
        r.raise_for_status()
        result = r.json()

        reward = float(result.get("reward", {}).get("total", 0.001))
        reward = max(0.00, min(1.00, reward))
        done   = bool(result.get("done", True))

        step_num = 1
        rewards.append(reward)
        score    = reward
        success  = score >= 0.30

        action_str = action.get("doctor_message", str(action))[:80].replace("\n", " ")
        log_step(step=step_num, action=action_str, reward=reward, done=done, error=None)

    except Exception as exc:
        step_num = max(step_num, 1)
        rewards  = rewards or [0.001]
        score    = 0.001
        log_step(step=step_num, action="error", reward=0.001, done=True, error=str(exc)[:100])

    finally:
        log_end(success=success, steps=step_num, score=score, rewards=rewards)


# ── main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Medical AI Doctor — Baseline Inference")
    parser.add_argument("--task", default=None,
                        help="Run only one task. Default: run all three.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    llm_client  = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "dummy")
    http_client = httpx.Client(base_url=ENV_BASE_URL, timeout=30.0)

    tasks_to_run = [args.task] if args.task else ALL_TASKS

    try:
        for task_name in tasks_to_run:
            run_task_episode(http_client, llm_client, task_name, seed=args.seed)
    finally:
        http_client.close()


if __name__ == "__main__":
    main()
