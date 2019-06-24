import wf
from .workflow import Workflow


get_cur_wf = None


class WorkflowBuilder(object):
    def __init__(self, name, desc='', event_subscriptions=None):
        """
        :param name:
        :param desc:
        :param event_subscriptions:
        """
        from wf.executor import get_cur_wf
        global get_cur_wf

        get_cur_wf = get_cur_wf

        self._wf = Workflow(name,  desc=desc)
        if event_subscriptions is None:
            event_subscriptions = []
        self.event_subscriptions = event_subscriptions

    def log(self, msg):
        return get_cur_wf().log(msg)

    def goto(self, next_task_name, reason=None):
        return get_cur_wf().goto(next_task_name, reason)

    def wait(self, event, to_state, timeout_ms, goto='', on_timeout=''):
        return get_cur_wf().wait(event, to_state, timeout_ms, goto=goto, on_timeout=on_timeout)

    def ask(self, desc, options, goto):
        return get_cur_wf().ask(desc, options, goto)

    def get_decision(self):
        return get_cur_wf().get_decision()

    def get_property(self, name, namespace=''):
        return wf.service_router.get_prop_mgr.get_property(name=name, namespace=namespace)

    def get_prop(self, key, default=None):
        return get_cur_wf().get_prop(key, default)

    def set_prop(self, key, value):
        get_cur_wf().set_prop(key, value)

    def task(self, task_name, entrance=False, **to):
        return self._wf.task(task_name, entrance, **to)

    def add_task(self, task_name, func, entrance=False, **to):
        return self._wf.add_task(task_name, func, **to)

    def end(self):
        return get_cur_wf().end()

    def __str__(self):
        return str(self._wf)

    def wf(self):
        '''
    TODO: this method is obselete, use build() instead
    '''
        return self._wf

    def build(self):
        """
    TODO:
        1. check building validation such as entrace must be called to set up the entrace task
        2. after build is  called, changing to the wf is prevented
    """
        return self._wf

    def get_subscription_keys(self):
        return [
            s.to_key() for s in self.event_subscriptions
        ]

