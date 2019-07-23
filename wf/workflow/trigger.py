import mongoengine as me

from wf.reactor.event import Event
from .judgement import Judgement


class TriggerFrame(me.EmbeddedDocument):
    req = me.DictField()
    event = me.ReferenceField(Event)
    judgement = me.EmbeddedDocumentField(Judgement)


class TriggerChain(me.EmbeddedDocument):
    chain = me.ListField()

    _req = me.DictField()
    _event = me.ReferenceField(Event)
    _judgement = me.EmbeddedDocumentField(Judgement)

    def add_trigger(self, event=None, req=None, judgement=None):
        frame = TriggerFrame(event=event, req=req, judgement=judgement)
        self.chain.append(frame)

        if req:
            self._req.update(req)
        if event:
            self._event = event
        if judgement:
            self._judgement = judgement

    @property
    def request(self):
        return self._req

    @property
    def event(self):
        return self._event

    @property
    def judgement(self):
        return self._judgement
