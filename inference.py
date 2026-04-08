"""
inference.py — Medical AI Doctor Baseline Agent
================================================
Runs a free open-source LLM (BioMistral / Llama3 via HuggingFace)
against all 3 tasks in the Medical AI Doctor environment.

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
from openai import OpenAI
import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.3")
HF_TOKEN = os.getenv("HF_TOKEN", "")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
BENCHMARK = "medical-ai-doctor"

SYSTEM_PROMPT = """You are Dr. Arogya, a compassionate and experienced doctor who helps poor patients 
who cannot afford regular healthcare. You consult patients in both English and Hindi depending on their language.

Your approach:
- For question_quality task: Ask ONE clear follow-up question at a time. Focus on most clinically important aspects.
- For assessment task: Based on conversation, give your best assessment of what condition the patient has.
- For safe_advice task: Give complete safe advice — what to do, what to eat, which medicines are safe, what to avoid, and WHEN to go to hospital.

CRITICAL SAFETY RULES:
- NEVER recommend ibuprofen, diclofenac, aspirin or NSAIDs for stomach pain or gastritis
- NEVER recommend medicines the patient is allergic to
- ALWAYS tell patient when they need to go to hospital immediately
- ALWAYS add disclaimer that this is guidance not replacement for real doctor

You must respond ONLY with valid JSON. No extra text before or after the JSON.
"""


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    reward = max(0.001, min(0.999, float(reward)))
    error_val = error if error else "null"
    done_val = str(done).lower()
    action_short = action[:80].replace("\n", " ")
    print(f"[STEP] step={step} action={action_short} reward={reward:.3f} done={done_val} error={error_val}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    score = max(0.001, min(0.999, float(score)))
    rewards = [max(0.001, min(0.999, float(r))) for r in rewards]
    rewards_str = ",".join(f"{r:.3f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def get_action_for_task(client: OpenAI, observation: dict, task_type: str) -> dict:
    """Use LLM to generate appropriate action for each task type."""

    complaint = observation.get("chief_complaint", "")
    age = observation.get("patient_age", 0)
    sex = observation.get("patient_sex", "M")
    language = observation.get("language", "en")
    medications = observation.get("current_medications", [])
    allergies = observation.get("allergies", [])
    history = observation.get("conversation_history", [])

    history_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history])

    lang_instruction = "Respond in Hindi if the patient wrote in Hindi, otherwise in English."

    if task_type == "question_quality":
        user_prompt = f"""Patient details:
Age: {age}, Sex: {sex}
Chief complaint: {complaint}
Medications: {medications}
Allergies: {allergies}
Conversation so far:
{history_text}

{lang_instruction}

Task: Ask the single most important follow-up question to better understand this patient's condition.
Think about what a real doctor would ask first.

Respond with ONLY this JSON:
{{
  "action_type": "question_quality",
  "doctor_message": "Your question to the patient here",
  "questions_asked": ["topic you are asking about"],
  "reasoning": "Why this question is most important"
}}"""

    elif task_type == "assessment":
        user_prompt = f"""Patient details:
Age: {age}, Sex: {sex}
Chief complaint: {complaint}
Medications: {medications}
Allergies: {allergies}
Conversation so far:
{history_text}

{lang_instruction}

Task: Based on the conversation, assess the most likely medical condition.

Respond with ONLY this JSON:
{{
  "action_type": "assessment",
  "doctor_message": "Your assessment message to patient in their language",
  "primary_condition": "Most likely condition",
  "possible_conditions": ["condition 2", "condition 3"],
  "confidence": "moderate",
  "reasoning": "Clinical reasoning for this assessment"
}}"""

    else:  # safe_advice
        user_prompt = f"""Patient details:
Age: {age}, Sex: {sex}
Chief complaint: {complaint}
Current medications: {medications}
Allergies: {allergies}
Conversation so far:
{history_text}

{lang_instruction}

Task: Give complete safe treatment advice. 
IMPORTANT: Check medications and allergies carefully before recommending anything.
For emergencies tell patient to go to hospital IMMEDIATELY.

