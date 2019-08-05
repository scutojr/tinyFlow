from socket import gethostbyname, getfqdn

from time import time
from httplib import HTTPConnection


def now_ms():
    return int(time() * 1000)

def host(hostname=None):
    if hostname:
        return gethostbyname(hostname)
    else:
        return gethostbyname(getfqdn())


class CacheRef(object):
    def __init__(self, timeout_ms):
        self.timeout = timeout_ms
        self.value = None
        self.deadline = 0

    def is_expired(self):
        return now_ms() >= self.deadline

    def get(self, default=None):
        if self.is_expired():
            self.valule = None
            return default
        else:
            return self.value or default

    def set(self, value):
        self.value = value
        self.deadline = now_ms() + self.timeout

    def set_if_expired_and_get(self, func, *args, **kwargs):
        if self.is_expired():
            value = func(*args, **kwargs)
            self.set(value)
        return self.get()

