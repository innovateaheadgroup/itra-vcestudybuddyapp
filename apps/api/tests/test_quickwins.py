from app.services.quickwins import next_schedule


def test_quickwins_interval_increases_on_correct() -> None:
    state = next_schedule(interval_days=2, ease_factor=2.3, correct=True)
    assert state.interval_days >= 4
    assert state.ease_factor > 2.3


def test_quickwins_interval_shortens_on_incorrect() -> None:
    state = next_schedule(interval_days=6, ease_factor=2.5, correct=False)
    assert state.interval_days <= 3
    assert state.ease_factor < 2.5
