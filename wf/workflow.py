import os
import json
from copy import deepcopy
from functools import partial
from traceback import format_exc
from collections import defaultdict
from imp import find_module, load_module

from bson.objectid import ObjectId
import mongoengine as me

import wf
from .utils import now_ms
from wf.server.reactor import Event, EventState, UserDecision


__all__ = [
    'Workflow',
    'Context'
]


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

    @staticmethod
    def key_from_event(event):
        return event.name, event.state


class WorkflowManager(object):
    def __init__(self, pack_dir):
        self.pack_dir = pack_dir
        self._workflows = {}
        self._handlers = defaultdict(list)
        self.load()

    def _get_pack(self):
        packs = os.listdir(self.pack_dir)
        return [pack for pack in packs if pack.endswith('.py')]

    def load(self):
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

    def set_callback(self, callback_name, on_timeout):
        self.callbacks.append((callback_name, on_timeout))

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

        self._start_task = None
        self._req_params = None
        self._req_event = None

    def wait(self, event, to_state, timeout_ms, goto='', on_timeout=''):
        if to_state not in EventState.alls:
            raise Exception('to_state must be in the list of: ' + ','.join(EventState.alls))
        self._ctx.callbacks.append((goto, on_timeout))
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
            self._start_task = task_name
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
        params, event = self.get_request()
        for param_def in defs:
            name, default, source = param_def.name, param_def.default, param_def.source
            if source == ParamSource.user:
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
            ctx.next_task = self._start_task
        self._ctx = ctx

    def set_request(self, params=None, event=None):
        self._req_params = params
        self._req_event = event

    def get_request(self):
        """
        :return: (dict, event)
        """
        return self._req_params, self._req_event

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

    def get_decision(self):
        return self._ctx.user_decision.decision

    def execute(self):
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
            ctx.save()
        if flag != -1:
            raise Exception(msg)

    def get_metadata(self):
        return {
            'name': self.name,
            'description': self.desc,
            'graph': self._graph
        }

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
        return get_cur_wf().goto(next_task_name, reason)

    def wait(self, event, to_state, timeout_ms, goto='', on_timeout=''):
        return get_cur_wf().wait(event, to_state, timeout_ms, goto=goto, on_timeout=on_timeout)

    def ask(self, desc, options, goto):
        return get_cur_wf().ask(desc, options, goto)

    def get_decision(self):
        return get_cur_wf().get_decision()

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

from .executor import get_cur_wf, WfStates
