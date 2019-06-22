import os
import logging
from copy import deepcopy
from collections import defaultdict
from imp import find_module, load_module

from .builder import WorkflowBuilder


class WorkflowManager(object):
    def __init__(self, pack_dir):
        self.logger = logging.getLogger(WorkflowBuilder.__name__)
        self.pack_dir = pack_dir
        self._workflows = {}
        self._handlers = defaultdict(list)
        self.load()

    def _get_pack(self):
        packs = os.listdir(self.pack_dir)
        return [pack for pack in packs if pack.endswith('.py')]

    def load(self):
        for pack in self._get_pack():
            if os.path.isfile(os.path.join(self.pack_dir, pack)):
                suffix_index = pack.rfind('.')
                if suffix_index > 0:
                    pack = pack[:suffix_index]
                file, pathname, desc = find_module(pack, [self.pack_dir])
                module = load_module(pack, file, pathname, desc)
                for attr in dir(module):
                    wfb = getattr(module, attr)
                    if isinstance(wfb, WorkflowBuilder):
                        wf = wfb.wf()
                        try:
                            wf.validate()
                        except AssertionError as e:
                            self.logger.exception('failed to validate ' + module.__file__)
                        else:
                            self._workflows[wf.name] = wf
                            for key in wfb.get_subscription_keys():
                                self._handlers[key].append(wf)

    def get_workflows(self):
        return self._workflows.values()

    def get_workflow(self, name):
        wf = self._workflows.get(name, None)
        if wf:
            wf = deepcopy(wf)
        return wf

    def get_wf_from_event(self, event):
        """
        :param event:
        :return: list of matching workflow instance
        """
        key = EventSubcription.key_from_event(event)
        wfs = self._handlers[key]
        return deepcopy(wfs)

    def get_wf_ctx(self, ctx_id):
        ctx = Context.objects(id=ctx_id).first()
        wf = self.get_workflow(ctx.wf)
        return wf, ctx

