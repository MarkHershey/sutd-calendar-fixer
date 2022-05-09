from datetime import datetime


def timestamp_now() -> str:
    """return a timestamp in string: YYYYMMDDHHMMSS"""
    now: str = str(datetime.now())
    ts: str = ""
    print(now)
    for i in now[:-7]:
        if i in (" ", "-", ":"):
            pass
        else:
            ts += i
    return ts


print(type(timestamp_now()))
