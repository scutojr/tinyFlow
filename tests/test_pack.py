import random
import unittest
import os.path as op

from wf.workflow.pack import *


class TestPack(unittest.TestCase):
    def setUp(self):
        self.cwd = op.dirname(op.abspath(__file__))
        self.name = 'test_pack'
        self.src_dir = self.cwd + op.sep + 'workflows'
        self.run_dir = '/var/run'

    def _test_version_update(self):
        pack = Pack(self.name, self.src_dir, self.run_dir)
        version_old = pack.latest

        with open(self.src_dir + sep + 'test_for_update_checksum', 'aw') as sink:
            sink.write(str(random.randint(1, 1000)))

        try:
            pack.load()
        except:
            self.assertTrue(False, 'failed to load the pack!!!')
        else:
            version_new = pack.latest
            self.assertIsNotNone(pack.get_wf('disk'), 'failed to get the latest workflow from pack')
            self.assertGreater(version_new, version_old, 'version must be updated on dir content change!!!')

    def _test_version_override(self):
        pack = Pack(self.name, self.src_dir, self.run_dir)
        version_old = pack.latest
        try:
            pack.load()
        except:
            self.assertTrue(False, 'failed to load the pack!!!')
        else:
            version_new = pack.latest
            self.assertIsNotNone(pack.get_wf('disk'), 'failed to get the latest workflow from pack')
            self.assertEqual(version_new, version_old, 'version must not be changed if dir content is not changed!!!')

    def test_load_pack(self):
        self._test_version_override()
        self._test_version_update()

    def test_multi_version_wf(self):
        pack = Pack(self.name, self.src_dir, self.run_dir)
        count = 0
        for wf_name, version in pack.wfs.keys():
            if wf_name == 'disk':
                count += 1
        self.assertGreater(count, 1)


if __name__ == '__main__':
    unittest.main()
