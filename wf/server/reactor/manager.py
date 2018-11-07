from threading import Thread


class AMQListener(object):
    pass


class EventManager(Thread):
    # dispatch the event to the specific wf
    # dispatch the user decision to the specific wf
    # periodically to remove the timeout event and trigger timeout event if needed

    def __init__(self, wf_manager, wf_executor):
        self.wf_manager = wf_manager
        self.wf_executor = wf_executor

    def run(self):
        pass

    def dispatch(self, event):
        wfs = self.wf_manager.get_wf_from_event(event.name)
        for wf in wfs:
            self.wf_executor.execute()