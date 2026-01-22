"""Phase 7 solutions: date and time.

Reference implementations for exercises 32.1–32.3.
"""

from __future__ import annotations

import datetime


def now_iso() -> str:
    """Exercise 32.1: Return current datetime in ISO format."""

    return datetime.datetime.now().isoformat(timespec="seconds")


def days_between(date1: datetime.date, date2: datetime.date) -> int:
    """Exercise 32.2: Absolute days difference between two dates."""

    return abs((date2 - date1).days)


def utc_to_ist(dt_utc: datetime.datetime) -> datetime.datetime:
    """Exercise 32.3: Convert a UTC datetime to IST (UTC+05:30)."""

    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=datetime.timezone.utc)

    ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    return dt_utc.astimezone(ist)
