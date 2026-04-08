from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["patient", "doctor"]
    content: str


class Observation(BaseModel):
    case_id: str
    patient_age: int
    patient_sex: Literal["M", "F", "Other"]
    language: Literal["en", "hi"] = "en"
    chief_complaint: str
    conversation_history: List[Message] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    task_type: Literal["question_quality", "assessment", "safe_advice"]
    task_description: str = ""
    step_number: int = 0


class QuestionQualityAction(BaseModel):
    action_type: Literal["question_quality"] = "question_quality"
    doctor_message: str
    questions_asked: List[str] = Field(default_factory=list)
    reasoning: str = ""


class AssessmentAction(BaseModel):
    action_type: Literal["assessment"] = "assessment"
    doctor_message: str
    primary_condition: str
    possible_conditions: List[str] = Field(default_factory=list)
    confidence: Literal["low", "moderate", "high"] = "moderate"
    reasoning: str = ""


class SafeAdviceAction(BaseModel):
    action_type: Literal["safe_advice"] = "safe_advice"
    doctor_message: str
    what_to_do: List[str] = Field(default_factory=list)
    what_to_eat: List[str] = Field(default_factory=list)
    medicines: List[str] = Field(default_factory=list)
    what_to_avoid: List[str] = Field(default_factory=list)
    go_to_hospital_if: List[str] = Field(default_factory=list)
    contraindications_checked: bool = True
    reasoning: str = ""


Action = QuestionQualityAction | AssessmentAction | SafeAdviceAction


class RewardBreakdown(BaseModel):
    accuracy: float = Field(0.0, ge=0.0, le=1.0)
    safety: float = Field(0.0, ge=0.0, le=1.0)
    completeness: float = Field(0.0, ge=0.0, le=1.0)
    danger_penalty: float = Field(0.0, ge=0.0, le=1.0)


class Reward(BaseModel):
    total: float = Field(..., ge=0.0, le=1.0)
    breakdown: RewardBreakdown
    feedback: str = ""
    is_safe: bool = True
    is_done: bool = False


class StepResponse(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: dict = Field(default_factory=dict)


class StateResponse(BaseModel):
    current_case: Observation
    episode_step: int
    cumulative_reward: float
    task_history: List[str] = Field(default_factory=list)
