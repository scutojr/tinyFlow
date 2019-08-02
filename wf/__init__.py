__all__ = [
    'service_router',
    'WorkflowBuilder',
    'Subscription'
]


class ServiceRouter(object):
    # singleton

    def get_reactor(self):
        return self.reactor

    def set_reactor(self, reactor):
        self.reactor = reactor

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

    def get_event_listener(self):
        return self.event_listener

    def set_event_listener(self, listener):
        self.event_listener = listener

    def get_http_server(self):
        return self.server

    def set_http_server(self, server):
        self.server = server


service_router = ServiceRouter()


from .workflow import WorkflowBuilder, Subscription
