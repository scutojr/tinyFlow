from time import sleep
from threading import Thread, RLock
from collections import defaultdict
from multiprocessing.pool import AsyncResult

import mongoengine as me

from wf.utils import now_ms


class Handler(object):
    def __init__(self, wf_builder, wf_executor):
        self.wf_builder = wf_builder
        self.wf_executor = wf_executor

    def handle(self, event=None, req=None, judgement=None):
        wf = self.wf_builder.build()
        wf.before_execute(event=event, req=req, judgement=judgement)
        return self.wf_executor.execute_async(wf)


class WorkflowDispatcher(object):
    def __init__(self, wf_executor):
        self.executor = wf_executor
        self.handlers = {}

    def attach(self, wf_builder):
        name = wf_builder.name
        self.handlers[name] = Handler(wf_builder, self.executor)

    def detach(self, wf_builder):
        name = wf_builder
        self.handlers.pop(name, None)

    def dispatch(self, wf_name, req=None, event=None):
        handler = self.handlers[wf_name]
        return [handler.handle(event=event, req=req)]


class EventDispatcher(object):
    def __init__(self, wf_executor):
        self.executor = wf_executor
        self.handlers = defaultdict(list)

    def attach(self, wf_builder):
        for sub in wf_builder.subscriptions:
            key = sub.to_key()
            handler = Handler(wf_builder, self.executor)
            self.handlers[key].append(handler)

    def detach(self, wf_builder):
        for sub in wf_builder.subscriptions:
            key = sub.to_key()
            # This not efficient, but it can remove redundant WorkflowBuilder
            # registered to the same event. It should be the responsibility of
            # WorkflowMangager, just in case
            self.handlers[key] = [o for o in self.handlers[key] if o.wf_builder == wf_builder]

    def dispatch(self, wf_name=None, req=None, event=None):
        key = event.general_key()
        results = []
        for h in self.handlers[key]:
            if wf_name and wf_name != h.wf_builder.name:
                continue
            r = h.handle(event=event, req=req)
            results.append(r)
        return results


class Reactor(Thread):
    def __init__(self, wf_executor):
        super(Reactor, self).__init__()
        self.running = False

        self.wf_executor = wf_executor
        self.lock = RLock()

        self.dispatcher_wf = WorkflowDispatcher(self.wf_executor)
        self.dispatcher_event = EventDispatcher(self.wf_executor)
        self.dispatcher_async_wf = None

    def attach_workflow(self, wf_builder):
        # TODO: concurrent problem?
        with self.lock:
            self.dispatcher_wf.attach(wf_builder)
            self.dispatcher_event.attach(wf_builder)

    def detach_workflow(self, wf_builder):
        # TODO: concurrent problem?
        with self.lock:
            self.dispatcher_wf.detach(wf_builder)
            self.dispatcher_event.detach(wf_builder)

    def dispatch_req(self, wf_name, req, event=None):
        return self.dispatcher_wf.dispatch(wf_name, req=req, event=event)

    def dispatch_event(self, event, wf_name=None, req=None):
        # TODO: how to deal with concurrent problom?
        with self.lock:
            key = event.general_key()
            results = self.dispatcher_event.dispatch(wf_name=wf_name, event=event, req=req)
            if self.dispatcher_async_wf:
                results += self.dispatcher_async_wf.dispatch_event(event)
            return results

    def dispatch_judgement(self, wf_id, judgement):
        return self.dispatcher_async_wf.dispatch_judgement(wf_id, judgement)

    def register_dispatcher_for_async_wf(self, dispatcher):
        self.dispatcher_async_wf = dispatcher

    def attach_async_workflow(self, async_wf_handler):
        self.dispatcher_async_wf.attach(async_wf_handler)

    def attach_judgement(self, judgement_handler):
        self.dispatcher_async_wf.attach(judgement_handler)

    def run(self):
        while self.running:
            now = now_ms()
            asyn_results = self.dispatcher_async_wf.handle_timeout(now)
            # TODO: log here
            sleep(1)

    def start(self):
        self.running = True
        super(Reactor, self).start()

    def stop(self, timeout=None):
        self.running = False
        self.join(timeout)
