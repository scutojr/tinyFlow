import json
import time
import uuid
from functools import partial


__all__ = [
    'context',
    'Workflow'
]


def ctx_proxy():
    # refact it to return a proxy context
    return Context()


class Context(object):
    def __init__(self,
            wf_id=None, curr_task=0,
            persist_dir='/var/workflow',
            params=None
    ):
        self.wf = None
        self.props = {}
        self.wf_id = wf_id
        self.curr_task = curr_task
        self.persist_dir = persist_dir
        self.params = params if params is not None else {}

    def get_wf(self):
        return self.wf

    def set_wf(self, workflow):
        self.wf = workflow

    def _load_context(self, wf_id):
        pass

    def get_prop(self, task_name=None):
        pass

    def set_prop(self, name, value):
        self.props[name] = value

    def save(self):
        if not self.wf_id:
            self.wf_id = str(uuid.uuid1())
        data = {
            'props': self.props,
            'wf_id': self.wf_id,
            'persist_dir': self.persist_dir,
            'curr_task': self.curr_task
        }
        with open(self.persist_dir + '/' + self.wf_id, 'w') as sink:
            json.dump(data, sink)

    def log(self, msg):
        pass

    @staticmethod
    def load(wf_id):
        ctx = Context()
        ctx._load_context(wf_id)
        return ctx

    def dump(self):
        return json.dumps(self.props) 


class Workflow(object):

    def __init__(self, name, ctx=None):
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
        for task_name, task_func in self.next_task():
            print 'executing: ', task_name
            task_func()

    def __str__(self):
        return json.dumps(self._graph)


context = ctx_proxy()