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

        self.wf_executor = wf_executor
        self.lock = RLock()

        self.dispatcher_wf = WorkflowDispatcher(self.wf_executor)
        self.dispatcher_event = EventDispatcher(self.wf_executor)
        self.dispatcher_async_wf = None

    '========================================='
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

    '========================================='

    def register_dispatcher_for_async_wf(self, dispatcher):
        self.dispatcher_async_wf = dispatcher

    def attach_async_workflow(self, async_wf_handler):
        self.dispatcher_async_wf.attach(async_wf_handler)

    def attach_judgement(self, judgement_handler):
        self.dispatcher_async_wf.attach(judgement_handler)

    '========================================='

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
        wfs = trigger.get_workflow(self, self.wf_manager)

        ids, async_res = [], []
        for wf in wfs:
            ctx_id, async_result = self.wf_executor.execute_async(wf, trigger)
            ids.append(str(ctx_id))
            async_res.append(async_result)
        return ids, async_res

