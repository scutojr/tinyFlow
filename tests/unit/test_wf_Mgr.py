import os
import os.path as op
import unittest
import shutil

from mock import Mock, patch

from wf.workflow.manager import (
    WorkflowManager,
    PACK_DIR,
    PACK_LEGACY_DIR
)
from wf.workflow.builder import WorkflowBuilder
from wf.config import Configuration
from wf.reactor import Reactor

from tests.utils.config import conf
import tests.utils.db as db
import tests.utils.wf_mgr as util_wf_mgr


class TestWorkflowManager(unittest.TestCase):
    def setUp(self):
        db.connect()

        self.pack_dir = conf.get(PACK_DIR)
        self.legacy_dir = conf.get(PACK_LEGACY_DIR)

        os.mkdir(self.legacy_dir)

    def tearDown(self):
        util_wf_mgr.clear_legacy()

    def _module_files(self, pack_dir):
        return [f[:-3] for f in os.listdir(self.pack_dir) if f.endswith('.py')]

    def test_load_legacy(self):
        executor = Mock()
        mgr = util_wf_mgr.create_wf_mgr(0, Reactor(executor))
        self.assertTrue(len(mgr.legacy_wf_builders) == 0)
        self.assertTrue(len(mgr.wf_builders) == 0)

        max_version = 5
        util_wf_mgr.prepare_legacy(max_version)
        mgr.load_legacy()
        self.assertTrue(len(mgr.legacy_wf_builders) == 5)
        for version, builders in mgr.legacy_wf_builders.iteritems():
            self.assertTrue(len(builders) > 0)
        files = self._module_files(self.pack_dir)
        self.assertTrue(len(mgr.wf_builders) == len(files))

    def test_load_new(self):
        max_version = 5
        executor = Mock()
        mgr = util_wf_mgr.create_wf_mgr(max_version, Reactor(executor))

        self.assertTrue(mgr.latest_version == max_version)
        mgr.load_new()

        self.assertTrue(mgr.latest_version > max_version)
        self.assertTrue(len(mgr.wf_builders) > 0)
        self.assertTrue(mgr.wf_builders == mgr.legacy_wf_builders[mgr.latest_version])

    def test_get_workflow(self):
        executor = Mock()
        module_files = self._module_files(self.pack_dir)
        mgr = util_wf_mgr.create_wf_mgr(5, Reactor(executor))
        wf_name = module_files[0]

        wf1 = mgr.get_workflow(wf_name, 4)
        wf2 = mgr.get_workflow(wf_name, 3)

        self.assertTrue(wf1 != None)
        self.assertTrue(wf2 != None)
        self.assertTrue(wf1 != wf2)

    def test_register(self):
        pass

if __name__ == '__main__':
    unittest.main()

