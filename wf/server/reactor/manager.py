from threading import Thread

from .event import Event
from .hook import EventWithHook
from wf.utils import now_ms


class EventManager(Thread):
    # dispatch the event to the specific wf
    # dispatch the user decision to the specific wf
    # periodically to remove the timeout event and trigger timeout event if needed

    def __init__(self, wf_manager, wf_executor):
        self.wf_manager = wf_manager
        self.wf_executor = wf_executor
        self.running = False

    def add_hook_for_event(self, event, ctx_id, to_state, duration_ms):
        event_with_hook = EventWithHook.from_event(event, to_state, ctx_id, now_ms() + duration_ms)
        event_with_hook.save()

    def receive_event(self, event=None, wf_name=None, extra_params=None):
        """
        :return: [list of wf id, list of AsyncResult]
        """
        ids, wfs, async_res = [], [], []

        # TODO: this condition block is ugly, please redesign this interface
        if event is not None:
            wfs.extend(self.wf_manager.get_wf_from_event(event))
            wfs.extend(self.get_wf_from_event(event))
            if wf_name:
                wfs = filter(lambda wf: wf.name == wf_name, wfs)
        else:
            wfs.append(self.wf_manager.get_workflow(wf_name))

        for wf in wfs:
            wf.set_request(extra_params, event)
            ctx_id, async_result = self.wf_executor.execute_async(wf)
            ids.append(str(ctx_id))
            async_res.append(async_result)
        return ids, async_res

    def get_wf_from_event(self, event):
        """
        :param event:
        :return: list of (wf, ctx)
        """
        if event is None:
            return []
        qry = {
            'name': event.name,
            'entity': event.entity,
            'state': event.state,
            'tags': {
                key: value for key, value in event.tags.items()
            },
            'is_processed': False
        }
        ewhs = EventWithHook.objects(__raw__=qry)

        wfs = []
        for ewh in ewhs:
            ctx_id = ewh.ctx_id
            wf = self.wf_manager.get_wf_from_ctx(ctx_id)
            wf.before_resume()
            wfs.append(wf)

            ewh.is_processed = True
            ewh.save()
        return wfs

    def dispatch(self, trigger):
        '''
        case of triggering a workflow:
            1. http request. Its state is static.
            2. on event entering and state change. state is both static and dynamic.
                current method:
                    register a hook in the event manager
                    hook: goto, on_timeout
                    after finishing: remove the hook
                user decision:
                    register a user decision hook in event manager
            3. timer event. state is both static and dynamic
        static state is easy;
        dynamic state need to record the state on mongodb.
        '''
        # import pudb
        # pudb.set_trace()

        wfs = trigger.get_workflow(self, self.wf_manager)

        ids, async_res = [], []
        for wf in wfs:
            ctx_id, async_result = self.wf_executor.execute_async(wf, trigger)
            ids.append(str(ctx_id))
            async_res.append(async_result)
        return ids, async_res

    def run(self):
        pass

    def start(self):
        self.running = True
        super(EventManager, self).start()

    def stop_and_join(self):
        self.running = True
        self.join()

