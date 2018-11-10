from httplib import *


def get(host, port, endpoint):
    """
    :param host:
    :param port:
    :param endpoint:
    :return:  (status, reason, response message)
    """
    conn = HTTPConnection(host, port)
    conn.request('GET', endpoint)
    resp = conn.getresponse()
    return resp.status, resp.reason, resp.read()


def post(host, port, endpoint, body=None):
    conn = HTTPConnection(host, port)
    conn.request('POST', endpoint, body)
    resp = conn.getresponse()
    return resp.status, resp.reason, resp.read()