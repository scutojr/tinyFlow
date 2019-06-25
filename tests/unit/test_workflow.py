#!/usr/bin/env python

import unittest

from mongoengine import connect

from wf.server.reactor.event import Event
from wf.workflow import Workflow, Context, Parameter, ParamSource
from wf.executor import SimpleExecutor, MultiThreadExecutor

import tests.utils.db as db


class TestWorkFlow(unittest.TestCase):

    def setUp(self):
        db.connect()

    def tearDown(self):
        db.disconnect()

    def test_wf_builder(self):
        print '===== test wf builder ====='
        wf = WorkflowBuilder.from_builder()
        wf.execute()

    def test_wf_descriptor(self):
        print '===== test wf descriptor ====='
        wf = WorkflowBuilder.from_descriptor()
        wf.execute()

    def test_wf_ctx(self):
        wf, ctx = WorkflowBuilder.wf_and_context()
        wf.set_ctx(ctx) # TODO: can we hide or decrease the calling of set_ctx?
        wf.execute()
        ctx.save()
        for ctx in Context.objects():
            print ctx.msgs

    def test_wf_max_depth(self):
        pass

    def test_workflow_entrance(self):
        order = [0]
        args = {
            'var_1': 111,
            'var_2': 222
        }
        event = Event(tags={'cluster': 'gz'})

        wf = Workflow('TestWorkflow')

        @wf.task('a')
        def task_a():
            order[0] += 1
            self.assertTrue(order[0] == 2)
            wf.goto('c')

        @wf.task('b', True)
        def task_b(
            param1 = Parameter('var_1', 1),
            param2 = Parameter('var_2', 2),
            param3 = Parameter('var_3', 3),
            param4 = Parameter('cluster', 'bj', ParamSource.event_tag)
        ):
            order[0] += 1
            self.assertTrue(order[0] == 1)
            self.assertTrue(param1 == args['var_1'])
            self.assertTrue(param2 == args['var_2'])
            self.assertTrue(param3 == 3) # test default value
            self.assertTrue(param4 == event.tags['cluster'])
            wf.goto('a')

        @wf.task('c')
        def task_c():
            order[0] += 1
            self.assertTrue(order[0] == 3)
            wf.end()

        wf.set_request(args, event)
        wf.set_ctx(Context())
        wf.execute()
        self.assertTrue(order[0] == 3)

    def test_executor(self):
        print '===== test wf executor ====='
        simple_executor = SimpleExecutor()
        multi_thread_exct = MultiThreadExecutor()

        for i in range(2):
            wf = WorkflowBuilder.from_builder()
            for exct in [simple_executor, multi_thread_exct]:
                exct.execute(wf)

    def test_set_get_prop(self):
        wf = WorkflowBuilder.from_builder()
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


class WorkflowBuilder():

    @staticmethod
    def wf_and_context():
        wf = Workflow('TestWorkflow')
        ctx = Context()

        @wf.task('task start', entrance=True, **{
            'succeed': 'task b',
            'fail': 'task c',
        })
        def start():
            msg = 'I am task start. Go to task b.'
            ctx.set_prop('task start', 'yes')
            ctx.log(msg)
            wf.goto('task b')

        @wf.task('task b')
        def b():
            msg = 'I am b. Go to task end.'
            ctx.set_prop('task b', 'yes')
            ctx.log(msg)
            wf.goto('task end')

        @wf.task('task c')
        def c():
            msg = 'I am c. Go to task end.'
            ctx.set_prop('task c', 'yes')
            ctx.log(msg)
            wf.goto('task end')

        @wf.task('task end')
        def end():
            msg = 'This is end task'
            print 'show wf topology:', str(wf)
            ctx.set_prop('task end', 'yes')
            ctx.log(msg)
            wf.end()
        return wf, ctx

    @staticmethod
    def from_descriptor():
        wf = Workflow('TestWorkflow')

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
        wf.set_ctx(Context())
        return wf


    @staticmethod
    def from_builder():
        wf = Workflow('TestWorkflow')
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
        wf.set_ctx(Context())
        return wf


if __name__ == '__main__':
    unittest.main()
