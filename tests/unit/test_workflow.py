#!/usr/bin/env python

import time
import unittest
from itertools import cycle

from mock import Mock, patch

from wf.reactor.event import Event
from wf.workflow.judgement import Judgement
from wf.workflow.workflow import (
    Dispatcher,
    AsyncEventHandler,
    JudgementHandler,
)
from wf.workflow.builder import WorkflowBuilder
from wf.workflow.execution import STATE_SUCCEED
from wf.workflow import wf_proxy
import tests.utils.db as db


class TestDispatcher(unittest.TestCase):
    def setUp(self):
        db.connect()

        self.wf = WorkflowFactory.from_builder()
        self.wf.save()
        self.on_fired, self.on_timeout = 'fired_task', 'timeout_task'
        self.judgement = Judgement.construct(
            'for test purpose',
            ['option1', 'option2', 'option3']
        )

        self.wf_mgr, self.wf_executor = (
            Mock(**{'get_workflow.side_effect': cycle([self.wf])}),
            Mock(**{'execute_async.side_effect': cycle([('', '')])})
        )
        self.dispatcher = Dispatcher(self.wf_mgr, self.wf_executor)

        for h in self._event_handlers(self.wf) + self._judgement_handlers(self.wf):
            self.dispatcher.attach(h)

    def tearDown(self):
        db.drop(AsyncEventHandler, JudgementHandler)

    def _event_handlers(self, wf):
        handlers = [
            AsyncEventHandler.construct(
                event, 'info', wf.id, self.on_fired, self.on_timeout
            )
            for event in self._event_gen()
        ]
        return handlers

    def _judgement_handlers(self, wf):
        handler = JudgementHandler.construct(
            self.wf.id,
            self.judgement,
            self.on_fired,
            self.on_timeout
        )
        return [handler]

    def _event_gen(self):
        state = 'warning'
        names = ['event1', 'event2', 'event3']
        for n in names:
            yield Event(name=n, entity='dev-machine', state=state)

    def test_handler_attach_detach(self):
        self.assertTrue(AsyncEventHandler.objects().count() > 0)

    def test_dispatch_event(self):
        self.assertTrue(AsyncEventHandler.objects().count() > 0)
        cnt_judgement = JudgementHandler.objects().count()

        for event in self._event_gen():
            event.state = 'info'
            self.dispatcher.dispatch_event(event)
            self.assertTrue(self.wf.execution.next_task == self.on_fired)
            self.assertTrue(self.wf_mgr.get_workflow.call_count > 0)
            self.assertTrue(self.wf_executor.execute_async.call_count > 0)

        self.assertTrue(AsyncEventHandler.objects().count() == 0)
        self.assertTrue(JudgementHandler.objects().count() == cnt_judgement)

    def test_dispatch_judgement(self):
        cnt_event_handler = AsyncEventHandler.objects().count()
        self.assertTrue(JudgementHandler.objects().count() > 0)

        self.judgement.judge('option1')
        self.dispatcher.dispatch_judgement(self.wf.id, self.judgement)
        self.assertTrue(self.wf.execution.next_task == self.on_fired)
        self.assertTrue(self.wf_mgr.get_workflow.call_count > 0)
        self.assertTrue(self.wf_executor.execute_async.call_count > 0)

        self.assertTrue(JudgementHandler.objects().count() == 0)
        self.assertTrue(AsyncEventHandler.objects().count() == cnt_event_handler)


class TestWorkflowAsyncExecution(unittest.TestCase):

    def setUp(self):
        db.connect()

        self.handler = None
        self.wf = None
        self.trace = None

        class Trace(object):
            def __init__(self):
                self.is_start = False
                self.is_end = False
                self.is_timeout = False

        builder = WorkflowBuilder('test_async_event')

        trace = Trace()
        self.trace = trace
        event = Event(name='test_event', entity='dev', state='warning')

        @builder.task('start', entrance=True)
        def task_start():
            trace.is_start = True
            builder.wait(
                event, 'info',
                on_fired='end',
                on_timeout='timeout',
                timeout_ms = 5 * 1000
            )

        @builder.task('end')
        def task_end():
            trace.is_end = True
            builder.end()

        @builder.task('timeout')
        def task_timeout():
            trace.is_timeout = True
            builder.end()

        reactor = Mock(**{
            'attach_async_workflow.side_effect': (lambda h: setattr(self, 'handler', h))
        })
        builder.setup(123, reactor)

        self.wf = builder.build()
        wf_proxy.set_workflow(self.wf)

    def tearDown(self):
        pass

    def test_wait_event(self):
        # TODO: test trigger
        wf, t = self.wf, self.trace

        wf.execute()

        self.assertTrue(wf.state_str == 'waiting')
        wf.before_execute(self.handler.on_fired)
        wf.execute()

        self.assertTrue(self.wf.state_str == 'succeed')
        self.assertTrue(t.is_start and t.is_end and not t.is_timeout)

    def test_wait_event_timeout(self):
        wf, t = self.wf, self.trace

        wf.execute()

        self.assertTrue(wf.state_str == 'waiting')
        wf.before_execute(self.handler.on_timeout)
        wf.execute()

        self.assertTrue(self.wf.state_str == 'succeed')
        self.assertTrue(t.is_start and not t.is_end and t.is_timeout)

    def test_user_judgement(self):
        pass


