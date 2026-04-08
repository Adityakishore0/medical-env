"""
environment.py — Core OpenEnv Medical AI Doctor Environment
reset() / step() / state() — full OpenEnv compliance
"""
from __future__ import annotations
import json
import random
from pathlib import Path
from env.models import (
    Observation, Message,
    QuestionQualityAction, AssessmentAction, SafeAdviceAction,
    Reward, RewardBreakdown, StepResponse, StateResponse,
)
from env.tasks import task1_question_quality, task2_assessment, task3_safe_advice

DATA_PATH = Path(__file__).parent.parent / "data" / "cases.json"


class MedicalAIDoctorEnvironment:
    def __init__(self, seed: int | None = None, task_filter: str | None = None):
        self._rng = random.Random(seed)
        self._cases_raw: list[dict] = self._load_cases(task_filter)
        self._case_queue: list[dict] = []
        self._current_case: dict | None = None
        self._current_obs: Observation | None = None
        self._episode_step: int = 0
        self._cumulative_reward: float = 0.0
        self._task_history: list[str] = []

    def reset(self, case_id: str | None = None) -> Observation:
        if not self._case_queue:
            self._case_queue = list(self._cases_raw)
            self._rng.shuffle(self._case_queue)

        if case_id:
            matches = [c for c in self._cases_raw if c["case_id"] == case_id]
            raw = matches[0] if matches else self._case_queue.pop(0)
        else:
            raw = self._case_queue.pop(0)

        self._current_case = raw
        self._episode_step = 0
        self._cumulative_reward = 0.0
        self._task_history = []
        self._current_obs = self._build_observation(raw)
        return self._current_obs

    def step(self, action_dict: dict) -> StepResponse:
        if self._current_case is None:
            raise RuntimeError("Call reset() before step().")

        self._episode_step += 1
        task_type = self._current_obs.task_type
        ground_truth = self._current_case.get("ground_truth", {})
        ground_truth["chief_complaint"] = self._current_case.get("chief_complaint", "")
        ground_truth["allergies"] = self._current_case.get("allergies", [])
        ground_truth["current_medications"] = self._current_case.get("current_medications", [])

        reward = self._grade(action_dict, task_type, ground_truth)
        self._cumulative_reward += reward.total
        self._task_history.append(
            f"step={self._episode_step} task={task_type} reward={reward.total:.3f}"
        )

        return StepResponse(
            observation=self._current_obs,
            reward=reward,
            done=True,
            info={
                "case_id": self._current_case["case_id"],
                "task_type": task_type,
                "episode_step": self._episode_step,
                "chief_complaint": self._current_case.get("chief_complaint", ""),
            },
        )

    def state(self) -> StateResponse:
        if self._current_obs is None:
            raise RuntimeError("Call reset() before state().")
        return StateResponse(
            current_case=self._current_obs,
            episode_step=self._episode_step,
            cumulative_reward=round(self._cumulative_reward, 4),
            task_history=self._task_history,
        )

    def _load_cases(self, task_filter: str | None) -> list[dict]:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            cases = json.load(f)
        if task_filter:
            cases = [c for c in cases if c.get("task_type") == task_filter]
        return cases

    def _build_observation(self, raw: dict) -> Observation:
        history = [Message(**m) for m in raw.get("conversation_history", [])]
        return Observation(
            case_id=raw["case_id"],
            patient_age=raw["patient_age"],
            patient_sex=raw["patient_sex"],
            language=raw.get("language", "en"),
            chief_complaint=raw["chief_complaint"],
            conversation_history=history,
            current_medications=raw.get("current_medications", []),
            allergies=raw.get("allergies", []),
            task_type=raw["task_type"],
            task_description=raw.get("task_description", ""),
            step_number=0,
        )

    def _grade(self, action_dict: dict, task_type: str, ground_truth: dict) -> Reward:
        try:
            if task_type == "question_quality":
                action = QuestionQualityAction(**action_dict)
                return task1_question_quality.grade(action, ground_truth)
            elif task_type == "assessment":
                action = AssessmentAction(**action_dict)
                return task2_assessment.grade(action, ground_truth)
            elif task_type == "safe_advice":
                action = SafeAdviceAction(**action_dict)
                return task3_safe_advice.grade(action, ground_truth)
            else:
                return self._null_reward(f"Unknown task: {task_type}")
        except Exception as e:
            return self._null_reward(f"Parse error: {e}")

    @staticmethod
    def _null_reward(msg: str) -> Reward:
        # FIX: Changed from 0.0 to 0.001 so score is strictly between 0 and 1
        return Reward(
            total=0.001,
            breakdown=RewardBreakdown(),
            feedback=msg,
            is_safe=False,
            is_done=True,
        )

    @property
    def case_count(self) -> int:
        return len(self._cases_raw)

    def list_cases(self) -> list[dict]:
        return [
            {"case_id": c["case_id"], "task_type": c["task_type"],
             "chief_complaint": c["chief_complaint"][:60]}
            for c in self._cases_raw
        ]