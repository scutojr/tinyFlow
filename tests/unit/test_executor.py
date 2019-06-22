import unittest

from wf.executor import WorkflowExecutor
import tests.utils.db as db


class TestExecutor(unittest.TestCase):
    def setUp(self):
        db.connect()
        self.executor = WorkflowExecutor()
        # TODO: generate wf execution information here

    def tearDown(self):
        pass

    def test_get_wf_history(self):
        ctxs = self.executor.get_wf_history()
        self.assertTrue(ctxs.count() > 0)


if __name__ == '__main__':
    unittest.main()
