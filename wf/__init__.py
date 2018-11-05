from .workflow import WorkflowBuilder
from .executor import ContextProxy


__all__ = [
    'context',
    'service_router',
    'WorkflowBuilder',
]

context = ContextProxy()


class ServiceRouter(object):
    # singleton

    def set_wf_manager(self, workflow_manager):
        self.workflow_manager = workflow_manager

    def get_wf_manager(self):
        return self.workflow_manager

    def get_wf_executor(self):
        return self.wf_executor

    def set_wf_executor(self, wf_executor):
        self.wf_executor = wf_executor


service_router = ServiceRouter()
