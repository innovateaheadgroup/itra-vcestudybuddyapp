from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import Attempt, Mastery, QuickWinsQueue, User
from app.schemas import (
    QuickWinsItemOut,
    QuickWinsReviewRequest,
    QuickWinsSessionOut,
    QuickWinsSessionRequest,
)
from app.services.quickwins import next_schedule

router = APIRouter(prefix="/quick-wins", tags=["quick-wins"])


def _status_streak(attempts: list[Attempt]) -> int:
    if not attempts:
        return 0
    by_day: dict[date, bool] = {}
    for attempt in attempts:
        by_day.setdefault(attempt.created_at.date(), True)
    streak = 0
    today = date.today()
    while by_day.get(today):
        streak += 1
        today = date.fromordinal(today.toordinal() - 1)
    return streak


@router.post("/session", response_model=QuickWinsSessionOut)
def get_daily_session(
    payload: QuickWinsSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuickWinsSessionOut:
    due_now = datetime.now(UTC)
    limit = {5: 4, 10: 8, 15: 12}[payload.minutes]
    due_items = db.scalars(
        select(QuickWinsQueue)
        .where(QuickWinsQueue.user_id == current_user.id, QuickWinsQueue.next_due_at <= due_now)
        .order_by(QuickWinsQueue.next_due_at)
        .limit(limit)
    ).all()

    if len(due_items) < limit:
        weak_topics = db.scalars(
            select(Mastery)
            .where(Mastery.user_id == current_user.id)
            .order_by(Mastery.mastery_score)
            .limit(limit - len(due_items))
        ).all()
        for mastery in weak_topics:
            item = QuickWinsQueue(
                user_id=current_user.id,
                topic_id=mastery.topic_id,
                question_id=None,
                next_due_at=due_now,
                interval_days=1,
                ease_factor=2.3,
            )
            db.add(item)
            due_items.append(item)
        db.commit()

    attempts = db.scalars(
        select(Attempt).where(Attempt.user_id == current_user.id).order_by(desc(Attempt.created_at)).limit(40)
    ).all()
    trend = [round(item.mastery_score, 3) for item in db.scalars(select(Mastery).where(Mastery.user_id == current_user.id)).all()]

    return QuickWinsSessionOut(
        items=[
            QuickWinsItemOut(
                id=item.id,
                topic_id=item.topic_id,
                question_id=item.question_id,
                next_due_at=item.next_due_at,
                interval_days=item.interval_days,
                ease_factor=item.ease_factor,
            )
            for item in due_items
        ],
        streak=_status_streak(attempts),
        mastery_trend=trend,
    )


@router.post("/review")
def submit_review(
    payload: QuickWinsReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    item = db.scalar(
        select(QuickWinsQueue).where(
            QuickWinsQueue.id == payload.queue_item_id, QuickWinsQueue.user_id == current_user.id
        )
    )
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")

    schedule = next_schedule(item.interval_days, item.ease_factor, payload.correct)
    item.interval_days = schedule.interval_days
    item.ease_factor = schedule.ease_factor
    item.next_due_at = schedule.next_due_at
    db.commit()
    return {
        "id": item.id,
        "interval_days": item.interval_days,
        "ease_factor": item.ease_factor,
        "next_due_at": item.next_due_at,
    }
