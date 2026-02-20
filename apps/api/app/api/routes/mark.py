from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import Attempt, Mastery, Question, QuickWinsQueue, User
from app.schemas import AttemptSubmitRequest, MarkResponse
from app.services.marking import mark_question

router = APIRouter(tags=["marking"])


@router.post("/mark", response_model=MarkResponse)
def mark_attempt(
    payload: AttemptSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MarkResponse:
    question = db.scalar(select(Question).where(Question.id == payload.question_id))
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    result = mark_question(
        question=question,
        answer_text=payload.answer_text,
        code_snapshot=payload.code_snapshot,
        track=payload.track,
        integrity_mode=payload.integrity_mode,
        is_sat_assessment=payload.is_sat_assessment,
    )

    attempt = Attempt(
        user_id=current_user.id,
        question_id=question.id,
        answer_text=payload.answer_text,
        code_snapshot=payload.code_snapshot,
        score=result.feedback.score,
        max_score=result.feedback.max_score,
        feedback_json=result.feedback.model_dump(),
        mistake_tags=result.feedback.mistake_tags,
    )
    db.add(attempt)

    mastery = db.scalar(
        select(Mastery).where(
            Mastery.user_id == current_user.id, Mastery.topic_id == question.topic_id
        )
    )
    ratio = result.feedback.score / max(1, result.feedback.max_score)
    if not mastery:
        mastery = Mastery(
            user_id=current_user.id,
            topic_id=question.topic_id,
            mastery_score=ratio,
            last_practiced_at=datetime.now(UTC),
        )
        db.add(mastery)
    else:
        mastery.mastery_score = max(
            0.0, min(1.0, round(mastery.mastery_score * 0.7 + ratio * 0.3, 3))
        )
        mastery.last_practiced_at = datetime.now(UTC)

    if result.feedback.score < result.feedback.max_score:
        queue_item = db.scalar(
            select(QuickWinsQueue).where(
                QuickWinsQueue.user_id == current_user.id, QuickWinsQueue.question_id == question.id
            )
        )
        if not queue_item:
            db.add(
                QuickWinsQueue(
                    user_id=current_user.id,
                    topic_id=question.topic_id,
                    question_id=question.id,
                    interval_days=1,
                    ease_factor=2.2,
                    next_due_at=datetime.now(UTC),
                )
            )
        else:
            queue_item.next_due_at = datetime.now(UTC)
            queue_item.interval_days = 1
            queue_item.ease_factor = max(1.3, queue_item.ease_factor - 0.1)

    db.commit()

    return MarkResponse(
        feedback=result.feedback,
        where_marks_were_lost=result.where_marks_were_lost,
        common_mistakes=result.common_mistakes,
        upgrade_response=result.upgrade_response,
    )
