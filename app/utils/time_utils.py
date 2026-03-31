import datetime


def now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def parse_iso(value: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(value)
