#!/usr/bin/env python

import unittest

from mongoengine import connect
from bson.objectid import ObjectId

from wf.workflow import WorkFlow, Context
from wf.execution.executor import WorkflowExecutor


class TestWorkFlow(unittest.TestCase):

    def setUp(self):
        db = 'test'
        host, port = 'mongo_test_server', 27017
        connect(db, host=host, port=port)

    def _ensure_log(self, wf_id):
        ctxs = Context.objects(id=ObjectId(wf_id))
        flag = any(len(task.msgs) > 0 for ctx in ctxs for task in ctx.tasks)
        self.assertTrue(flag, 'ensure the log method is functional.')

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
        self._ensure_log(ctx.id)

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
        wf = WorkFlow('TestWorkflow')
        ctx = Context.new_context(wf)

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
        wf.set_ctx(ctx)
        return wf, ctx

    @staticmethod
    def from_descriptor():
        wf = WorkFlow('TestWorkflow')

        @wf.task('task start', **{
            'succeed': 'task b',
            'fail': 'task c',
        })
        def start():
            wf.log('I am task start. Go to task b.')
            wf.goto('task b')

        @wf.task('task b')
        def b():
            wf.log('I am b. Go to task end.')
            wf.goto('task end')

        @wf.task('task c')
        def c():
            wf.log('I am c. Go to task end.')
            wf.goto('task end')
        
        @wf.task('task end')
        def end():
            wf.log('This is end task')
            wf.log('show wf topology:' + str(wf))
            wf.end()
        wf.set_ctx(Context.new_context(wf))
        return wf


    @staticmethod
    def from_builder():
        wf = WorkFlow('TestWorkflow')
        def start():
            wf.log('I am task start. Go to task b.')
            wf.goto('task b')

        def b():
            wf.log('I am b. Go to task end.')
            wf.goto('task end')

        def c():
            wf.log('I am c. Go to task end.')
            wf.goto('task end')
        
        def end():
            wf.log('This is end task')
            wf.log('show wf topology:' + str(wf))
            wf.end()

        wf.add_task('task start', start, **{
            'succeed': 'task b',
            'fail': 'task c',
        })
        wf.add_task('task b', b)
        wf.add_task('task c', c)
        wf.add_task('task end', end)
        wf.set_ctx(Context.new_context(wf))
        return wf


if __name__ == '__main__':
    unittest.main()
