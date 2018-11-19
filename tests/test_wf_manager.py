import unittest
import os.path as op

from wf.workflow.manager import WorkFlowManager


class TestPack(unittest.TestCase):
    def setUp(self):
        self.cwd = op.dirname(op.abspath(__file__))
        self.src_dir = self.cwd

    def test_manager(self):
        manager = WorkFlowManager(self.src_dir)
        self.assertTrue(len(manager.packs) > 0, 'number of pack must be greater than 0')
        self.assertTrue(len(list(manager.get_workflows())) > 0, 'number of workflow must be greater than 0')
        self.assertTrue(len(manager.handlers) > 0, 'number of handlers must be greater than 0')
        for key, value in manager.handlers:
            self.assertTrue(len(value) > 0, 'number of handlers must be greater than 0')


if __name__ == '__main__':
    unittest.main()
