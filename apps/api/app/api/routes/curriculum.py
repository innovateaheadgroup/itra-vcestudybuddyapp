from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import Lesson, Mastery, Subject, Topic, User
from app.schemas import LessonOut, TopicCardOut, TopicOut

router = APIRouter(prefix="/learn", tags=["learn"])


@router.get("/subjects")
def list_subjects(db: Session = Depends(get_db)) -> list[dict]:
    subjects = db.scalars(select(Subject).order_by(Subject.id)).all()
    return [{"id": s.id, "code": s.code, "name": s.name} for s in subjects]


@router.get("/topics", response_model=list[TopicCardOut])
def list_topics(
    subject_code: str | None = None,
    unit: int | None = Query(default=None, ge=1, le=4),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TopicCardOut]:
    query = select(Topic).join(Subject, Topic.subject_id == Subject.id)
    if subject_code:
        query = query.where(Subject.code == subject_code)
    if unit:
        query = query.where(Topic.unit == unit)
    query = query.order_by(Topic.unit, Topic.order)

    topics = db.scalars(query).all()
    cards: list[TopicCardOut] = []
    for topic in topics:
        mastery = db.scalar(
            select(Mastery).where(Mastery.user_id == current_user.id, Mastery.topic_id == topic.id)
        )
        mastery_pct = int(round((mastery.mastery_score if mastery else 0) * 100))
        if mastery_pct == 0:
            status = "Not started"
        elif mastery_pct < 50:
            status = "Learning"
        elif mastery_pct < 80:
            status = "Practising"
        else:
            status = "Ready"

        estimated_time = (
            db.scalar(select(func.coalesce(func.sum(Lesson.estimated_minutes), 20)).where(Lesson.topic_id == topic.id))
            or 20
        )
        cards.append(
            TopicCardOut(
                topic=TopicOut.model_validate(topic),
                mastery_pct=mastery_pct,
                status=status,  # type: ignore[arg-type]
                estimated_time=int(estimated_time),
            )
        )
    return cards


@router.get("/topics/{topic_id}/lessons", response_model=list[LessonOut])
def list_lessons(topic_id: int, db: Session = Depends(get_db)) -> list[LessonOut]:
    lessons = db.scalars(select(Lesson).where(Lesson.topic_id == topic_id).order_by(Lesson.id)).all()
    return [LessonOut.model_validate(lesson) for lesson in lessons]
