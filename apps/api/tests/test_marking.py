from app.models.models import Question
from app.services.marking import mark_question


def test_marking_mcq_exact_match() -> None:
    question = Question(
        topic_id=1,
        type="mcq",
        exam_style="short",
        command_terms=["describe"],
        marks=2,
        difficulty=1,
        prompt_md="Select the correct option.",
        options_json={"A": "Correct", "B": "Incorrect"},
        correct_json={"answer": "a"},
    )
    result = mark_question(
        question=question,
        answer_text="a",
        code_snapshot=None,
        track="foundation",
        integrity_mode="foundation",
    )
    assert result.feedback.score == 2
    assert result.feedback.max_score == 2
    assert result.feedback.criteria[0].name == "Correct option"


def test_marking_short_answer_rubric_keywords() -> None:
    question = Question(
        topic_id=3,
        type="short",
        exam_style="extended",
        command_terms=["justify"],
        marks=3,
        difficulty=2,
        prompt_md="Explain with evidence.",
        rubric_json={"keywords": ["requirement", "testing"], "reasoning_terms": ["because"]},
    )
    result = mark_question(
        question=question,
        answer_text="The requirement is clear because testing validates it.",
        code_snapshot=None,
        track="foundation",
        integrity_mode="foundation",
    )
    assert result.feedback.score >= 2
    assert result.feedback.max_score == 3
    assert any(item.name == "Reasoning quality" for item in result.feedback.criteria)
