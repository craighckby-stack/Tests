"""Recurring task scheduling utilities."""

from datetime import datetime, timedelta, timezone
from typing import Final, Optional, Sequence

WEEKDAYS: Final[tuple[str, ...]] = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)

_DAYS_IN_MONTH: Final[tuple[int, ...]] = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


class ScheduledTask:
    """A recurring task that runs every interval_days."""

    __slots__ = ("name", "interval_days", "next_run", "run_history")

    name: str
    interval_days: int
    next_run: datetime
    run_history: list[str]

    def __init__(
        self,
        name: str,
        interval_days: int,
        next_run: Optional[datetime] = None,
    ) -> None:
        if not isinstance(interval_days, int):
            raise TypeError("interval_days must be an integer.")
        if interval_days <= 0:
            raise ValueError("interval_days must be greater than zero.")
        self.name = name
        self.interval_days = interval_days
        self.next_run = next_run if next_run is not None else datetime.now(timezone.utc)
        self.run_history = []

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
) -> list[ScheduledTask]:
    """Return tasks that run between start and end inclusive."""
    return [task for task in tasks if start <= task.next_run <= end]


def add_months(date: datetime, months: int) -> datetime:
    """Return a new date with `months` added."""
    if not isinstance(date, datetime):
        raise TypeError("date must be a datetime instance.")
    if not isinstance(months, int):
        raise TypeError("months must be an integer.")
        
    total_months = date.month - 1 + months
    year = date.year + total_months // 12
    month = total_months % 12 + 1
    
    # Handle overflow in days for months with fewer days
    is_leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    max_days = 29 if month == 2 and is_leap else _DAYS_IN_MONTH[month - 1]
    day = min(date.day, max_days)
    
    return date.replace(year=year, month=month, day=day)


def parse_deadline(deadline_str: str) -> datetime:
    """Parse deadlines written in strict DD/MM/YYYY format with robust error handling."""
    if not isinstance(deadline_str, str):
        raise TypeError("deadline_str must be a string.")
    try:
        return datetime.strptime(deadline_str, "%d/%m/%Y")
    except (ValueError, TypeError) as err:
        raise ValueError(f"Invalid deadline format: '{deadline_str}'. Expected DD/MM/YYYY.") from err


def weekday_name(date: datetime) -> str:
    """Return the weekday name for a date using safe tuple indexing."""
    if not isinstance(date, datetime):
        raise TypeError("date must be a datetime instance.")
    return WEEKDAYS[date.weekday()]