from time import time


def now_ms():
    return int(time() * 1000)


def now_s():
    return int(time())


def is_int(string):
    try:
        int(string)
    except:
        return False
    return True


def visible_for_test(func):
    pass