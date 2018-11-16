from time import time, sleep
from threading import Thread

import mongoengine as me

from wf.utils import *
from .event import Event, EventWithHook


def now_ms():
    return int(time() * 1000)


class AMQListener(object):
    pass


class TimerHook(me.Document):
    wf_id = me.ObjectIdField()
    wakeup_stamp = me.IntField()

    _meta = {
        'indexes': {
            'wakeup_stamp'
        }
    }


class EventManager(Thread):
    # dispatch the event to the specific wf
    # dispatch the user decision to the specific wf
    # periodically to remove the timeout event and trigger timeout event if needed

    def __init__(self, wf_manager):
        self.wf_manager = wf_manager
        self._timer_running = False

    def add_hook_for_event(self, event, ctx_id, to_state, duration_ms):
        event_with_hook = EventWithHook.from_event(event, to_state, ctx_id, now_ms() + duration_ms)
        event_with_hook.save()

    def get_hooks(self, event):
        """

        :param event:
        :return: list of (wf, ctx)
        """
        # import pudb
        # pudb.set_trace()
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

    def sleep(self, wf_id, timeout_sec):
        # TODO: if a wf call sleep multiple time at the same method, what should we do?
        TimerHook(wf_id=wf_id, wakeup_stamp=now_s() + timeout_sec).save()

    def _clean_timeout_hook(self):
        pass

    def _start_timer(self):
        def run():
            self._timer_running = True
            while self._timer_running:
                for timer_hook in TimerHook.objects(wakeup_stamp__gt=now_s()):
                    wf_id = timer_hook.wf_id
                    # TODO: call executor method to run the wf from wf_id again
                sleep(1)
        self._timer = Thread(target=run)
        self._timer.setDaemon(True)
        self._timer.start()

    def _stop_timer(self):
        self._timer_running = False
        self._timer.join()

    def start(self):
        self._start_timer()

    def stop(self):
        self._stop_timer()

    @staticmethod
    def build_event():
        pass
