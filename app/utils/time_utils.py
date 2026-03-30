import datetime


def now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)
