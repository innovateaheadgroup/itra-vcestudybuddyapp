from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Question, Subject, Topic
from app.schemas import PracticeSetResponse, QuestionOut, SetBuilderRequest

router = APIRouter(prefix="/practice", tags=["practice"])


@router.post("/set-builder", response_model=PracticeSetResponse)
def build_set(payload: SetBuilderRequest, db: Session = Depends(get_db)) -> PracticeSetResponse:
    query = select(Question).join(Topic, Question.topic_id == Topic.id).join(Subject, Topic.subject_id == Subject.id)

    if payload.subject_code:
        query = query.where(Subject.code == payload.subject_code)
    if payload.unit:
        query = query.where(Topic.unit == payload.unit)
    if payload.topic_ids:
        query = query.where(Question.topic_id.in_(payload.topic_ids))
    if payload.difficulty:
        query = query.where(Question.difficulty == payload.difficulty)
    if payload.question_types:
        query = query.where(Question.type.in_(payload.question_types))
    if payload.exam_styles:
        query = query.where(Question.exam_style.in_(payload.exam_styles))

    if payload.mixed_topics:
        query = query.order_by(func.random())
    else:
        query = query.order_by(Question.topic_id, Question.id)

    questions = db.scalars(query.limit(payload.number_of_questions)).all()
    estimated_minutes = min(payload.time_target_minutes, len(questions) * 4)
    return PracticeSetResponse(
        questions=[QuestionOut.model_validate(question) for question in questions],
        estimated_minutes=estimated_minutes,
    )


@router.get("/questions/{question_id}", response_model=QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)) -> QuestionOut:
    question = db.scalar(select(Question).where(Question.id == question_id))
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return QuestionOut.model_validate(question)
