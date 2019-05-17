import unittest
import os.path as op

import wf.config as config


class TestConfig(unittest.TestCase):
    def setUp(self):
        pass

    def test_built_in_vars(self):
        home_dir = op.abspath(op.join(op.dirname(__name__), '..'))
	self.assertTrue(
	    home_dir == config.HOME,
	    'home dir is wrong, you may change the path of config module'
	)


if __name__ == '__main__':
    unittest.main()
