import unittest
from multiprocessing.pool import AsyncResult

from mock import Mock, patch

import wf
from wf.reactor.reactor import Reactor
from wf.reactor.event import Event
from wf.workflow.manager import WorkflowManager
from wf.workflow.builder import WorkflowBuilder

import tests.utils.wf_mgr as util_wf_mgr
import tests.utils.db as db
from tests.utils.config import conf


MAX_VERSION = 5


class TestReactor(unittest.TestCase):
    def setUp(self):
        db.connect()

        max_version = 5
        self.wf_executor = Mock(**{
            'execute_async.return_value': AsyncResult({}, None)
        })
        self.reactor = Reactor(self.wf_executor)
        self.wf_mgr = util_wf_mgr.create_wf_mgr(MAX_VERSION, self.reactor, self.wf_executor)

    def tearDown(self):
        util_wf_mgr.clear_legacy()

    def test_dispatch_req(self):
        wf_builders = self.wf_mgr.get_wf_builders()
        dummy_req = {}
        self.assertTrue(len(wf_builders) > 0)
        for b in wf_builders:
            results = self.reactor.dispatch_req(b.name, dummy_req)
            self.assertTrue(isinstance(results, list))
            self.assertTrue(len(results) > 0)
            for r in results:
                self.assertTrue(isinstance(r, AsyncResult))
                self.assertTrue(self.wf_executor.execute_async.call_count > 0)

    def test_dispatch_event(self):
        wf_builders = self.wf_mgr.get_wf_builders()
        self.assertTrue(len(wf_builders) > 0)
        for builder in wf_builders:
            subs = builder.subscriptions
            self.assertTrue(len(subs) > 0)
            for sub in subs:
                event = Event(name=sub.name, state=sub.state)
                results = self.reactor.dispatch_event(event)
                self.assertTrue(len(results) > 0)
                for r in results:
                    self.assertTrue(isinstance(r, AsyncResult))
                    self.assertTrue(self.wf_executor.execute_async.call_count > 0)
        fake_event = Event(name='not_exist_name', state='unknown')
        results = self.reactor.dispatch_event(fake_event)
        self.assertTrue(len(results) == 0)


if __name__ == '__main__':
    unittest.main()
