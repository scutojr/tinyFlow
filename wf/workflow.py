import os
import json
from time import time
from copy import deepcopy
from functools import partial
from traceback import format_exc
from collections import defaultdict
from imp import find_module, load_module

import mongoengine as me

from wf.server.reactor import Event


__all__ = [
    'Workflow',
    'Context'
]


def now_ms():
    return int(time() * 1000)


class Package(object):
    def __init__(self, dir):
        self.dir = dir


class WorkflowManager(object):
    # discover and load workflow
    # singleton
    def __init__(self, pack_dir):
        self.pack_dir = pack_dir
        self._workflows = {}
        self._load()
        self._handlers = defaultdict(list)

    def _load(self):
        pathes = os.listdir(self.pack_dir)
        for path in pathes:
            if os.path.isfile(os.path.join(self.pack_dir, path)):
                suffix_index = path.rfind('.')
                if suffix_index > 0:
                    path = path[:suffix_index]
                file, pathname, desc = find_module(path, [self.pack_dir])
                module = load_module(path, file, pathname, desc)
                for attr in dir(module):
                    wfb = getattr(module, attr)
                    if isinstance(wfb, WorkflowBuilder):
                        wf = wfb.wf()
                        self._workflows[wf.name] = wf
                        for event_name in wfb.interested:
                            self._handlers[event_name].append(wf)

    def get_workflows(self):
        return self._workflows.values()

    def get_workflow(self, name):
        wf = self._workflows.get(name, None)
        if wf:
            wf = deepcopy(wf)
        return wf

    def get_wf_from_event(self, event_name):
        wfs = self._handlers[event_name]
        return deepcopy(wfs)


class UserDecision(me.Document):
    options = me.DictField()
    decision = me.StringField()
    comment = me.StringField()

    created_time = me.IntField()
    decided_time = me.IntField()

    def __init__(self, *args, **kwargs):
        super(UserDecision, self).__init__(*args, **kwargs)
        self.created_time = now_ms()

    def add_option(self, *option):
        for op in option:
            self.options[op] = ''

    def make_decision(self,  decision, comment=''):
        if decision not in self.options:
            raise Exception('decision from user is not in the list of options')
        self.decision = decision
        self.comment = comment
        self.decided_time = now_ms()


class Context(me.Document):
    wf = me.StringField(default='')
    props = me.DictField()
    msgs = me.ListField()

    source_event = me.ReferenceField(Event)
    exec_history = me.ListField(me.StringField())
    next_task = me.StringField(default='')
    state = me.StringField(default='')

    def __init__(self, *args, **kwargs):
        super(Context, self).__init__(*args, **kwargs)

    def get_prop(self, key, default=None):
        return self.props.get(key, default)

    def set_prop(self, key, value):
        self.props[key] = value

    def save(self):
        super(Context, self).save()

    def log(self, msg, time_ms=None):
        self.msgs.append((time_ms or now_ms(), self.next_task, msg))


class Workflow(object):

    def __init__(self, name, desc='', max_task_run=100):
        self.name = name
        self.desc = desc
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

    def end(self):
        self._ending = True

    def set_ctx(self, ctx):
        if not ctx.next_task:
            ctx.next_task = self._default_start_task
        self._ctx = ctx

    def next_task(self):
        while not self._ending:
            next_task = self._ctx.next_task
            yield (next_task, self._tasks[next_task])

    def execute(self):
        count = 0
        ctx = self._ctx
        for task_name, task_func in self.next_task():
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

    def __str__(self):
        return json.dumps(self._graph)


class WorkflowBuilder(object):
    def __init__(self, name, desc='', interested=None):
        """
        :param name:
        :param desc:
        :param interested: list of interested event name
        """
        self._wf = Workflow(name,  desc=desc)
        self.interested = interested if interested else []

    def goto(self, next_task_name, reason=None):
        get_cur_wf().goto(next_task_name, reason)

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


from .executor import get_cur_wf
