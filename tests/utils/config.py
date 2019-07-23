import os.path as op

from wf.config import Configuration


conf = Configuration()

PACK_DIR = 'pack_dir'
PACK_LEGACY_DIR = 'pack_legacy_dir'


def ini_conf(conf):
    cwd = op.abspath(op.dirname(__file__))

    conf.set(PACK_DIR, op.join(cwd, '../workflows'))
    conf.set(PACK_LEGACY_DIR, '/tmp/test_tobot')


ini_conf(conf)

