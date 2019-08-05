import socket
from httplib import HTTPConnection


def get():
    conn = HTTPConnection('localhost', 41432)
    conn.request('GET', '/xx/yy/zz')
    rsp = conn.getresponse()
    print rsp


try:
    get()
except socket.error:
    print 'ehehe'
