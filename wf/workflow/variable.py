from ..executor import workflow


class Scope(object):
    local = 'local'
    workflow = 'workflow'
    overall = 'overall'


class Variable(object):
    def __init__(self, name, desc='', scope=Scope.local):
        self.name = name
        self.desc = desc
        self.scope = scope
        self.value = None

    def get(self, default=None):
        return workflow.get_prop(self.name, default=default)

    def set(self, value):
        workflow.set_prop(self.name, value)

    def to_json():
        return {
            'name': self.name,
            'desc': self.desc,
            'scope': self.scope,
            'value': self.value
        }

