from time import time


def now_ms():
    return int(time() * 1000)

def now_s():
    return int(time())
