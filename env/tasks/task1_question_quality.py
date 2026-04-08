"""
task1_question_quality.py — Easy task
Did the AI ask the RIGHT questions for this complaint?
Score strictly between 0.0 and 1.0 (exclusive)
"""
from __future__ import annotations
import re
from env.models import QuestionQualityAction, Reward, RewardBreakdown
from env.medical_rules import find_matching_rule


def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def _contains(text: str, keyword: str) -> bool:
    return _normalise(keyword) in _normalise(text)


def _clamp(v: float) -> float:
    """Clamp to strictly (0, 1) — never exactly 0.0 or 1.0."""
    return max(0.001, min(0.999, round(v, 3)))


def grade(action: QuestionQualityAction, ground_truth: dict) -> Reward:
    complaint = ground_truth.get("chief_complaint", "")
    rule = find_matching_rule(complaint)
    must_ask = rule.get("must_ask", [])
    red_flags = rule.get("red_flags", [])

    all_text = action.doctor_message + " " + " ".join(action.questions_asked) + " " + action.reasoning

    # How many required topics were asked about
    asked_count = sum(1 for topic in must_ask if _contains(all_text, topic))
    ask_score = min(0.999, asked_count / max(len(must_ask), 1))

    # Did AI ask about at least one red flag
    red_flag_asked = any(_contains(all_text, rf.split()[0]) for rf in red_flags)
    safety = 0.95 if red_flag_asked else 0.4

    # Was message long enough to be a real question
    completeness = 0.95 if len(action.doctor_message.strip()) > 20 else 0.3

    # Danger: did AI give diagnosis too early without asking questions
    premature_diagnosis = any(word in _normalise(action.doctor_message) for word in
                               ["you have", "aapko", "diagnosis is", "it is definitely"])
    danger_penalty = 0.3 if premature_diagnosis and asked_count < 3 else 0.0
    is_safe = danger_penalty == 0.0

    raw_total = (
        ask_score * 0.5
        + safety * 0.3
        + completeness * 0.2
        - danger_penalty
    )

    feedback_parts = []
    feedback_parts.append(f"Asked {asked_count}/{len(must_ask)} required topics.")
    if not red_flag_asked:
        feedback_parts.append(f"Did not ask about red flags: {red_flags[0] if red_flags else 'none'}.")
    if premature_diagnosis:
        feedback_parts.append("Gave diagnosis too early without enough questions.")

    return Reward(
        total=_clamp(raw_total),
        breakdown=RewardBreakdown(
            accuracy=_clamp(ask_score),
            safety=_clamp(safety),
            completeness=_clamp(completeness),
            danger_penalty=_clamp(danger_penalty),
        ),
        feedback=" ".join(feedback_parts),
        is_safe=is_safe,
        is_done=True,
    )
