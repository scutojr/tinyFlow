import os
import logging
from collections import defaultdict
from imp import find_module, load_module

from .builder import WorkflowBuilder
from .workflow import EventSubcription
from .context import Context
from .variable import Variable


class WorkflowManager(object):
    def __init__(self, pack_dir):
        self.logger = logging.getLogger(WorkflowBuilder.__name__)
        self.pack_dir = pack_dir
        self._workflows = {}
        self._handlers = defaultdict(list)
        self._vars = defaultdict(list)
        self._subs = defaultdict(list)

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
                wf, vars = None, []
                for attr in dir(module):
                    attr = getattr(module, attr)
                    if isinstance(attr, Variable):
                        vars.append(attr)
                    elif isinstance(attr, WorkflowBuilder):
                        wf = attr.build()
                        try:
                            wf.validate()
                        except AssertionError as e:
                            self.logger.exception('failed to validate ' + module.__file__)
                        else:
                            self._workflows[wf.name] = wf
                            for sub in attr.get_subscriptions():
                                self._register(sub, wf)
                                self._add_sub(attr.name, sub)
                else:
                    if wf is not None:
                        for var in vars:
                            self._add_var(attr.name, var)

    def get_workflows(self):
        wfs = self._workflows.values()
        return [wf.instance() for wf in wfs]

    def get_workflow(self, name, ctx_id=None):
        wf = self._workflows.get(name, None)
        if wf:
            wf = wf.instance(ctx_id=ctx_id)
        return wf

    def get_wf_from_ctx(self, ctx_id):
        ctx, wf = Context.objects(id=ctx_id).first(), None
        if ctx:
            wf = self._workflows.get(ctx.wf, None)
            if wf:
                wf = wf.instance(ctx=ctx)
        return wf

    def get_wf_from_event(self, event):
        """
        :param event:
        :return: list of matching workflow instance
        """
        if event is None:
            return []
        key = EventSubcription.key_from_event(event)
        wfs = self._handlers[key]
        return [wf.instance() for wf in wfs]

    def _register(self, sub, wf):
        self._handlers[sub.to_key()].append(wf)

    def _add_var(self, wf_name, var):
        self._vars[wf_name].append(var)

    def _add_sub(self, wf_name, sub):
        self._subs[wf_name].append(sub)

    def get_variables(self, wf_name):
        return self._vars[wf_name]

    def get_subscriptions(self, wf_name):
        return self._sub[wf_name]

