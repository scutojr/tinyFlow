import unittest

from wf.executor import SimpleExecutor, MultiThreadExecutor
import tests.utils.db as db


# TODO:
#     1. ensure AsyncResult has wf_id


class TestExecutor(unittest.TestCase):
    def setUp(self):
        db.connect()

    def tearDown(self):
        pass

    def test_get_wf_history(self):
        for executor in [SimpleExecutor(), MultiThreadExecutor()]:
            wfs = executor.get_execution_history()
            self.assertTrue(wfs.count() > 0)


if __name__ == '__main__':
    unittest.main()
