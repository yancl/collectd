import time

def now():
    return int(time.time())

def now_microseconds():
    return int(time.time() * 1000000)
