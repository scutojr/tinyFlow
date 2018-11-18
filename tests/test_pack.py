import unittest
import traceback
import os.path as op

from wf.workflow.pack import *


class TestPack(unittest.TestCase):
    def setUp(self):
        self.cwd = op.dirname(op.abspath(__file__))
        self.name = 'test_pack'
        self.src_dir = self.cwd + op.sep + 'workflows'
        self.run_dir = '/var/run'

    def test_load_pack(self):
        # TODO: case a) update version, b) override version

        pack = Pack(self.name, self.src_dir, self.run_dir)
        try:
            pack.load()
        except:
            print traceback.format_exc()
            self.assertTrue(False, 'failed to load the pack!!!')
        else:
            # TODO: test the case of pack dir content change
            for key in pack.wfs.keys():
                print key
            self.assertIsNotNone(pack.get_wf('disk'), 'failed to get the latest workflow from pack')

    def test_pack_recovery(self):
        pass

    def test_multi_version_wf(self):
        pass


if __name__ == '__main__':
    unittest.main()
