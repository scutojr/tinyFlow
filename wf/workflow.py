import os
import json
from time import time
from copy import deepcopy
from imp import find_module, load_module
from functools import partial

import mongoengine as me


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
                    member = getattr(module, attr)
                    if isinstance(member, WorkflowBuilder):
                        wf = member.wf()
                        self._workflows[wf.name] = wf

    def get_workflows(self):
        return self._workflows.values()

    def get_workflow(self, name):
        wf = self._workflows.get(name, None)
        if wf:
            wf = deepcopy(wf)
        return wf


class Context(me.Document):
    # source event
    # [] props
    # [] log
    # id = me.StringField(primary_key=True)
    _id = me.ObjectIdField()
    wf_id = me.StringField(default='')
    props = me.DictField()
    msgs = me.ListField()

    def __init__(self, *args, **kwargs):
        super(Context, self).__init__(*args, **kwargs)

    def get_prop(self, key, default=None):
        return self.props.get(key, default)

    def set_prop(self, key, value):
        self.props[key] = value

    def save(self):
        super(Context, self).save()

    def log(self, msg, time_ms=None):
        self.msgs.append((time_ms or now_ms(), msg))
        # self.msgs.append(msg)


class Workflow(object):

    def __init__(self, name, ctx=None, desc=''):
        self.name = name
        self.desc = desc
        self._ending = False
        self._next_task = None
        self._tasks = {}
        self._graph = {}
        self.ctx = ctx if ctx else Context()

    def goto(self, next_task_name, reason=None):
        self._next_task = next_task_name

    def task(self, task_name, **to):
        self._graph[task_name] = to
        return partial(self.add_task, task_name, **to)

    def add_task(self, task_name, func, **to):
        if not self._next_task:
            self._next_task = task_name
        self._graph[task_name] = to
        self._tasks[task_name] = func

    def end(self):
        self._ending = True

    def get_ctx(self):
        return self.ctx

    @staticmethod
    def from_ctx(context):
        pass

    def next_task(self):
        while not self._ending:
            yield (self._next_task, self._tasks[self._next_task])

    def execute(self):
        count = 0
        for task_name, task_func in self.next_task():
            count += 1
            task_func()
            if count > 10:
                break

    def get_metadata(self):
        return {
            'name': self.name,
            'description': self.desc,
            'graph': self._graph
        }

    def __str__(self):
        return json.dumps(self._graph)


class WorkflowBuilder(object):
    def __init__(self, name, ctx=None, desc=''):
        self._wf = Workflow(name, ctx=ctx, desc=desc)

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
