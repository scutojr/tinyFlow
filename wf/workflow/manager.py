import os
import os.path as op
import shutil
import logging
from threading import RLock
from collections import defaultdict
from imp import find_module, load_module

from bson import ObjectId

from .variable import Variable
from .builder import WorkflowBuilder
from .workflow import Workflow, Dispatcher
from .subscription import Subscription


PACK_DIR = 'pack_dir'
PACK_LEGACY_DIR = 'pack_legacy_dir'


class WorkflowManager(object):
    def __init__(self, config, reactor, wf_executor):
        self.logger = logging.getLogger(WorkflowBuilder.__name__)

        self.pack_dir = config.get(PACK_DIR, '/etc/tobot/')
        self.legacy_dir = config.get(PACK_LEGACY_DIR, '/var/run/tobot/')

        self._legacy_wf_builders = defaultdict(dict)
        self._wf_builders = {}

        self.latest_version = 0
        self.reactor = reactor
        self.wf_executor = wf_executor
        self.lock = RLock()

        self._register_wf_async_handler()

    def _register_wf_async_handler(self):
        """
        dispatcher and handler is quit confused for green hands. Actually,
        dispatcher can be handler for a group of subject/topic/event
        """
        dispatcher = Dispatcher(self, self.wf_executor)
        self.reactor.register_dispatcher_for_async_wf(dispatcher)

    @property
    def wf_builders(self):
        """
        used for test purpose
        """
        return self._wf_builders

    @property
    def legacy_wf_builders(self):
        """
        used for test purpose
        """
        return self._legacy_wf_builders

    def _scan_legacy(self):
        files = os.listdir(self.legacy_dir)
        packs = []
        for f in files:
            version = self._get_version(f)
            path = op.join(self.legacy_dir, f)
            if op.isdir(path) and version:
                packs.append((path, version))
                self.latest_version = max(self.latest_version, version)
        return packs

    def _get_version(self, pack_name):
        try:
            version = int(pack_name)
        except ValueError:
            return None
        else:
            return version

    def reload(self):
        pass

    def _register(self, builders):
        self._wf_builders = builders
        for b in builders.values():
            self.reactor.attach_workflow(b)

    def _unregister(self, builders):
        for b in builders:
            self.reactor.detach_workflow(b)

    def _get_wf_modules(self, path, version):
        modules = []
        files = os.listdir(path)

        for f in files:
            if op.isfile(op.join(path, f)) and f.endswith('.py'):
                suffix_index = f.rfind('.')
                if suffix_index > 0:
                    f = f[:suffix_index]
                file, pathname, desc = find_module(f, [path])
                mod = load_module(f + ':' + str(version), file, pathname, desc)
                modules.append(mod)
        return modules

    def _load_pack(self, pack_dir, version):
        builders = {}
        for module in self._get_wf_modules(pack_dir, version):
            builder, vars = None, []
            for attr in dir(module):
                attr = getattr(module, attr)
                if isinstance(attr, Variable):
                    vars.append(attr)
                elif isinstance(attr, WorkflowBuilder):
                    builder = attr
                    try:
                        builder.setup(version, self.reactor)
                        builder.validate()
                    except AssertionError as e:
                        self.logger.exception('failed to validate ' + module.__file__)
            else:
                if builder is not None:
                    for var in vars:
                        builder.add_variable(var)
                    builders[builder.name] = builder
        self._legacy_wf_builders[version] = builders
        return builders

    def load_legacy(self):
        packs = self._scan_legacy()

        for pack, version in packs:
            builders = self._load_pack(pack, version)
            if version >= self.latest_version:
                self._register(builders)


    def load_new(self):
        # TODO: before successfully loading, you need to unregister the latest wf from
        #       reactor
        self.lock.acquire()

        try:
            new_version = self.latest_version + 1
            new_pack_dir = op.join(self.legacy_dir, str(new_version))

            shutil.copytree(self.pack_dir, new_pack_dir)
            builders = self._load_pack(new_pack_dir, new_version)
            self.latest_version = new_version

            self._unregister(self._wf_builders.itervalues())
            self._register(builders)
        finally:
            self.lock.release()

    def clear_legacy(self):
        pass

    def get_wf_builders(self):
        """
        :return: list of WorkflowBuilder
        """
        return self._wf_builders.values()

    def get_wf_builder(self, name, version=None):
        if version:
            return self._legacy_wf_builders[version][name]
        else:
            return self._wf_builders[name]

    def get_wf_builder_from_id(self, wf_id):
        wf = Workflow.objects(id=wf_id).only('name', 'version').first()
        return self.get_wf_builder(name=wf.name, version=wf.version)

    def get_workflow(self, name=None, version=None, wf_id=None, fields=()):
        wf = None
        if wf_id:
            cursor = Workflow.objects(id=wf_id)
            if fields:
                wf = cursor.only(*fields).first()
            else:
                wf = cursor.first()
            if wf is None:
                raise Exception('wf with id %s is not found' % (wf_id))
            name, version = wf.name, wf.version

        try:
            builder = self._legacy_wf_builders[version or self.latest_version][name]
        except KeyError:
            raise Exception('no workflow is found for %s-%s' % (name, version))
        return builder.build(wf)

    def get_workflow_info(self, name=None, wf_id=None):
        if wf_id:
            wf_builder = self.get_wf_builder_from_id(wf_id)
        else:
            wf_builder = self.get_wf_builder(name=name)
        return wf_builder.workflow_info()

    def get_variables(self, wf_name):
        pass

    def get_variables_from_wf(self, wf_id, filled_value=False):
        wf= self.get_workflow(wf_id=wf_id, fields=['name', 'version', 'execution'])
        builder = self.get_wf_builder(wf.name, wf.version)

        if filled_value:
            res = []
            for var in builder.variables:
                seri = var.to_json()
                seri['value'] = var.get(workflow=wf)
                res.append(seri)
            return res
        else:
            return [v.to_json for v in builder.variables]

    """
    def get_workflows(self):
        wfs = self._workflows.values()
        return [wf.instance() for wf in wfs]

    def get_wf_from_event(self, event):
        if event is None:
            return []
        key = EventSubcription.key_from_event(event)
        wfs = self._handlers[key]
        return [wf.instance() for wf in wfs]

    def get_workflow(self, name, ctx_id=None):
        wf = self._workflows.get(name, None)
        if wf:
            wf = wf.instance(ctx_id=ctx_id)
        return wf

    def _register(self, sub, wf):
        self._handlers[sub.to_key()].append(wf)

    def _add_var(self, wf_name, var):
        self._vars[wf_name].append(var)

    def get_variables(self, wf_name):
        return self._vars[wf_name]

    def get_subscriptions(self, wf_name):
        return self._sub[wf_name]
    """

