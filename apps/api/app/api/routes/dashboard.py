from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import Attempt, Mastery, QuickWinsQueue, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    one_week_ago = datetime.now(UTC) - timedelta(days=7)
    attempts_week = db.scalar(
        select(func.count(Attempt.id)).where(
            and_(Attempt.user_id == current_user.id, Attempt.created_at >= one_week_ago)
        )
    )
    avg_score = db.scalar(select(func.avg(Attempt.score)).where(Attempt.user_id == current_user.id)) or 0
    avg_max = db.scalar(select(func.avg(Attempt.max_score)).where(Attempt.user_id == current_user.id)) or 1
    due_quickwins = db.scalar(
        select(func.count(QuickWinsQueue.id)).where(
            QuickWinsQueue.user_id == current_user.id, QuickWinsQueue.next_due_at <= datetime.now(UTC)
        )
    )
    weak_topics = db.scalar(
        select(func.count(Mastery.id)).where(Mastery.user_id == current_user.id, Mastery.mastery_score < 0.5)
    )
    return {
        "attempts_last_7_days": int(attempts_week or 0),
        "average_score_ratio": round(float(avg_score) / max(float(avg_max), 1), 3),
        "quickwins_due": int(due_quickwins or 0),
        "weak_topics": int(weak_topics or 0),
    }
