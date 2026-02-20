from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, period_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.period = timedelta(seconds=period_seconds)
        self._events: dict[str, deque[datetime]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = datetime.now(UTC)
        events = self._events[key]
        cutoff = now - self.period
        while events and events[0] < cutoff:
            events.popleft()
        if len(events) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        events.append(now)
