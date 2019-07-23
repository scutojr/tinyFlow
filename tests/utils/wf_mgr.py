import os
import shutil
import commands

from .config import *
from wf.workflow.manager import WorkflowManager


pack_dir = conf.get(PACK_DIR)
legacy_dir = conf.get(PACK_LEGACY_DIR)


def clear_legacy():
    assert legacy_dir.strip() != '/'
    commands.getstatusoutput('rm -rf ' + legacy_dir)


def prepare_legacy(max_version=0):
    if not os.path.exists(legacy_dir):
        os.mkdir(legacy_dir)
    for i in xrange(1, int(max_version) + 1):
        shutil.copytree(pack_dir, op.join(legacy_dir, str(i)))


def create_wf_mgr(max_version=5, reactor=None, wf_executor=None):
    prepare_legacy(max_version)
    mgr = WorkflowManager(conf, reactor, wf_executor)
    mgr.load_legacy()
    return mgr


def module_files():
    return [f[:-3] for f in os.listdir(pack_dir) if f.endswith('.py')]

