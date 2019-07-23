from traceback import format_exc

import mongoengine as me


MAX_TASK_RUN = 100

STATE_SCHEDULING = 1 << 1
STATE_RUNNING = 1 << 2
STATE_WAITING = 1 << 3
STATE_TIMEOUT = 1 << 4
STATE_SUCCEED = 1 << 5
STATE_FAILED = 1 << 6

STATE_MAPPING = {
    STATE_SCHEDULING: 'scheduling',
    STATE_RUNNING: 'running',
    STATE_WAITING: 'waiting',
    STATE_TIMEOUT: 'timeout',
    STATE_SUCCEED: 'succeed',
    STATE_FAILED: 'failed'
}


def state_str(state):
    return STATE_MAPPING.get(state, 'unknown')


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


class Execution(me.EmbeddedDocument):
    wf_name = me.StringField(default='')
    props = me.DictField()
    exec_history = me.ListField(me.StringField())
    next_task = me.StringField(default='')

    state = me.IntField(default=STATE_SCHEDULING)
    exception = me.StringField(default='')

    @property
    def state_str(self):
        return state_str(self.state)

    def tasks(self):
        """
        :yield : task_name
        """
        while self.is_running():
            t = self.next_task
            self.next_task = None
            yield t

    def execute(self, topology, tri_chain):
        """
        :except:
        """
        flag, count = False, 0
        self.state = STATE_RUNNING
        for task_name in self.tasks():
            count += 1
            try:
                func = topology.get_task(task_name)
                func(*self.parse_task_params(func, tri_chain))
            except:
                flag = True
                self.state, self.exception = STATE_FAILED, format_exc()
            if count >= MAX_TASK_RUN:
                flag = True
                self.state = STATE_FAILED
                self.exception = (
                    'end due to max number of task run exceeded: '
                    + str(MAX_TASK_RUN)
                )
            self.exec_history.append(task_name)
            self.save()
        if flag:
            raise Exception(self.exception)

    def goto(self, task, reason=None):
        self.next_task = task

    def is_running(self):
        return (self.state & STATE_RUNNING) == STATE_RUNNING

    def get_prop(self, key, default=None):
        return self.props.get(key, default)

    def set_prop(self, key, value):
        self.props[key] = value

    def end(self):
        self.state = STATE_SUCCEED

    def parse_task_params(self, func, tri_chain):
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
        req, event = tri_chain.request, tri_chain.event
        for param_def in defs:
            name, default, source = param_def.name, param_def.default, param_def.source
            if source == ParamSource.user and req:
                inputs.append(req.get(name, default))
            elif event is not None:
                if source == ParamSource.event_param:
                    inputs.append(event.req.get(name, default))
                elif source == ParamSource.event_tag:
                    inputs.append(event.tags.get(name, default))
                else:
                    inputs.append(default)
            else:
                inputs.append(default)
        return inputs
