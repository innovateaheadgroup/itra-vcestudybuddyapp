from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.config import get_settings
from app.schemas import BuddyChatRequest, BuddyChatResponse, FeedbackObject


def _empty_feedback(mode: str) -> FeedbackObject:
    return FeedbackObject(
        score=0,
        max_score=0,
        criteria=[],
        missing=[],
        next_steps=[],
        drills=[],
        mistake_tags=[],
        integrity_mode=mode,  # type: ignore[arg-type]
    )


def should_refuse_scored_full_answer(prompt: str, patterns: list[str]) -> bool:
    lowered = prompt.lower()
    if "sac" in lowered or "sat" in lowered:
        for pattern in patterns:
            if pattern in lowered:
                return True
    return False


class BuddyProvider(ABC):
    @abstractmethod
    def coach(self, payload: BuddyChatRequest) -> BuddyChatResponse:
        raise NotImplementedError


class MockBuddyProvider(BuddyProvider):
    def coach(self, payload: BuddyChatRequest) -> BuddyChatResponse:
        settings = get_settings()
        if payload.integrity_mode == "scored" and should_refuse_scored_full_answer(
            payload.prompt, settings.buddy_refusal_patterns
        ):
            return BuddyChatResponse(
                quick_diagnosis="You are asking for a full assessed SAC/SAT answer, which is not allowed in scored mode.",
                what_to_fix_first=[
                    "Reframe the request as coaching (e.g. ask for structure or feedback on your own draft).",
                    "Start with key command terms and what each mark likely expects.",
                ],
                hints=[
                    "What is the core claim your answer should defend?",
                    "Which case/data evidence directly supports your claim?",
                    "Where can you justify trade-offs or limitations?",
                ],
                mini_drill="Write a 3-bullet response plan: claim, evidence, justification.",
                checklist_aligned_to_marks=[
                    "1 mark: accurate terminology",
                    "1 mark: relevant case/data evidence",
                    "1 mark: explicit explanation of impact",
                ],
                feedback=_empty_feedback("scored"),
            )

        mode = payload.integrity_mode
        worked_example_hint = (
            "A worked exemplar can be shown for this practice context."
            if mode == "foundation"
            else "Scaffold only in scored mode: no full assessed response provided."
        )
        marks = payload.marks or 4

        return BuddyChatResponse(
            quick_diagnosis="Your response likely has partial understanding but lacks explicit justification against marking criteria.",
            what_to_fix_first=[
                "State a clear claim in the first sentence.",
                "Attach one concrete example or data point.",
                "Link evidence back to the command term directly.",
            ],
            hints=[
                "Which command term is dominant (explain/analyse/justify)?",
                "Can you include one counterpoint or limitation?",
                "Have you mapped each sentence to at least one mark?",
            ],
            mini_drill="In 3 lines: claim -> evidence -> justification. Keep each line under 20 words.",
            checklist_aligned_to_marks=[f"Mark {i + 1}: explicit criterion evidence" for i in range(marks)],
            feedback=FeedbackObject(
                score=max(1, marks - 1),
                max_score=marks,
                criteria=[
                    {"name": "Concept accuracy", "score": 1, "max": 1, "notes": ["Terminology mostly correct."]},
                    {"name": "Evidence use", "score": 1, "max": 1, "notes": ["Add specific evidence."]},
                    {
                        "name": "Reasoning depth",
                        "score": max(0, marks - 2),
                        "max": max(1, marks - 2),
                        "notes": [worked_example_hint],
                    },
                ],
                missing=["An explicit link from evidence to outcome"],
                next_steps=["Use a template from Exam Skills", "Complete one targeted skill drill"],
                drills=[{"topic_id": 1, "count": 2}],
                mistake_tags=["vague_justification"],
                integrity_mode=mode,  # type: ignore[arg-type]
            ),
        )


def get_buddy_provider() -> BuddyProvider:
    settings = get_settings()
    if settings.llm_provider == "mock":
        return MockBuddyProvider()
    # For non-mock providers, keep a safe fallback until external API wiring is added.
    return MockBuddyProvider()
