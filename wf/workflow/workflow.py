import sys
import json
from functools import partial
from traceback import format_exc

import mongoengine as me
from bson.objectid import ObjectId

import wf
from .task import Task
from wf.execution.wf_state import WfStates
from .base import BaseWorkFlow, BaseContext
from wf.server.reactor import Event, EventState


class Context(me.Document):
    pack = me.StringField(default='')
    wf = me.StringField(default='')
    version = me.IntField()

    props = me.DictField()

    tags = me.DictField()

    source_event = me.ReferenceField(Event)
    state = me.StringField(default='')

    tasks = me.ListField(me.EmbeddedDocumentField(Task))

    def __init__(self, *args, **kwargs):
        super(Context, self).__init__(*args, **kwargs)

    def get_prop(self, key, default=None):
        return self.props.get(key, default)

    def set_prop(self, key, value):
        self.props[key] = value

    def add_tag(self, *tags):
        for tag in tags:
            self.tags[tag] = ''

    def log(self, msg, time_ms=None):
        self.tasks[-1].log(msg, time_ms)

    def save(self):
        event = self.source_event
        if event and not event.id:
            event.save()
        super(Context, self).save()

    def set_current_task(self, name):
        self.tasks.append(Task.create(name))

    def get_current_task(self):
        if len(self.tasks) > 0:
            return self.tasks[-1]
        else:
            return None

    def set_callback(self, **on):
        self._ctx.get_current_task().set_callback(**on)

    def get_latest_callback(self, signal_name):
        return self.tasks[-1].callbacks[signal_name]

    def create_decision(self, desc, *options, **callbacks):
        self.tasks[-1].create_decision(desc, *options, **callbacks)

    def make_decision(self, decison, comment):
        return self.tasks[-1].make_decision(decison, comment)

    def get_decison(self):
        return self.tasks[-1].user_decision.decision

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


class WorkFlow(BaseWorkFlow, BaseContext):

    def __init__(self, name, desc='', max_task_run=100):
        self.name = name
        self.desc = desc
        self._asking = False
        self._waited = False
        self._ending = False
        self._default_start_task = None
        self._tasks = {}
        self._graph = {}
        self._ctx = None
        self._max_task_run = max_task_run

        self._pack_name = ''
        self._version = 0
        self._hash_code = 0

    def set_pack_info(self, pack_name, version):
        self._pack_name = pack_name
        self._version = version
        self._hash_code = hash(pack_name + '.' + self.name)

    def set_ctx(self, ctx):
        self._ctx = ctx
        ctx.pack = self._pack_name
        ctx.version = self._version
        if not ctx.get_current_task():
            self._ctx.set_current_task(name=self._default_start_task)

    @property
    def source_event(self):
        return self._ctx.source_event

    def save(self):
        self._ctx.save()

    def get_id(self):
        return self._ctx.id

    def get_decision(self):
        return self._ctx.get_decision()

    def make_decision(self, decision, comment=''):
        task_name = self._ctx.make_decision(decision, comment)
        self.goto(task_name)

    def task(self, task_name, **to):
        self._graph[task_name] = to
        return partial(self.add_task, task_name, **to)

    def add_task(self, task_name, func, **to):
        if not self._default_start_task:
            self._default_start_task = task_name
        self._graph[task_name] = to
        self._tasks[task_name] = func

    def end(self):
        self._ending = True

    def is_asking(self):
        return self._asking

    def should_wait(self):
        return self._waited

    def get_metadata(self):
        return {
            'name': self.name,
            'description': self.desc,
            'graph': self._graph
        }

    def on(self, signal):
        task_name = self._ctx.get_current_task().callbacks[signal]
        self.goto(task_name)

    def goto(self, next_task_name, reason=None):
        self._ctx.set_current_task(name=next_task_name)

    def ask(self, desc, options, default=None, **callbacks):
        self._ctx.create_decision(desc, *options, default=default, **callbacks)
        self._asking = True

    def wait(self, event, to_state, timeout_ms=sys.maxint, on_receive=None, on_timeout=None):
        if to_state not in EventState.alls:
            raise Exception('to_state must be in the list of: ' + ','.join(EventState.alls))
        self._ctx.get_current_task().set_callback(on_receive=on_receive, on_timeout=on_timeout)

        event_manager = wf.service_router.get_event_manager()
        event_manager.add_hook_for_event(event, self.get_id(), to_state, timeout_ms)

        self._waited = True

    def sleep(self, on_wakeup=None):
        # TODO
        pass

    def classify(self, *tags):
        self._ctx.add_tag(*tags)

    def get_prop(self, key, default=None):
        self._ctx.get_prop(key, default)

    def set_prop(self, key, value):
        self._ctx.set_prop(key, value)

    def log(self, msg, time_ms=None):
        self._ctx.log(msg, time_ms)

    def next_task(self):
        while not self._ending:
            yield self._ctx.get_current_task()

    def execute(self):
        count = 0
        ctx = self._ctx
        for task in self.next_task():
            task_name, task_func = task.name, self._tasks[task.name]
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
            ctx.save()
            if self.should_wait() or self.is_asking():
                break

    def __str__(self):
        return json.dumps(self._graph)

    def __hash__(self):
        return self._hash_code
