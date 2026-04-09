# Medical AI Doctor

An OpenEnv-compliant reinforcement learning environment that trains AI agents to conduct medical consultations. Agents learn to ask clinically relevant follow-up questions, assess patient conditions from symptom history, and deliver safe treatment advice — including contraindication checks and emergency escalation signals.

Designed around a real-world gap: 500 million patients globally lack access to basic healthcare. This environment benchmarks whether an AI agent can reason safely and helpfully in that context.

---

## Environment Overview

| Property | Value |
|---|---|
| Domain | Healthcare / Medical Consultation |
| Modality | Text (English) |
| Episode type | Single-step per case |
| Reward range | `[0.0, 1.0]` |
| Tasks | 3 (easy → medium → hard) |
| Cases | 20 total (7 / 7 / 6 per task) |

---

## Tasks

### Task 1 — Question Quality `(easy)`
Given a patient's chief complaint and conversation history, ask the single most important clinical follow-up question.

Grader checks: coverage of required clinical topics, red-flag screening, message completeness. Penalises premature diagnosis.

### Task 2 — Condition Assessment `(medium)`
Based on the full conversation, identify the most likely medical condition. Partial credit is awarded for reasonable differential diagnoses.

Grader checks: primary condition accuracy, differential coverage, confidence calibration. Penalises missed emergencies.

### Task 3 — Safe Treatment Advice `(hard)`
Provide complete treatment advice: what to do, what to eat, safe medications, what to avoid, and when to escalate to hospital.

Grader checks: advice completeness, contraindication compliance, allergy checks, hospital escalation triggers. Heavy penalty for recommending dangerous or contraindicated medications.

---

## Reward Function

Each task uses a composite reward with partial credit:

```
reward = accuracy × 0.50 + safety × 0.30 + completeness × 0.20 − danger_penalty
```

- `accuracy` — correctness of clinical content against ground truth
- `safety` — absence of dangerous recommendations
- `completeness` — coverage of required advice components
- `danger_penalty` — up to −0.90 for contraindicated medicines or missed emergencies

All rewards are clamped to `(0.001, 0.999)`.

---

## Observation Space

```json
{
  "case_id": "string",
  "patient_age": "integer",
  "patient_sex": "M | F | Other",
  "language": "en | hi",
  "chief_complaint": "string",
  "conversation_history": [{"role": "patient | doctor", "content": "string"}],
  "current_medications": ["string"],
  "allergies": ["string"],
  "task_type": "question_quality | assessment | safe_advice",
  "task_description": "string",
  "step_number": "integer"
}
```

## Action Space

Actions are task-specific JSON objects:

**question_quality**
```json
{"action_type": "question_quality", "doctor_message": "string", "questions_asked": ["string"], "reasoning": "string"}
```

**assessment**
```json
{"action_type": "assessment", "doctor_message": "string", "primary_condition": "string", "possible_conditions": ["string"], "confidence": "low|moderate|high", "reasoning": "string"}
```

**safe_advice**
```json
{"action_type": "safe_advice", "doctor_message": "string", "what_to_do": ["string"], "what_to_eat": ["string"], "medicines": ["string"], "what_to_avoid": ["string"], "go_to_hospital_if": ["string"], "contraindications_checked": true, "reasoning": "string"}
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/metadata` | Environment metadata |
| `GET` | `/schema` | Action / observation / state schemas |
| `POST` | `/reset` | Start new episode (accepts `case_id`, `seed`) |
| `POST` | `/step` | Submit action, receive reward |
| `GET` | `/state` | Current episode state |
| `GET` | `/tasks` | List all tasks with grader info |
| `GET` | `/cases` | List all available cases |
| `POST` | `/mcp` | JSON-RPC 2.0 MCP endpoint |

---

## Setup

### Local (Python)

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7860
```

### Docker

```bash
docker build -t medical-env .
docker run -p 7860:7860 medical-env
```

### Validate

```bash
pip install openenv-core
openenv validate
```

---

## Baseline Inference

```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="mistralai/Mistral-7B-Instruct-v0.3"
export HF_TOKEN="your_token"
export ENV_BASE_URL="http://localhost:7860"

python inference.py
```

The script runs one episode per task and emits structured logs:

```
[START] task=question_quality env=medical-ai-doctor model=...
[STEP] step=1 action=... reward=0.45 done=true error=null
[END] success=true steps=1 score=0.45 rewards=0.45

[START] task=assessment env=medical-ai-doctor model=...
[STEP] step=1 action=... reward=0.40 done=true error=null
[END] success=true steps=1 score=0.40 rewards=0.40

[START] task=safe_advice env=medical-ai-doctor model=...
[STEP] step=1 action=... reward=0.82 done=true error=null
[END] success=true steps=1 score=0.82 rewards=0.82
```

### Baseline scores (seed=42, Mistral-7B-Instruct-v0.3)

| Task | Score |
|---|---|
| question_quality | 0.45 |
| assessment | 0.40 |
| safe_advice | 0.82 |

---

## Project Structure

```
.
├── main.py                  # FastAPI server
├── inference.py             # Baseline inference script
├── openenv.yaml             # OpenEnv spec
├── Dockerfile
├── requirements.txt
├── data/
│   └── cases.json           # 20 patient cases
└── env/
    ├── models.py            # Pydantic models
    ├── environment.py       # Core environment logic
    ├── medical_rules.py     # Clinical rules and red flags
    └── tasks/
        ├── task1_question_quality.py
        ├── task2_assessment.py
        └── task3_safe_advice.py
```

---

## License

Apache 2.0
