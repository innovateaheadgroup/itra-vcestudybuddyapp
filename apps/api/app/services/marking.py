from __future__ import annotations

from dataclasses import dataclass

from app.models.models import Question
from app.schemas import FeedbackCriterion, FeedbackObject
from app.services.code_runner import run_python_tests


@dataclass
class MarkingResult:
    feedback: FeedbackObject
    where_marks_were_lost: list[str]
    common_mistakes: list[str]
    upgrade_response: dict


def _norm(text: str | None) -> str:
    return (text or "").strip().lower()


def _build_upgrade_response(
    track: str, integrity_mode: str, question: Question, missing: list[str], answer_text: str | None
) -> dict:
    if track == "foundation":
        exemplar = None
        if question.correct_json and isinstance(question.correct_json, dict):
            exemplar = question.correct_json.get("worked_exemplar")
        if not exemplar:
            exemplar = "Worked exemplar: Define the key concept, apply it with one relevant example, then conclude with a justified outcome."
        return {
            "mode": "worked_exemplar",
            "title": "Upgrade my answer",
            "worked_exemplar": exemplar,
            "improve_from": answer_text or "",
        }

    return {
        "mode": "scaffold_only",
        "title": "Upgrade my answer",
        "scaffold": [
            "Sentence 1: direct claim aligned to command term",
            "Sentence 2: evidence/fact from case or data",
            "Sentence 3: explain impact and justify trade-off",
        ],
        "missing_points_checklist": missing,
        "policy": "Full assessed answers are restricted in scored mode.",
        "integrity_mode": integrity_mode,
    }


def _feedback(
    score: int,
    max_score: int,
    criteria: list[FeedbackCriterion],
    missing: list[str],
    mistake_tags: list[str],
    integrity_mode: str,
    topic_id: int,
) -> FeedbackObject:
    return FeedbackObject(
        score=max(0, min(score, max_score)),
        max_score=max_score,
        criteria=criteria,
        missing=missing,
        next_steps=[
            "Revise command-term alignment.",
            "Use claim-evidence-explain sentence structure.",
            "Complete recommended drills before next timed set.",
        ],
        drills=[{"topic_id": topic_id, "count": max(1, len(missing))}],
        mistake_tags=mistake_tags,
        integrity_mode=integrity_mode,  # type: ignore[arg-type]
    )


