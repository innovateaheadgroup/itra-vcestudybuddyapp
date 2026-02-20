from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import Attempt, Mastery, User

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("")
def profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    attempt_count = db.scalar(select(func.count(Attempt.id)).where(Attempt.user_id == current_user.id)) or 0
    avg_mastery = db.scalar(select(func.avg(Mastery.mastery_score)).where(Mastery.user_id == current_user.id)) or 0
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "attempt_count": int(attempt_count),
        "average_mastery": round(float(avg_mastery), 3),
    }
