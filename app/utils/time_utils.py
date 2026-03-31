import datetime


def now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def parse_iso(value: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(value)


def add_days_to_date(date: datetime.datetime, days: int) -> datetime.datetime:
    return date + datetime.timedelta(days=days)
