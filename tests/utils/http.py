from httplib import *


def get(host, port, endpoint, **params):
    """
    :param host:
    :param port:
    :param endpoint:
    :return:  (status, reason, response message)
    """
    conn = HTTPConnection(host, port)
    search = []
    for k, v in params.iteritems():
        search.append(str(k) + '=' + str(v))
    if search:
        endpoint += '?' + '&'.join(search)
    conn.request('GET', endpoint)
    resp = conn.getresponse()
    return resp.status, resp.reason, resp.read()


def post(host, port, endpoint, body=None, method=None):
    conn = HTTPConnection(host, port)
    conn.request(method or 'POST', endpoint, body)
    resp = conn.getresponse()
    return resp.status, resp.reason, resp.read()


def delete(host, port, endpoint, body=None):
    return post(host, port, endpoint, body, 'DELETE')
