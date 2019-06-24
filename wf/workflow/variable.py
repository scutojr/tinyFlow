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
        wf = get_cur_wf()
        return wf.get_prop(self.name, default=default)

    def set(self, value):
        wf = get_cur_wf()
        wf.set_prop(self.name, value)

    def to_json():
        return {
            'name': self.name,
            'desc': self.desc,
            'scope': self.scope,
            'value': self.value
        }


from wf.executor import get_cur_wf
