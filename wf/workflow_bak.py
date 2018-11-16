import os
import json
from time import time
from copy import deepcopy
from functools import partial
from traceback import format_exc
from collections import defaultdict
from imp import find_module, load_module

from bson.objectid import ObjectId
import mongoengine as me

import wf
from wf.server.reactor import Event, EventState, UserDecision


__all__ = [
    'Workflow',
    'Context'
]


def now_ms():
    return int(time() * 1000)


class EventSubcription(object):
    def __init__(self, event_name, event_state):
        if event_state not in EventState.alls:
            raise Exception('value of event state must be one of: ' + ','.join(EventState.alls))
        self.name = event_name
        self.state = event_state

    def to_key(self):
        return self.name, self.state

    @staticmethod
    def key_from_event(event):
        return event.name, event.state


class WorkflowManager(object):
    def __init__(self, pack_dir):
        self.pack_dir = pack_dir
        self._workflows = {}
        self._handlers = defaultdict(list)

        self._load()

    def _get_pack(self):
        packs = os.listdir(self.pack_dir)
        return [pack for pack in packs if pack.endswith('.py')]

    def _load(self):
        for pack in self._get_pack():
            if os.path.isfile(os.path.join(self.pack_dir, pack)):
                suffix_index = pack.rfind('.')
                if suffix_index > 0:
                    pack = pack[:suffix_index]
                file, pathname, desc = find_module(pack, [self.pack_dir])
                module = load_module(pack, file, pathname, desc)
                for attr in dir(module):
                    wfb = getattr(module, attr)
                    if isinstance(wfb, WorkflowBuilder):
                        wf = wfb.wf()
                        self._workflows[wf.name] = wf
                        for key in wfb.get_subscription_keys():
                            self._handlers[key].append(wf)

    def get_workflows(self):
        return self._workflows.values()

    def get_workflow(self, name):
        wf = self._workflows.get(name, None)
        if wf:
            wf = deepcopy(wf)
        return wf

    def get_wf_from_event(self, event):
        """
        :param event:
        :return: list of matching workflow instance
        """
        key = EventSubcription.key_from_event(event)
        wfs = self._handlers[key]
        return deepcopy(wfs)

    def get_wf_ctx(self, ctx_id):
        ctx = Context.objects(id=ctx_id).first()
        wf = self.get_workflow(ctx.wf)
        return wf, ctx


class Context(me.Document):
    wf = me.StringField(default='')
    props = me.DictField()
    msgs = me.ListField()

    source_event = me.ReferenceField(Event)
    exec_history = me.ListField(me.StringField())
    next_task = me.StringField(default='')
    state = me.StringField(default='')

    callbacks = me.ListField()

    user_decision = me.EmbeddedDocumentField(UserDecision)

    def __init__(self, *args, **kwargs):
        super(Context, self).__init__(*args, **kwargs)

    def get_prop(self, key, default=None):
        return self.props.get(key, default)

    def set_prop(self, key, value):
        self.props[key] = value

    def save(self):
        event = self.source_event
        if event and not event.id:
            event.save()
        super(Context, self).save()

    def log(self, msg, time_ms=None):
        self.msgs.append((time_ms or now_ms(), self.next_task, msg))

    def set_callback(self, by_default, on_timeout):
        self.callbacks.append((by_default, on_timeout))

    def get_latest_callback(self, timeout=False):
        if timeout:
            return self.callbacks[-1][1]
        else:
            return self.callbacks[-1][0]

    def create_decision(self, desc, *options):
        self.user_decision = UserDecision(desc=desc, options=options)

    def make_decision(self, decison, comment):
        self.user_decision.make_decision(decison, comment)
        self.next_task = self.callbacks[-1][0]

    @staticmethod
    def new_context(workflow):
        return Context(wf=workflow.name)

    @staticmethod
    def from_ctx_id(ctx_id):
        return Context.objects(id=ObjectId(ctx_id)).first()

    @staticmethod
    def get_asking_context():
        """
        :return: list of context that is asking user for decision
        """
        return Context.objects(state=WfStates.asking.state)


