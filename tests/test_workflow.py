import unittest

from workflow.workflow import Workflow, context
from workflow.executor import WorkflowExecutor


class TestWorkFlow(unittest.TestCase):

    def setUp(self):
        pass

    def _create_wf_from_builder(self):
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
            print 'show workflow topology:', str(wf)
            wf.end()

        wf.add_task('task start', start, **{
            'succeed': 'task b',
            'fail': 'task c',
        })
        wf.add_task('task b', b)
        wf.add_task('task c', c)
        wf.add_task('task end', end)
        return wf

    def _create_wf_from_descriptor(self):
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
            print 'show workflow topology:', str(wf)
            wf.end()
        return wf

    def test_wf_builder(self):
        print '===== test wf builder ====='
        wf = self._create_wf_from_builder()
        wf.execute()

    def test_wf_descriptor(self):
        print '===== test wf descriptor ====='
        wf = self._create_wf_from_descriptor()
        wf.execute()

    def test_executor(self):
        print '===== test wf executor ====='
        executor = WorkflowExecutor(20)
        for i in range(2):
            wf = self._create_wf_from_builder()
            executor.execute(wf)


if __name__ == '__main__':
    unittest.main()