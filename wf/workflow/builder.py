import sys

from .workflow import WorkFlow
from .base import BaseContext, BaseWorkFlow


class WorkFlowBuilder(BaseContext, BaseWorkFlow):
    def __init__(self, name, desc='', event_subscriptions=None):
        """
        :param name:
        :param desc:
        :param event_subscriptions:
        """
        self._wf = WorkFlow(name,  desc=desc)
        if event_subscriptions is None:
            event_subscriptions = []
        self.event_subscriptions = event_subscriptions

    def get_decision(self):
        get_cur_wf().get_decision()

    def task(self, task_name, **to):
        return self._wf.task(task_name, **to)

    def add_task(self, task_name, func, **to):
        self._wf.add_task(task_name, func, **to)

    def end(self):
        get_cur_wf().end()

    def wf(self):
        return self._wf

    def get_subscription_keys(self):
        return [
            s.to_key() for s in self.event_subscriptions
        ]

    def get_prop(self, key, default=None):
        get_cur_wf().get_prop(key, default)

    def set_prop(self, key, value):
        get_cur_wf().set_prop(key, value)

    def log(self, msg, time_ms=None):
        get_cur_wf().log(msg, time_ms)

    def goto(self, next_task_name, reason=None):
        get_cur_wf().goto(next_task_name, reason)

    def sleep(self, on_wakeup=None):
        pass

    def wait(self, event, to_state, timeout_ms=sys.maxint, on_receive=None, on_timeout=None):
        get_cur_wf().wait(event, to_state, timeout_ms, on_receive=on_receive, on_timeout=on_timeout)

    def ask(self, desc, options, default=None, **callbacks):
        get_cur_wf().ask(desc, options, default, **callbacks)

    def classify(self, *tags):
        pass

    def __str__(self):
        return str(self._wf)


from wf.execution.executor import get_cur_wf
