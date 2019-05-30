from .workflow import WorkflowBuilder, EventSubcription
from .executor import ContextProxy


__all__ = [
    'context',
    'service_router',
    'WorkflowBuilder',
    'EventSubcription'
]


context = ContextProxy()


class ServiceRouter(object):
    # singleton

    def get_event_manager(self):
        return self.event_manager

    def set_event_manager(self, event_manager):
        self.event_manager = event_manager

    def get_wf_manager(self):
        return self.workflow_manager

    def set_wf_manager(self, workflow_manager):
        self.workflow_manager = workflow_manager

    def get_wf_executor(self):
        return self.wf_executor

    def set_wf_executor(self, wf_executor):
        self.wf_executor = wf_executor

    def get_prop_mgr(self):
        return self.prop_mgr

    def set_prop_mgr(self, prop_mgr):
        self.prop_mgr = prop_mgr


service_router = ServiceRouter()
