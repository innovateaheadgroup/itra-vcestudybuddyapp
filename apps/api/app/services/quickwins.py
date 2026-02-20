from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass
class ScheduleState:
    interval_days: int
    ease_factor: float
    next_due_at: datetime


def next_schedule(interval_days: int, ease_factor: float, correct: bool) -> ScheduleState:
    interval_days = max(1, interval_days)
    ease_factor = max(1.3, ease_factor)

    if correct:
        new_ease = min(3.0, ease_factor + 0.1)
        new_interval = int(round(interval_days * new_ease))
    else:
        new_ease = max(1.3, ease_factor - 0.2)
        new_interval = max(1, int(round(interval_days * 0.5)))

    due = datetime.now(UTC) + timedelta(days=new_interval)
    return ScheduleState(interval_days=new_interval, ease_factor=new_ease, next_due_at=due)
