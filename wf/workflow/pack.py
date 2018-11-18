import os
import shutil
from os.path import sep
from hashlib import md5
from threading import RLock
from imp import find_module, load_module

from wf.utils import *
from . import WorkFlowBuilder


class Pack(object):
    # TODO: unify the type of version including self.latest, key of self.wfs
    def __init__(self, name, src_dir, run_dir):
        self.name = name
        self.src_dir = src_dir
        self.run_dir = run_dir + sep + name
        self.latest = 0
        self.wfs = {}

        # initialize to be the value of self.latest
        self.seed_version = 0
        self.lock_seed = RLock()
        self.lock_load_pack = RLock()

        self.recover()

    def recover(self):
        if not os.path.exists(self.run_dir):
            os.mkdir(self.run_dir)

        self.latest = self.latest_version()
        self.seed_version = self.latest

        self._load_class()
        # TODO: check tmp dir on recovery, if tmp dir exist, just remove the respective version dir in case of
        # TODO: version dir of middle state

    def load(self):
        self._load_pack()

    def get_wf(self, wf_name, version=None):
        return self.wfs[(wf_name, version or self.latest)]

    def add_wf(self, wf_name, version, wf):
        self.wfs[(wf_name, int(version))] = wf

    def remove(self, version):
        for wf_name, v in self.wfs.keys():
            if v == version:
                self.wfs.pop((wf_name, v))

    @staticmethod
    def compute_checksum(dest, file_filter=lambda: ''):
        if os.path.isdir(dest):
            files = [dest + sep + file for file in os.listdir(dest)]
            files.sort()
        else:
            if os.path.exists(dest):
                files = [dest]
            else:
                files = []
        files = [file for file in files if file_filter(file)]
        checksum = md5()
        for file in files:
            with open(file) as src:
                for chunk in iter(lambda : src.read(4096), b''):
                    checksum.update(chunk)
        return checksum.hexdigest()

    def latest_version(self):
        versions = [int(v) for v in os.listdir(self.run_dir) if is_int(v)]
        versions.sort()
        return len(versions) > 0 and versions[-1] or 0

    def checksum(self, version):
        return self.compute_checksum(self.run_dir + sep + str(version), self._py_file_filter)

    def get_latest_version_and_checksum(self):
        version  = self.latest_version()
        return version, self.checksum(version)

    def _get_wf_file(self, root):
        packs = os.listdir(root)
        return [pack for pack in packs if pack.endswith('.py')]

    def _py_file_filter(self, file_name):
        return not file_name.endswith('.pyc')

    def _new_version(self):
        with self.lock_seed:
            self.seed_version += 1
            res = self.seed_version
        return res

    def _load_class(self, version=None):
        if version is None:
            versions = [v for v in os.listdir(self.run_dir) if is_int(v)]
        else:
            versions = [version]

        for version in versions:
            module_root = self.run_dir + sep + version
            for py_file_name in self._get_wf_file(module_root):
                index = py_file_name.rfind('.')
                if index >= 0:
                    py_file_name = py_file_name[:index]
                file, pathname, desc = find_module(py_file_name, [module_root])
                module = load_module('.'.join([self.name, version, py_file_name]), file, pathname, desc)
                for attr in dir(module):
                    wfb = getattr(module, attr)
                    if isinstance(wfb, WorkFlowBuilder):
                        wf = wfb.wf()
                        self.add_wf(wf.name, version, wf)

    def _load_pack(self):
        latest_version, latest_checksum = self.get_latest_version_and_checksum()
        new_checksum = self.compute_checksum(self.src_dir, self._py_file_filter)

        try:
            self.lock_load_pack.acquire()
            if latest_checksum != new_checksum:
                new_version = self._new_version()
                tmp_dir = self.run_dir + sep + '.tmp_load_pack'
                new_dir = self.run_dir + sep + str(new_version)
                shutil.copytree(self.src_dir, tmp_dir)
                os.rename(tmp_dir, new_dir)
                self.latest = new_version
            else:
                tmp_dir = self.run_dir + sep + '.tmp_load_pack'
                shutil.copytree(self.src_dir, tmp_dir)
                latest_dir = self.run_dir + sep + str(self.latest)
                shutil.rmtree(latest_dir, ignore_errors=True)
                os.rename(tmp_dir, latest_dir)
            self._load_class(str(self.latest))
        finally:
            self.lock_load_pack.release()
