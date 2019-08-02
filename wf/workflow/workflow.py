import sys
import json
from copy import deepcopy
from functools import partial
from traceback import format_exc

from bson import ObjectId
import mongoengine as me

from wf.utils import now_ms
from wf.reactor.event import EventState
from .execution import *
from .log_processor import LogProcessor
from .trigger import TriggerChain
from .judgement import Judgement


class AsyncHandler(me.Document):
    wf_id = me.ObjectIdField()
    timestamp = me.IntField()

    on_fired = me.StringField()
    on_timeout = me.StringField()

    meta = {
        'allow_inheritance': True,
        'indexes': [
            'timestamp',
        ]
    }


class AsyncEventHandler(AsyncHandler):
    name = me.StringField()
    entity = me.StringField()
    state = me.StringField()

    @staticmethod
    def construct(event, to_state, wf_id, on_fired, on_timeout):
        # TODO: validate to_state
        n, e = event.name, event.entity
        handler = AsyncEventHandler(
            name=n, entity=e,
            state=to_state, wf_id=wf_id,
            on_fired=on_fired, on_timeout=on_timeout
        )
        return handler

    def _handle(self, wf_mgr, wf_executor, next_task, event=None):
        # TODO:
        #     during testing, I remove all workflow, which has some observers
        #     registered. After sending an event, those observers will raise
        #     an exception of no workflow found. Then the event sending request
        #     failed. I Think it's not good, the response should be hybrid and
        #     contains both correct and error result in the response
        wf = wf_mgr.get_workflow(wf_id=self.wf_id)
        wf.before_execute(next_task=next_task, event=event)
        result = wf_executor.execute_async(wf)
        return result

    def handle_fired(self, wf_mgr, wf_executor, event):
        return self._handle(wf_mgr, wf_executor, self.on_fired, event)

    def handle_timeout(self, wf_mgr, wf_executor):
        return self._handle(wf_mgr, wf_executor, self.on_timeout)


class JudgementHandler(AsyncHandler):
    judgement = me.EmbeddedDocumentField(Judgement)

    @staticmethod
    def construct(wf_id, judgement, on_fired, on_timeout=''):
        # TODO: support on_timeout
        jh = JudgementHandler(
            wf_id=wf_id,
            judgement=judgement,
            on_fired=on_fired,
            on_timeout=on_timeout
        )
        return jh

    def _handle(self, wf_mgr, wf_executor, next_task, judgement=None):
        wf = wf_mgr.get_workflow(wf_id=self.wf_id)
        wf.before_execute(next_task=next_task, judgement=judgement)
        result = wf_executor.execute_async(wf)
        return result

    def handle_fired(self, wf_mgr, wf_executor, judgement):
        return self._handle(wf_mgr, wf_executor, self.on_fired, judgement)

    def handle_timeout(self, wf_mgr, wf_executor):
        return self._handle(wf_mgr, wf_executor, self.on_timeout)


class Dispatcher(object):
    def __init__(self, wf_mgr, wf_executor):
        self.wf_mgr = wf_mgr
        self.wf_executor = wf_executor

    def attach(self, handler):
        handler.save()

    def detach(self, handler):
        handler.delete()

    def _dispatch(self, handlers, payload, is_timeout):
        results = []
        for h in handlers:
            if is_timeout:
                r = h.handle_timeout(self.wf_mgr, self.wf_executor)
            else:
                r = h.handle_fired(self.wf_mgr, self.wf_executor, payload)
            # TODO: if crash during the wf execution, this observer will lose forever
            self.detach(h)
            results.append(r)
        return results

    def dispatch_event(self, event, is_timeout=False):
        handlers = AsyncEventHandler.objects(
            name = event.name,
            entity = event.entity,
            state = event.state
        )
        return self._dispatch(handlers, event, is_timeout)

    def dispatch_judgement(self, wf_id, judgement, is_timeout=False):
        handlers = JudgementHandler.objects(wf_id=ObjectId(wf_id))
        return self._dispatch(handlers, judgement, is_timeout)

    def handle_timeout(self, before):
        handlers = AsyncHandler.objects(__raw__={'timestamp': {'$lte': before}})
        return self._dispatch(handlers, None, True)


class Workflow(me.Document):
    name = me.StringField()
    version = me.IntField()

    start = me.IntField(default=0)

    execution = me.EmbeddedDocumentField(Execution)
    logger = me.EmbeddedDocumentField(LogProcessor)
    tri_chain = me.EmbeddedDocumentField(TriggerChain)

    meta = {
        'indexes': [
            'start',
        ]
    }

    def construct(self, topology, reactor):
        self.topology = topology
        self.reactor = reactor

        if not self.id:
            self.logger = LogProcessor()
            self.execution = Execution(
                next_task=topology.entrance,
                wf_name=self.name
            )
            self.tri_chain = TriggerChain()
            self.start = now_ms()

    def ask(self, desc, options, on_fired):
        """
        TODO:
        1. update the state of execution
        2. not register a listener to reactor until current execution exit
        """
        if self.execution.state == STATE_WAITING:
            raise Exception('workflow is already in waiting state')
        options = [str(o) for o in options]
        judgement = Judgement(desc=desc, options=options)

        handler = JudgementHandler.construct(self.id, judgement, on_fired)
        self.reactor.attach_judgement(handler)

        self.execution.state = STATE_WAITING

    def wait(self, event, to_state, on_fired='', on_timeout='', timeout_ms=sys.maxint):
        # TODO: event may not so handy for user to use ? refact it to make wait method
        #       part of Event?
        # validate to_state, on_fired and on_timeout
        if self.execution.state == STATE_WAITING:
            raise Exception('workflow is already in waiting state')
        handler = AsyncEventHandler.construct(
            event, to_state, self.id,
            on_fired=on_fired,
            on_timeout=on_timeout
        )
        self.reactor.attach_async_workflow(handler)

        self.execution.state = STATE_WAITING

    def end(self):
        self.execution.end()

    def get_prop(self, key, default=None):
        return self.execution.get_prop(key, default=default)

    def set_prop(self, key, value):
        return self.execution.set_prop(key, value)

    def goto(self, task_name, reason=None):
        self.execution.goto(task_name)

    def set_next_task(self, next_task_name):
        self.execution.next_task = next_task_name

    def before_execute(self, next_task=None, event=None, judgement=None, req=None):
        next_task and self.set_next_task(next_task)
        self.tri_chain.add_trigger(event=event, req=req, judgement=judgement)

    def execute(self):
        logger = self.logger
        try:
            self.execution.execute(self.topology, self.tri_chain)
        except Exception as e:
            # TODO: the phase?
            logger.system(format_exc())
            raise e

    @property
    def state(self):
        return self.execution.state

    @property
    def state_str(self):
        return state_str(self.execution.state)

    @property
    def workflow_info(self):
        return self.topology.workflow_info()

    @staticmethod
    def get_judgement_handler(id):
        """
        :return: Judgement instancet or None if not found
        """
        return JudgementHandler.objects(id=ObjectId(id)).first()

    @staticmethod
    def get_judgement_handlers():
        """
        :return: iterable of Judgement instance
        """
        return JudgementHandler.objects()

    @staticmethod
    def get_execution(wf_id):
        wf = Workflow.objects(id=wf_id).only('execution').first()
        return wf and wf.execution

    @staticmethod
    def get_logger(wf_id):
        wf = Workflow.objects(id=wf_id).only('logger').first()
        return wf and wf.logger

