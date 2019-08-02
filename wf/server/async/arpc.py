import sys
import time
import logging
import inspect
from mock import Mock
from threading import Thread
from functools import partial

import bson.json_util as json
from stomp import ConnectionListener, Connection
from stomp.exception import ConnectFailedException

from wf.reactor import Event

from .publisher import Publisher
from .consumer import Consumer


ARPC_ANNOTATION ='arpc_annotation'


def route(routing_key=None):
    def internal(func):
        m = Method(routing_key or func.__name__)
        func.arpc_annotation = m
        return func
    return internal


def method_with_annotation(obj_or_cls):
    results = []
    for field in dir(obj_or_cls):
        member = getattr(obj_or_cls, field)
        if inspect.ismethod(member) or isinstance(member, Mock):
            annotation = getattr(member, ARPC_ANNOTATION, None)
            if annotation:
                results.append((annotation, member))
    return results


class Method(object):
    def __init__(self, routing_key):
        self.key = routing_key


class AsyncRpcServer(Consumer):
    pass


class AsyncRpcClient(Publisher):
    def __init__(self, host_and_ports, topic, stub_cls):
        super(AsyncRpcClient, self).__init__(host_and_ports, topic)
        self.stub_cls = stub_cls
        self.stubs = {}

        self._build()

    def _build(self):
        def do_publish(routing_key, *args, **kwarg):
            msg = {
                'args': args,
                'kwarg': kwarg
            }
            self.publish(msg, routing_key)
        for annotation, method in method_with_annotation(self.stub_cls):
            key = annotation.key
            self.stubs[method.__name__] = partial(do_publish, key)

    def __getattr__(self, name, default=None):
        if name not in self.stubs:
            raise AttributeError(
                '%s object has no attribute %s' % (self.stub_cls.__name__, name)
            )
        return self.stubs[name]


class Handler(object):
    def __init__(self, obj):
        self.obj = obj
        self.stubs = {}

        self._build()

    def _build(self):
        for annotation, method in method_with_annotation(self.obj):
            key = annotation.key
            self.stubs[key] = method

    def handle(self, msg):
        key = msg['routing_key']
        payload = msg['payload']
        args, kwarg = payload.get('args', []), payload.get('kwarg', {})
        stub = self.stubs[key]
        stub(*args, **kwarg)


class AsyncRpcBuilder(object):
    def __init__(self, host_and_ports, username=None, password=None):
        self.host_and_ports = host_and_ports
        self.username = username
        self.password = password

    def server(self, topic, obj):
        handler = Handler(obj)
        server = AsyncRpcServer(
            self.host_and_ports,
            topic, handler,
            self.username, self.password
        )
        return server

    def client(self, topic, cls):
        return AsyncRpcClient(self.host_and_ports, topic, cls)

