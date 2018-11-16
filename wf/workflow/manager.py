import os
from copy import deepcopy
from collections import defaultdict
from imp import find_module, load_module

from .builder import WorkFlowBuilder
from .workflow import Context
from wf.server.reactor import EventState


class EventSubcription(object):
    def __init__(self, event_name, event_state):
        if event_state not in EventState.alls:
            raise Exception('value of event state must be one of: ' + ','.join(EventState.alls))
        self.name = event_name
        self.state = event_state

    def to_key(self):
        return self.name, self.state

    @staticmethod
    def key_from_event(event):
        return event.name, event.state


class WorkFlowManager(object):
    def __init__(self, pack_dir):
        self.pack_dir = pack_dir
        self._workflows = {}
        self._handlers = defaultdict(list)

        self._load()

    def _get_pack(self):
        packs = os.listdir(self.pack_dir)
        return [pack for pack in packs if pack.endswith('.py')]

    def _load(self):
        for pack in self._get_pack():
            if os.path.isfile(os.path.join(self.pack_dir, pack)):
                suffix_index = pack.rfind('.')
                if suffix_index > 0:
                    pack = pack[:suffix_index]
                file, pathname, desc = find_module(pack, [self.pack_dir])
                module = load_module(pack, file, pathname, desc)
                for attr in dir(module):
                    wfb = getattr(module, attr)
                    if isinstance(wfb, WorkFlowBuilder):
                        wf = wfb.wf()
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
