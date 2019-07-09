import json
from copy import deepcopy
from functools import partial
from traceback import format_exc

import wf
from .context import Context
from wf.server.reactor import EventState


__all__ = [
    'Workflow',
    'Context'
]

'''
Workflow Feature
    trigger:
        1. event driven
        2. user interactive
    feature
        1. event listening with timeout
        2. sleep with timeout
        3. user decision
        4. workflow diagram for better visualization
'''


class ParamSource(object):
    event_tag = 0
    event_param = 1
    user = 2


class Parameter(object):
    def __init__(self, name, default=None, source=ParamSource.user, description=''):
        self.name = name
        self.default = default
        self.description = description
        self.source = source


class Package(object):
    def __init__(self, dir):
        self.dir = dir


class EventSubcription(object):
    def __init__(self, event_name, event_state):
        if event_state not in EventState.alls:
            raise Exception('value of event state must be one of: ' + ','.join(EventState.alls))
        self.name = event_name
        self.state = event_state

    def to_key(self):
        return self.name, self.state

    def to_json(self):
        return {
            'name': self.name,
            'state': self.state
        }

    @staticmethod
    def key_from_event(event):
        return event.name, event.state


class Workflow(object):

    EXCEP = 1
    MAX_TASK_RUN = 2

    def __init__(self, name, desc='', max_task_run=100):
        self.name = name
        self.desc = desc
        self._asking = False
        self._waited = False
        self._ending = False
        self._tasks = {}
        self._graph = {}
        self._ctx = None # assign before the workflow is to running
        self._max_task_run = max_task_run

        self._entrance = None
        self._req_params = {}
        self._req_event = None

    def instance(self, ctx=None, ctx_id=None):
        # TODO: what happen if ctx is not found with this ctx_id
        wf = deepcopy(self)
        if ctx is None:
            if ctx_id:
                ctx = Context.from_ctx_id(ctx_id)
            else:
                ctx = Context.new_context(wf)
        wf.set_ctx(ctx)
        return wf

    def log(self, msg, phase=None):
        self._ctx.log(msg, phase=phase)

    def sleep(self):
        pass

    def wait(self, event, to_state, timeout_ms, goto='', on_timeout=''):
        if to_state not in EventState.alls:
            raise Exception('to_state must be in the list of: ' + ','.join(EventState.alls))
        self._ctx.set_callback(goto, on_timeout)
        event_manager = wf.service_router.get_event_manager()
        event_manager.add_hook_for_event(event, self.get_id(), to_state, timeout_ms)
        self._waited = True

    def goto(self, next_task_name, reason=None):
        self._ctx.next_task = next_task_name

    def ask(self, desc, options, goto):
        self._ctx.create_decision(desc, *options)
        self._ctx.set_callback(goto, goto)
        self._asking = True

    def task(self, task_name, entrance=False, **to):
        self._graph[task_name] = to
        return partial(self.add_task, task_name, entrance=entrance, **to)

    def add_task(self, task_name, func, entrance=False, **to):
        self._graph[task_name] = to
        self._tasks[task_name] = func
        if entrance:
            self._entrance = task_name
        return func

    def parse_task_params(self, func):
        """
        TODO: this method is quite confused, because you need to understand the state
              between workflowBuilder, first workflow instance and workflow instance
              created on every request;
              calling order of task() and entrance()
        """
        inputs = []
        defs = func.func_defaults
        if defs is None:
            return inputs
        trg = self.get_trigger()
        params, event = trg.params, trg.event
        for param_def in defs:
            name, default, source = param_def.name, param_def.default, param_def.source
            if source == ParamSource.user and params:
                inputs.append(params.get(name, default))
            elif event is not None:
                if source == ParamSource.event_param:
                    inputs.append(event.params.get(name, default))
                elif source == ParamSource.event_tag:
                    inputs.append(event.tags.get(name, default))
                else:
                    inputs.append(default)
            else:
                inputs.append(default)
        return inputs

    def get_id(self):
        return self._ctx.id

    def set_ctx(self, ctx):
        if not ctx.next_task:
            # TODO: refact it because it goes wrong if we call set_ctx before adding
            # task to the workflow
            ctx.next_task = self._entrance
        self._ctx = ctx

    def get_ctx(self):
        return self._ctx

    def next_task(self):
        while not self._ending:
            next_task = self._ctx.next_task
            yield (next_task, self._tasks[next_task])

    def end(self):
        self._ending = True

    def should_wait(self):
        return self._waited

    def is_asking(self):
        return self._asking

    def make_decision(self, decision, comment):
        self._ctx.make_decision(decision, comment)

    def get_decision(self):
        return self._ctx.user_decision.decision

    def get_prop(self, key, default=None):
        return self._ctx.get_prop(key, default=default)

    def set_prop(self, key, value):
        self._ctx.set_prop(key, value)

    def before_resume(self):
        self._ctx.next_task = self._ctx.get_latest_callback()

    def execute(self, trigger):
        self.before_execute(trigger)

        flag, count = -1, 0
        ctx = self._ctx
        for task_name, task_func in self.next_task():
            if self.should_wait() or self.is_asking():
                break
            count += 1
            try:
                task_func(*self.parse_task_params(task_func))
            except:
                flag, msg = self.EXCEP, format_exc()
                ctx.log(msg)
                self.end()
            if count >= self._max_task_run:
                flag, msg = self.MAX_TASK_RUN, 'max task run exceeded'
                ctx.log('end due to max number of task run exceeded: ' + self._max_task_run)
                self.end()
            ctx.exec_history.append(task_name)
            print self.get_trigger()
            print self.get_trigger().to_json()
            ctx.save()
        if flag != -1:
            raise Exception(msg)

    def get_metadata(self):
        return {
            'name': self.name,
            'description': self.desc,
            'graph': self._graph,
            'entrance': self._entrance
        }

    def before_execute(self, trigger):
        self._update_trigger(trigger)
        print trigger
        print self._ctx.trigger

    def _update_trigger(self, trigger):
        tri = self._ctx.trigger
        if tri:
            tri.update(trigger)
        else:
            self._ctx.trigger = trigger

    def get_trigger(self):
        return self._ctx.trigger

    def set_state(self, state):
        self._ctx.state = state

    def get_id(self):
        return self._ctx.id

    def save(self):
        self._ctx.save()

    def validate(self):
        assert self._entrance is not None, 'entrance of the workflow must be defined'

    def __str__(self):
        return json.dumps(self._graph)
