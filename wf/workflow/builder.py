import wf
from .workflow import Workflow


workflow = None


class WorkflowBuilder(object):
    def __init__(self, name, desc='', event_subscriptions=None):
        """
        :param name:
        :param desc:
        :param event_subscriptions:
        """
        from ..executor import workflow as wf
        global workflow

        workflow = wf

        self._wf = Workflow(name,  desc=desc)
        if event_subscriptions is None:
            _subscriptions = []
        self._subscriptions = event_subscriptions

    @property
    def name(self):
        return self._wf.name

    def log(self, msg):
        return workflow.log(msg)

    def goto(self, next_task_name, reason=None):
        return workflow.goto(next_task_name, reason)

    def wait(self, event, to_state, timeout_ms, goto='', on_timeout=''):
        return workflow.wait(event, to_state, timeout_ms, goto=goto, on_timeout=on_timeout)

    def ask(self, desc, options, goto):
        return workflow.ask(desc, options, goto)

    def get_decision(self):
        return workflow.get_decision()

    def get_property(self, name, namespace=''):
        return wf.service_router.get_prop_mgr.get_property(name=name, namespace=namespace)

    def get_prop(self, key, default=None):
        return workflow.get_prop(key, default)

    def set_prop(self, key, value):
        workflow.set_prop(key, value)

    def task(self, task_name, entrance=False, **to):
        return self._wf.task(task_name, entrance, **to)

    def add_task(self, task_name, func, entrance=False, **to):
        return self._wf.add_task(task_name, func, **to)

    def end(self):
        return workflow.end()

    @property
    def trigger(self):
        return workflow.get_trigger()

    def __str__(self):
        return str(self._wf)

    def build(self):
        """
        TODO:
            1. check building validation such as entrace must be called to set up the entrace task
            2. after build is  called, changing to the wf is prevented
        """
        return self._wf

    def get_subscriptions(self):
        return self._subscriptions
