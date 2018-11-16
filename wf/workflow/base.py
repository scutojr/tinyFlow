from abc import abstractmethod
import sys


# TODO: workflow builder will inherit from BaseContext and BaseWorkflow

class BaseContext(object):
    @abstractmethod
    def get_prop(self, key, default=None):
        pass

    @abstractmethod
    def set_prop(self, key, value):
        pass

    @abstractmethod
    def log(self, msg, time_ms=None):
        pass


class BaseWorkFlow(object):

    @abstractmethod
    def task(self, task_name, **to):
        pass

    @abstractmethod
    def add_task(self, task_name, func, **to):
        pass

    @abstractmethod
    def goto(self, next_task_name, reason=None):
        pass

    @abstractmethod
    def sleep(self, on_wakeup=None):
        pass

    @abstractmethod
    def wait(self, event, to_state, timeout_ms=sys.maxint, on_receive=None, on_timeout=None):
        pass

    @abstractmethod
    def ask(self, desc, options, default=None, **callbacks):
        pass

    @abstractmethod
    def classify(self, *tags):
        pass

    @abstractmethod
    def end(self):
        pass
