from ..executor import workflow

import wf


NS_WF = 'built-in:wf'
NS_OVERALL = 'built-in:overall'


class Scope(object):
    local = 'local'
    workflow = 'workflow'
    overall = 'overall'

    alls = [local, workflow, overall]


class Variable(object):
    def __init__(self, name, desc='', scope=Scope.local):
        self.name = name
        self.desc = desc
        self.scope = scope
        self._router = wf.service_router

        assert scope in Scope.alls, 'scope must be one of: ' + Scope.alls

    def get(self, default=None, workflow=workflow):
        s = self.scope
        name = self.name
        if s == Scope.local:
            return workflow.get_prop(name, default=default)
        elif s == Scope.workflow:
            ns = NS_WF
            name = workflow.name + ':' + name
        else:
            ns = NS_OVERALL
        return self._router.get_prop_mgr().get_value(name=name, namespace=ns) or default

    def set(self, value):
        s = self.scope
        name = self.name
        if s == Scope.local:
            return workflow.set_prop(name, value)
        elif s == Scope.workflow:
            ns = NS_WF
            name = workflow.name + ':' + name
        else:
            ns = NS_OVERALL
        return self._router.get_prop_mgr().update_property(name=name, namespace=ns, value=value)

    def to_json():
        return {
            'name': self.name,
            'desc': self.desc,
            'scope': self.scope,
        }