Respond with ONLY this JSON:
{{
  "action_type": "safe_advice",
  "doctor_message": "Your complete advice message to patient in their language",
  "what_to_do": ["step 1", "step 2"],
  "what_to_eat": ["food 1", "food 2"],
  "medicines": ["safe medicine 1", "safe medicine 2"],
  "what_to_avoid": ["avoid 1", "avoid 2"],
  "go_to_hospital_if": ["warning sign 1", "warning sign 2"],
  "contraindications_checked": true,
  "reasoning": "Why this advice is safe for this patient"
}}"""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=800,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()

        # Clean up JSON if model added extra text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        return json.loads(text)

    except json.JSONDecodeError:
        # Fallback actions if model doesn't return valid JSON
        if task_type == "question_quality":
            return {
                "action_type": "question_quality",
                "doctor_message": f"How long have you been experiencing {complaint}? Do you have any fever or vomiting?",
                "questions_asked": ["duration", "fever", "vomiting"],
                "reasoning": "Fallback: asking basic triage questions"
            }
        elif task_type == "assessment":
            return {
                "action_type": "assessment",
                "doctor_message": f"Based on your symptoms of {complaint}, I need you to consult a doctor for proper diagnosis.",
                "primary_condition": "requires medical evaluation",
                "possible_conditions": ["viral infection", "stress related"],
                "confidence": "low",
                "reasoning": "Fallback: insufficient information for assessment"
            }
        else:
            return {
                "action_type": "safe_advice",
                "doctor_message": "Please rest, drink plenty of water, and consult a doctor for proper treatment. Do not self medicate.",
                "what_to_do": ["rest", "drink plenty of water", "consult a doctor"],
                "what_to_eat": ["light food", "plenty of fluids"],
                "medicines": ["paracetamol 500mg for fever or pain if not allergic"],
                "what_to_avoid": ["self medication without advice"],
                "go_to_hospital_if": ["symptoms worsen", "high fever", "severe pain", "difficulty breathing"],
                "contraindications_checked": True,
                "reasoning": "Fallback safe generic advice"
            }
    except Exception as exc:
        raise exc


def run_episode(client: httpx.Client, llm_client: OpenAI, case_id: Optional[str], task_filter: Optional[str]) -> tuple[float, bool, List[float]]:
    """Run one patient episode. Returns (score, success, rewards)."""

    # Reset
    reset_body = {}
    if case_id:
        reset_body["case_id"] = case_id
    r = client.post("/reset", json=reset_body)
    r.raise_for_status()
    observation = r.json()
    task_type = observation.get("task_type", "")

    if task_filter and task_type != task_filter:
        return 0.0, False, []

    # Get action from LLM
    action = get_action_for_task(llm_client, observation, task_type)

    # Step
    r = client.post("/step", json={"action": action})
    r.raise_for_status()
    result = r.json()

    reward_total = result.get("reward", {}).get("total", 0.001)
    reward_total = max(0.001, min(0.999, float(reward_total)))
    done = result.get("done", True)
    is_safe = result.get("reward", {}).get("is_safe", True)

    return reward_total, is_safe, [reward_total]


def main():
    parser = argparse.ArgumentParser(description="Medical AI Doctor — Baseline Inference")
    parser.add_argument("--task", default=None, help="Filter by task type")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--n", type=int, default=20, help="Number of cases to run")
    args = parser.parse_args()

    llm_client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "dummy")
    http_client = httpx.Client(base_url=ENV_BASE_URL, timeout=30.0)

    task_label = args.task or "all"
    log_start(task=task_label, env=BENCHMARK, model=MODEL_NAME)

    all_rewards: List[float] = []
    all_scores: List[float] = []
    safe_count = 0
    step_num = 0
    start_time = time.time()

    # Reset env with seed
    http_client.post("/reset", json={"seed": args.seed})

    # Get all cases
    cases_resp = http_client.get("/cases")
    cases = cases_resp.json().get("cases", [])
    cases_to_run = cases[:args.n]

    for case_info in cases_to_run:
        case_id = case_info["case_id"]
        step_num += 1
        error_msg = None

        try:
            score, is_safe, rewards = run_episode(http_client, llm_client, case_id, args.task)
            if not rewards:
                continue
            all_rewards.extend(rewards)
            all_scores.append(score)
            if is_safe:
                safe_count += 1
            log_step(step=step_num, action=f"case={case_id}", reward=score, done=True, error=None)
        except Exception as e:
            error_msg = str(e)[:100]
            all_scores.append(0.001)
            log_step(step=step_num, action=f"case={case_id}", reward=0.001, done=True, error=error_msg)

    elapsed = round(time.time() - start_time, 1)
    final_score = sum(all_scores) / max(len(all_scores), 1)
    final_score = max(0.001, min(0.999, final_score))
    success = final_score >= 0.4

    print(f"[INFO] elapsed={elapsed}s cases={len(all_scores)} safe_rate={safe_count/max(len(all_scores),1):.2f}", flush=True)
    log_end(success=success, steps=step_num, score=final_score, rewards=all_rewards)

    http_client.close()


if __name__ == "__main__":
    main()