class Workflow(object):

    def __init__(self, name, desc='', max_task_run=100):
        self.name = name
        self.desc = desc
        self._asking = False
        self._waited = False
        self._ending = False
        self._default_start_task = None
        self._tasks = {}
        self._graph = {}
        self._ctx = None # assign before the workflow is to running
        self._max_task_run = max_task_run

    def goto(self, next_task_name, reason=None):
        self._ctx.next_task = next_task_name

    def task(self, task_name, **to):
        self._graph[task_name] = to
        return partial(self.add_task, task_name, **to)

    def add_task(self, task_name, func, **to):
        if not self._default_start_task:
            self._default_start_task = task_name
        self._graph[task_name] = to
        self._tasks[task_name] = func

    def get_id(self):
        return self._ctx.id

    def end(self):
        self._ending = True

    def wait(self, event, to_state, timeout_ms, goto='', on_timeout=''):
        if to_state not in EventState.alls:
            raise Exception('to_state must be in the list of: ' + ','.join(EventState.alls))
        self._ctx.callbacks.append((goto, on_timeout))
        event_manager = wf.service_router.get_event_manager()
        event_manager.add_hook_for_event(event, self.get_id(), to_state, timeout_ms)
        self._waited = True

    def set_ctx(self, ctx):
        if not ctx.next_task:
            ctx.next_task = self._default_start_task
        self._ctx = ctx

    def next_task(self):
        while not self._ending:
            next_task = self._ctx.next_task
            yield (next_task, self._tasks[next_task])

    def should_wait(self):
        return self._waited

    def execute(self):
        count = 0
        ctx = self._ctx
        for task_name, task_func in self.next_task():
            if self.should_wait() or self.is_asking():
                break
            count += 1
            try:
                task_func()
            except:
                error = format_exc()
                ctx.log(error)
                self.end()
            if count >= self._max_task_run:
                ctx.log('end due to max number of task run exceeded: ' + self._max_task_run)
                self.end()
            ctx.exec_history.append(task_name)
            ctx.save()

    def get_metadata(self):
        return {
            'name': self.name,
            'description': self.desc,
            'graph': self._graph
        }

    def is_asking(self):
        return self._asking

    def ask(self, desc, options, goto):
        self._ctx.create_decision(desc, *options)
        self._ctx.set_callback(goto, goto)
        self._asking = True

    def get_decision(self):
        return self._ctx.user_decision.decision

    def __str__(self):
        return json.dumps(self._graph)


class WorkflowBuilder(object):
    def __init__(self, name, desc='', event_subscriptions=None):
        """
        :param name:
        :param desc:
        :param event_subscriptions:
        """
        self._wf = Workflow(name,  desc=desc)
        if event_subscriptions is None:
            event_subscriptions = []
        self.event_subscriptions = event_subscriptions

    def goto(self, next_task_name, reason=None):
        get_cur_wf().goto(next_task_name, reason)

    def wait(self, event, to_state, timeout_ms, goto='', on_timeout=''):
        get_cur_wf().wait(event, to_state, timeout_ms, goto=goto, on_timeout=on_timeout)

    def ask(self, desc, options, goto):
        get_cur_wf().ask(desc, options, goto)

    def get_decision(self):
        get_cur_wf().get_decision()

    def task(self, task_name, **to):
        return self._wf.task(task_name, **to)

    def add_task(self, task_name, func, **to):
        self._wf.add_task(task_name, func, **to)

    def end(self):
        get_cur_wf().end()

    def __str__(self):
        return str(self._wf)

    def wf(self):
        return self._wf

    def get_subscription_keys(self):
        return [
            s.to_key() for s in self.event_subscriptions
        ]


from wf.execution.executor import get_cur_wf, WfStates
