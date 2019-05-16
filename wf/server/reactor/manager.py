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
