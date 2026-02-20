from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import Mastery, Question, Topic, User
from app.schemas import CommandTermGuide, ExamTemplate, QuestionOut

router = APIRouter(prefix="/exam-skills", tags=["exam-skills"])


@router.get("/command-terms", response_model=list[CommandTermGuide])
def command_terms() -> list[CommandTermGuide]:
    return [
        CommandTermGuide(
            term="describe",
            definition="Give characteristics or features.",
            checklist=["Use relevant terminology", "State key features clearly"],
            example="Describe two functional requirements in the brief.",
        ),
        CommandTermGuide(
            term="explain",
            definition="Make the relationship between ideas clear.",
            checklist=["State cause/effect", "Use because/therefore", "Link to context"],
            example="Explain why normalisation improves data quality.",
        ),
        CommandTermGuide(
            term="analyse",
            definition="Break into parts and examine relationships.",
            checklist=["Identify components", "Compare effects", "Draw insight"],
            example="Analyse trade-offs between array and dictionary storage.",
        ),
        CommandTermGuide(
            term="justify",
            definition="Support a decision with reasons and evidence.",
            checklist=["Make a decision", "Provide evidence", "Address alternatives"],
            example="Justify your chosen visualisation for stakeholders.",
        ),
        CommandTermGuide(
            term="evaluate",
            definition="Judge value based on criteria.",
            checklist=["Set criteria", "Assess strengths/weaknesses", "Conclude"],
            example="Evaluate solution fitness against requirements.",
        ),
    ]


@router.get("/templates", response_model=list[ExamTemplate])
def templates() -> list[ExamTemplate]:
    return [
        ExamTemplate(
            id="short_define_apply_conclude",
            title="Short answer template: Define -> Apply -> Conclude",
            structure=["Define concept", "Apply to case/data", "Conclude impact"],
            example="Define validation, apply with an input rule, conclude data quality improvement.",
        ),
        ExamTemplate(
            id="short_claim_evidence_explain",
            title="Short answer template: Claim -> Evidence -> Explain",
            structure=["Claim", "Evidence", "Explain link to question"],
            example="Claim chart type suitability, cite dataset shape, explain readability impact.",
        ),
        ExamTemplate(
            id="case_study",
            title="Case study template",
            structure=[
                "Extract facts",
                "Identify requirement",
                "Propose approach",
                "Justify with constraints/risks",
            ],
            example="Extract stakeholder need, propose iterative model, justify with feedback cycle.",
        ),
        ExamTemplate(
            id="data_insights",
            title="Data insights template",
            structure=["Claim", "Evidence", "Explanation", "Limitation"],
            example="Claim trend, cite calculated percentage, explain implication, note sample bias.",
        ),
        ExamTemplate(
            id="software_design",
            title="Software design template",
            structure=[
                "Requirement",
                "Approach",
                "Algorithm/Data",
                "Testing",
                "Justification",
            ],
            example="State requirement, propose modular design, include algorithm choice and tests.",
        ),
    ]


@router.get("/timed-practice")
def timed_practice(
    unit: int = Query(..., ge=1, le=4),
    minutes: int = Query(default=20, ge=5, le=120),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    weak_topics = db.scalars(
        select(Topic)
        .join(Mastery, Mastery.topic_id == Topic.id, isouter=True)
        .where((Mastery.user_id == current_user.id) | (Mastery.user_id.is_(None)), Topic.unit == unit)
        .order_by(asc(Mastery.mastery_score).nullsfirst(), Topic.order)
        .limit(5)
    ).all()
    weak_topic_ids = [topic.id for topic in weak_topics]

    question_query = select(Question)
    if weak_topic_ids:
        question_query = question_query.where(Question.topic_id.in_(weak_topic_ids))
    questions = db.scalars(question_query.limit(10)).all()
    question_payload = []
    total_marks = max(1, sum(question.marks for question in questions))
    time_per_mark = max(1, round(minutes / total_marks, 2))
    for question in questions:
        question_payload.append(
            {
                "question": QuestionOut.model_validate(question).model_dump(),
                "time_per_mark_hint_minutes": time_per_mark,
            }
        )
    return {"unit": unit, "minutes": minutes, "questions": question_payload}


@router.post("/case-study/answer-plan")
def generate_answer_plan(payload: dict) -> dict:
    case_text = payload.get("case_text", "")
    tags = payload.get("tags", {})
    integrity_mode = payload.get("integrity_mode", "foundation")
    return {
        "case_summary": case_text[:220],
        "tagged_items": tags,
        "scaffold": [
            "Extract 3 critical facts from the case.",
            "Map each fact to one explicit requirement.",
            "Select one approach and justify with stakeholder/risk constraints.",
            "Add one limitation and mitigation.",
        ],
        "policy": (
            "Scaffold only (no full assessed answer in scored mode)."
            if integrity_mode == "scored"
            else "Practice scaffold with optional worked expansion."
        ),
    }
