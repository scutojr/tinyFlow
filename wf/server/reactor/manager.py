from threading import Thread

from .event import Event, EventWithHook
from wf.utils import now_ms


class AMQListener(object):
    pass


class EventManager(Thread):
    # dispatch the event to the specific wf
    # dispatch the user decision to the specific wf
    # periodically to remove the timeout event and trigger timeout event if needed

    def __init__(self, wf_manager):
        self.wf_manager = wf_manager

    def add_hook_for_event(self, event, ctx_id, to_state, duration_ms):
        event_with_hook = EventWithHook.from_event(event, to_state, ctx_id, now_ms() + duration_ms)
        event_with_hook.save()

    def receive_event(self, event=None, wf_name=None, extra_params=None):
        """
        :return: [list of wf id, list of AsyncResult]
        """
        ids = []
        async_res = []
        new_wfs = wf_manager.get_wf_from_event(event)
        hooks = self.get_hooks(event)

        if wf_name:
            new_wfs = filter(lambda wf: wf.name == wf_name, new_wfs)
            hooks = filter(lambda hook: hook[0].name == wf_name, hooks)

        for wf in new_wfs:
            wf.set_request(extra_params, event)
            ctx_id, async_result = wf_executor.execute_async(wf, event)
            ids.append(str(ctx_id))
            async_res.append(async_result)
        for wf, ctx in hooks:
            wf.set_request(extra_params, event)
            _, async_result = wf_executor.execute_async(wf, event, ctx)
            ids.append(str(ctx.id))
            async_res.append(async_result)
        return ids, async_res

    def get_hooks(self, event):
        """
        :param event:
        :return: list of (wf, ctx)
        """
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

        hooks = []
        for ewh in ewhs:
            ctx_id = ewh.ctx_id
            wf, ctx = self.wf_manager.get_wf_ctx(ctx_id)
            ctx.next_task = ctx.get_latest_callback()
            hooks.append((wf, ctx))

            ewh.is_processed = True
            ewh.save()
        return hooks

    def _clean_timeout_hook(self):
        pass

    def run(self):
        pass

    @staticmethod
    def build_event():
        pass
