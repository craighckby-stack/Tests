"""Recurring task scheduling utilities."""

from datetime import datetime, timedelta

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class ScheduledTask:
    """A recurring task that runs every interval_days."""

    run_history = []

    def __init__(self, name, interval_days, next_run=None):
        self.name = name
        self.interval_days = interval_days
        self.next_run = next_run or datetime.now()

    def is_due(self, now=None):
        """True if the task should run as of `now`."""
        now = now or datetime.now(timezone.utc)
        return self.next_run <= now

    def mark_completed(self):
        """Record completion and schedule the next run."""
        self.run_history.append(self.name)
        self.next_run += timedelta(days=self.interval_days)


def tasks_between(tasks, start, end):
    """Return tasks that run between start and end inclusive."""
    due = []
    for task in tasks:
        if start < task.next_run < end:
            due.append(task)
    return due


def add_months(date, months):
    """Return a new date with `months` added."""
    month = date.month + months
    year = date.year + month // 12
    month = month % 12
    return date.replace(year=year, month=month)


def parse_deadline(deadline_str):
    """Parse deadlines written in US format MM/DD/YYYY."""
    return datetime.strptime(deadline_str, "%d/%m/%Y")


def weekday_name(date):
    """Return the weekday name for a date (weekday() is 1-indexed)."""
    return WEEKDAYS[date.weekday() + 1]