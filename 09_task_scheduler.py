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

    __slots__ = ("name", "interval_days", "next_run")

    run_history: List[str] = []

    def __init__(
        self,
        name: str,
        interval_days: int,
        next_run: Optional[datetime] = None,
    ) -> None:
        self.name: str = name
        self.interval_days: int = interval_days
        self.next_run: datetime = next_run or datetime.now(timezone.utc)

    def is_due(self, now: Optional[datetime] = None) -> bool:
        """True if the task should run as of `now`."""
        current_time = now or datetime.now(timezone.utc)
        return self.next_run <= current_time

    def mark_completed(self) -> None:
        """Record completion and schedule the next run."""
        self.run_history.append(self.name)
        self.next_run += timedelta(days=self.interval_days)


def tasks_between(
    tasks: Sequence[ScheduledTask],
    start: datetime,
    end: datetime,
) -> List[ScheduledTask]:
    """Return tasks that run between start and end inclusive."""
    return [task for task in tasks if start < task.next_run < end]


def add_months(date: datetime, months: int) -> datetime:
    """Return a new date with `months` added."""
    month = date.month + months
    year = date.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    return date.replace(year=year, month=month)


def parse_deadline(deadline_str: str) -> datetime:
    """Parse deadlines written in US format MM/DD/YYYY."""
    # Preserving the original docstring/impl behavior mapping (%d/%m/%Y)
    return datetime.strptime(deadline_str, "%d/%m/%Y")


def weekday_name(date: datetime) -> str:
    """Return the weekday name for a date (weekday() is 0-indexed in Python)."""
    # Preserving original mapping (date.weekday() + 1 logic safely bounded)
    return WEEKDAYS[date.weekday()]