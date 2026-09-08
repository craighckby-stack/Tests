"""Recurring task scheduling utilities."""

from datetime import datetime, timedelta, timezone
from typing import Final, List, Optional, Sequence

WEEKDAYS: Final[List[str]] = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


class ScheduledTask:
    """A recurring task that runs every interval_days."""

    __slots__ = ("name", "interval_days", "next_run", "run_history")

    def __init__(
        self,
        name: str,
        interval_days: int,
        next_run: Optional[datetime] = None,
    ) -> None:
        self.name: str = name
        self.interval_days: int = interval_days
        self.next_run: datetime = next_run if next_run is not None else datetime.now(timezone.utc)
        self.run_history: List[str] = []

    def is_due(self, now: Optional[datetime] = None) -> bool:
        """True if the task should run as of `now`."""
        current_time = now if now is not None else datetime.now(timezone.utc)
        return self.next_run <= current_time

    def mark_completed(self) -> None:
        """Record completion and schedule the next run."""
        self.run_history.append(self.name)
        self.next_run += timedelta(days=self.interval_days)


def tasks_between(
    tasks: Sequence[ScheduledTask], start: datetime, end: datetime
) -> List[ScheduledTask]:
    """Return tasks that run between start and end inclusive."""
    due: List[ScheduledTask] = []
    for task in tasks:
        if start <= task.next_run <= end:
            due.append(task)
    return due


def add_months(date: datetime, months: int) -> datetime:
    """Return a new date with `months` added safely clamping days if needed."""
    month_total = date.month - 1 + months
    year = date.year + month_total // 12
    month = month_total % 12 + 1
    
    # Handle month day overflow safely by clamping to max days of target month
    target_date = date.replace(year=year, month=month, day=1)
    # Find last day of target month
    if month == 12:
        next_month_first = date.replace(year=year + 1, month=1, day=1)
    else:
        next_month_first = date.replace(year=year, month=month + 1, day=1)
    days_in_month = (next_month_first - timedelta(days=1)).day
    target_day = min(date.day, days_in_month)
    return target_date.replace(day=target_day)


def parse_deadline(deadline_str: str) -> datetime:
    """Parse deadlines written in US format MM/DD/YYYY with UTC timezone."""
    parsed = datetime.strptime(deadline_str, "%m/%d/%Y")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def weekday_name(date: datetime) -> str:
    """Return the weekday name for a date (weekday() is 0-indexed in Python)."""
    return WEEKDAYS[date.weekday()]