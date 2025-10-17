from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Iterable, Tuple


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_month(value: str) -> Tuple[date, date]:
    start = datetime.strptime(value + "-01", "%Y-%m-%d").date()
    # Compute end of month by jumping to next month and subtracting a day
    if start.month == 12:
        next_month = date(year=start.year + 1, month=1, day=1)
    else:
        next_month = date(year=start.year, month=start.month + 1, day=1)
    end = next_month - timedelta(days=1)
    return (start, end)


def month_iter(start_month: str, end_month: str) -> Iterable[str]:
    cursor = datetime.strptime(start_month + "-01", "%Y-%m-%d").date()
    end_date = datetime.strptime(end_month + "-01", "%Y-%m-%d").date()
    while cursor <= end_date:
        yield f"{cursor.year:04d}-{cursor.month:02d}"
        if cursor.month == 12:
            cursor = date(year=cursor.year + 1, month=1, day=1)
        else:
            cursor = date(year=cursor.year, month=cursor.month + 1, day=1)


def advance_date_by_frequency(current: date, frequency: str) -> date:
    if frequency == "daily":
        return current + timedelta(days=1)
    if frequency == "weekly":
        return current + timedelta(weeks=1)
    if frequency == "monthly":
        # naive month add: jump by 1 month keeping day where possible
        month = current.month + 1
        year = current.year + (1 if month > 12 else 0)
        month = 1 if month > 12 else month
        # clamp day to 28 to avoid invalid dates
        day = min(current.day, 28)
        return date(year=year, month=month, day=day)
    if frequency == "yearly":
        # clamp Feb 29 to Feb 28 if needed
        day = current.day
        month = current.month
        year = current.year + 1
        if month == 2 and day == 29:
            day = 28
        return date(year=year, month=month, day=day)
    return current
