#!/usr/bin/env python

import unittest

from mongoengine import connect

from wf.workflow import Workflow, Context
from wf.executor import WorkflowExecutor, context


class TestWorkFlow(unittest.TestCase):

    def setUp(self):
        db = 'test'
        host, port = 'mongo_test_server', 27017
        connect(db, host=host, port=port)

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
        wf.execute()
        ctx.save()
        for ctx in Context.objects():
            print ctx.msgs

    def test_wf_max_depth(self):
        pass

    def test_executor(self):
        print '===== test wf executor ====='
        executor = WorkflowExecutor(20)
        for i in range(2):
            wf = WorkflowBuilder.from_builder()
            print 'xxxxx =============='
            print 'xxxx:', executor.execute(wf)
            print 'xxxxx =============='


class WorkflowBuilder():

    @staticmethod
    def wf_and_context():
        wf = Workflow('TestWorkflow')
        ctx = context

        @wf.task('task start', **{
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

        @wf.task('task start', **{
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

        wf.add_task('task start', start, **{
            'succeed': 'task b',
            'fail': 'task c',
        })
        wf.add_task('task b', b)
        wf.add_task('task c', c)
        wf.add_task('task end', end)
        return wf


if __name__ == '__main__':
    unittest.main()
