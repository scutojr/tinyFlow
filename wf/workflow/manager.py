import os
from os.path import sep, isdir
from copy import deepcopy
from collections import defaultdict

from bson.objectid import ObjectId

from .pack import Pack
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
    def __init__(self, packs_dir):
        self.packs_dir = packs_dir
        self.packs = {}
        self._handlers = defaultdict(set)

        self._load_pack()

    def _load_pack(self):
        default_run_dir = '/var/run'
        packs = os.listdir(self.packs_dir)
        for name in packs:
            src_dir = self.packs_dir + sep + name
            if not isdir(src_dir):
                continue
            pack = Pack(name, src_dir, default_run_dir, self)
            pack.load()
            self.packs[name] = pack

    @property
    def handlers(self):
        return self._handlers

    def get_workflows(self):
        for pack in self.packs.itervalues():
            for wf in pack.get_wf():
                # TODO: add a test to ensure it must be deep copied
                yield deepcopy(wf)

    def get_wf_from_ctx(self, ctx):
        return self.get_workflow(ctx.pack, ctx.wf, ctx.version)

    def get_workflow(self, pack, name, version=None):
        # TODO: change globally
        wf = self.packs[pack].get_wf(name, version)
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

    def register_workflow(self, event_subscription, workflow):
        key = event_subscription.to_key()
        self._handlers[key].add(workflow)

    def unregister_workflow(self, workflow):
        for wfs in self._handlers.values():
            wfs.remove(workflow)

    def get_wf_ctx(self, ctx_id):
        if isinstance(ctx_id, str):
            ctx_id = ObjectId(ctx_id)
        ctx = Context.objects(id=ctx_id).first()
        wf = self.get_workflow(ctx.pack, ctx.wf, ctx.version)
        wf.set_ctx(ctx)
        return wf, ctx
