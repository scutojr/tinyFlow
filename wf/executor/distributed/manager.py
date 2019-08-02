from .consumer import Consumer
import routing_key as key
from wf.utils import now_ms


class Handler(object):
    def __init__(self, manager):
        self.mgr = manager
        self.mapper = {
            key.RUNNER_HEARTBEAT: self.magr.heartbeat
        }

    def handle(self, message):
        m = self.mapper(message.pop('key'))
        m and m(**message)


class Runner(object):
    def __init__(self, hostname, last=None):
        self.hostname = hostname
        self.last = now_ms()


class RunnerManager(object):
    def __init__(self):
        self._runners = {}

    def add_runner(self, hostname):
        self._runners[hostname] = Runner(hostname)

    def remove_runner(self, hostname):
        self._runners.pop(hostname, None)

    def list_runner(self):
        return self._runners.itervalues()

    def heartbeat(self, hostname):
        runner = self._runners.get(hostname, None)
        if not runner:
            runner = Runner(hostname)
            self._runners[hostname] = runner
        runner.last = now_ms()

    def handler(self):
        return Handler(self)