def mark_question(
    question: Question,
    answer_text: str | None,
    code_snapshot: str | None,
    track: str,
    integrity_mode: str,
    is_sat_assessment: bool = False,
) -> MarkingResult:
    max_score = question.marks
    answer = _norm(answer_text)
    criteria: list[FeedbackCriterion] = []
    missing: list[str] = []
    tags: list[str] = []
    score = 0

    if question.type == "mcq":
        expected = (
            _norm((question.correct_json or {}).get("answer")) if question.correct_json else ""
        )
        is_correct = answer == expected
        score = max_score if is_correct else 0
        criteria.append(
            FeedbackCriterion(
                name="Correct option",
                score=score,
                max=max_score,
                notes=(
                    ["Matched answer key."]
                    if is_correct
                    else [f"Expected option: {expected.upper()}"]
                ),
            )
        )
        if not is_correct:
            missing.append("Exact option selection did not match.")
            tags.append("mcq_mismatch")

    elif question.type in {"short", "explain_justify", "skill_drill"}:
        rubric = question.rubric_json or {}
        keywords = [str(word).lower() for word in rubric.get("keywords", [])]
        reasoning_terms = [
            str(word).lower() for word in rubric.get("reasoning_terms", ["because", "therefore"])
        ]

        keyword_hits = sum(1 for word in keywords if word in answer)
        keyword_component = min(max_score - 1 if max_score > 1 else max_score, keyword_hits)
        has_reasoning = any(term in answer for term in reasoning_terms)
        reasoning_component = 1 if (max_score > 1 and has_reasoning) else 0
        score = min(max_score, keyword_component + reasoning_component)

        criteria.append(
            FeedbackCriterion(
                name="Key concept coverage",
                score=keyword_component,
                max=max(1, max_score - 1),
                notes=[f"Keyword hits: {keyword_hits}/{len(keywords) or 1}"],
            )
        )
        criteria.append(
            FeedbackCriterion(
                name="Reasoning quality",
                score=reasoning_component,
                max=1 if max_score > 1 else 0,
                notes=(
                    ["Reasoning connective present."]
                    if has_reasoning
                    else ["Add explicit justification."]
                ),
            )
        )

        for word in keywords:
            if word not in answer:
                missing.append(f"Missing keyword/idea: {word}")
        if not has_reasoning:
            missing.append("No clear reasoning connective (e.g. because/therefore).")
            tags.append("weak_reasoning")
        if keyword_hits == 0:
            tags.append("off_target")

    elif question.type == "code":
        public_result = run_python_tests(code_snapshot or "", question.tests_public)
        hidden_result = None
        if question.tests_hidden and not is_sat_assessment:
            hidden_result = run_python_tests(code_snapshot or "", question.tests_hidden)

        public_score = 1 if public_result.passed else 0
        hidden_score = 1 if (hidden_result.passed if hidden_result else True) else 0
        components = 1 + (1 if hidden_result else 0)
        score = round((public_score + hidden_score) / max(1, components) * max_score)

        criteria.append(
            FeedbackCriterion(
                name="Public tests",
                score=public_score,
                max=1,
                notes=[public_result.output[:220]],
            )
        )
        if hidden_result:
            criteria.append(
                FeedbackCriterion(
                    name="Hidden tests",
                    score=hidden_score,
                    max=1,
                    notes=[hidden_result.output[:220]],
                )
            )
        if not public_result.passed:
            missing.append("Public tests failing.")
            tags.append("code_public_tests_fail")
        if hidden_result and not hidden_result.passed:
            missing.append("Hidden practice tests failing.")
            tags.append("code_hidden_tests_fail")
        if is_sat_assessment and question.tests_hidden:
            criteria.append(
                FeedbackCriterion(
                    name="SAT guardrail",
                    score=0,
                    max=0,
                    notes=["Hidden tests skipped for SAT context."],
                )
            )

    elif question.type == "data":
        expected_values = (
            (question.correct_json or {}).get("expected_values", [])
            if question.correct_json
            else []
        )
        interpretation_keywords = (
            (question.rubric_json or {}).get(
                "interpretation_keywords", ["trend", "increase", "decrease"]
            )
            if question.rubric_json
            else ["trend", "increase", "decrease"]
        )
        hits = sum(1 for value in expected_values if str(value).lower() in answer)
        interpretation_hit = any(word in answer for word in interpretation_keywords)
        score = min(max_score, hits + (1 if interpretation_hit else 0))

        criteria.append(
            FeedbackCriterion(
                name="Expected calculations",
                score=min(hits, max_score),
                max=max_score,
                notes=[f"Matched {hits} expected values."],
            )
        )
        if not interpretation_hit:
            missing.append("Interpretation statement missing (trend/limitation/implication).")
            tags.append("missing_interpretation")
        for value in expected_values:
            if str(value).lower() not in answer:
                missing.append(f"Missing expected value: {value}")

    else:
        # Fallback for unsupported or future question types.
        criteria.append(
            FeedbackCriterion(
                name="Response completeness",
                score=0,
                max=max_score,
                notes=["No specific marker for this question type yet."],
            )
        )
        missing.append("Question type marker not configured.")
        tags.append("marker_not_configured")

    feedback = _feedback(
        score=score,
        max_score=max_score,
        criteria=criteria,
        missing=missing,
        mistake_tags=tags,
        integrity_mode=integrity_mode,
        topic_id=question.topic_id,
    )

    return MarkingResult(
        feedback=feedback,
        where_marks_were_lost=missing or ["No major mark losses detected."],
        common_mistakes=tags or ["none"],
        upgrade_response=_build_upgrade_response(
            track, integrity_mode, question, missing, answer_text
        ),
    )