class TestWorkflow(unittest.TestCase):

    def setUp(self):
        db.connect()

    def tearDown(self):
        db.disconnect()

    def test_wf_builder(self):
        wf = WorkflowFactory.from_builder()
        wf_proxy.set_workflow(wf)
        wf.execute()
        self.assertTrue(wf.state == STATE_SUCCEED)

    def test_wf_descriptor(self):
        wf = WorkflowFactory.from_descriptor()
        wf_proxy.set_workflow(wf)
        wf.execute()
        self.assertTrue(wf.state == STATE_SUCCEED)

    def test_wf_max_depth(self):
        builder = WorkflowBuilder('TestWorkflow')
        task_name = 'sole'

        def func():
          builder.goto(task_name)

        builder.add_task(task_name, func, entrance=True)
        wf = builder.build()
        wf_proxy.set_workflow(wf)
        try:
            wf.execute()
        except Exception as e:
            self.assertTrue('max number' in e.message)
        else:
            self.assertTrue(False)

    def test_immutable(self):
        builder = WorkflowBuilder('TestImmutable')
        builder.add_task('sole', lambda a: a, entrance=True)
        wf = builder.build()

        try:
            builder.add_task('another_task', lambda a: a)
        except Exception as e:
            self.assertTrue('immutable' in e.message)

    def test_workflow_entrance(self):
        order, expect = [], ['b', 'a', 'c']
        builder = WorkflowBuilder('TestWorkflow')

        @builder.task('a')
        def task_a():
            order.append('a')
            builder.goto('c')

        @builder.task('b', True)
        def task_b():
            order.append('b')
            builder.goto('a')

        @builder.task('c')
        def task_c():
            order.append('c')
            builder.end()

        wf = builder.build()
        wf_proxy.set_workflow(wf)

        wf.execute()
        self.assertTrue(order == expect)

    def test_set_get_prop(self):
        wf = WorkflowFactory.from_builder()
        wf_proxy.set_workflow(wf)
        props = {
            'p1': 'v1',
            'p2': 'v2',
            'p3': 'v3',
            'p4': 'v4'
        }
        for k, v in props.iteritems():
            wf.set_prop(k, v)
        for k in props:
            v = wf.get_prop(k)
            self.assertTrue(v == props[k])


class WorkflowFactory():

    @staticmethod
    def wf():
        wf = WorkflowBuilder('TestWorkflow')

        @wf.task('task start', entrance=True, **{
            'succeed': 'task b',
            'fail': 'task c',
        })
        def start():
            msg = 'I am task start. Go to task b.'
            wf.set_prop('task start', 'yes')
            wf.log(msg)
            wf.goto('task b')

        @wf.task('task b')
        def b():
            msg = 'I am b. Go to task end.'
            wf.set_prop('task b', 'yes')
            wf.log(msg)
            wf.goto('task end')

        @wf.task('task c')
        def c():
            msg = 'I am c. Go to task end.'
            wf.set_prop('task c', 'yes')
            wf.log(msg)
            wf.goto('task end')

        @wf.task('task end')
        def end():
            msg = 'This is end task'
            print 'show wf topology:', str(wf)
            wf.set_prop('task end', 'yes')
            wf.log(msg)
            wf.end()
        return wf.build()

    @staticmethod
    def from_descriptor():
        wf = WorkflowBuilder('TestWorkflow')

        @wf.task('task start', entrance=True, **{
            'succeed': 'task b',
            'fail': 'task c',
        })
        def start():
            print 'I am task start. Go to task b.'
            wf.goto('task b')

        @wf.task('task b')
        def b():
            print 'I am b. Go to task end.'
            wf.goto('task end')

        @wf.task('task c')
        def c():
            print 'I am c. Go to task end.'
            wf.goto('task end')

        @wf.task('task end')
        def end():
            print 'This is end task'
            print 'show wf topology:', str(wf)
            wf.end()
        return wf.build()


    @staticmethod
    def from_builder():
        wf = WorkflowBuilder('TestWorkflow')
        def start():
            print 'I am task start. Go to task b.'
            wf.goto('task b')

        def b():
            print 'I am b. Go to task end.'
            wf.goto('task end')

        def c():
            print 'I am c. Go to task end.'
            wf.goto('task end')

        def end():
            print 'This is end task'
            print 'show wf topology:', str(wf)
            wf.end()

        wf.add_task('task start', start, entrance=True, **{
            'succeed': 'task b',
            'fail': 'task c',
        })
        wf.add_task('task b', b)
        wf.add_task('task c', c)
        wf.add_task('task end', end)
        return wf.build()


if __name__ == '__main__':
    unittest.main()
