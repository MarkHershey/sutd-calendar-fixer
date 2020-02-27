from datetime import datetime

def timestamp():
    now = str(datetime.now())
    ts = ""
    for i in now[:-7]:
        if i in (" ", "-", ":"):
            pass
        else:
            ts += i
    return ts
