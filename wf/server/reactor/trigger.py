import mongoengine as me
from .event import Event


class BasedTrigger(me.EmbeddedDocument):

    params = me.DictField()
    event = me.ReferenceField(Event)
    decision = me.StringField()
    comment = me.StringField()

    meta = {
        'allow_inheritance': True
    }


    def update(self, trigger):
        if trigger.params and self.params:
            self.params.clear()
            self.params.update(trigger.params)
        if trigger.event:
            self.event = event
        if trigger.decision:
            self.decision = trigger.decision
        if trigger.comment:
            self.comment = trigger.comment


class Trigger(BasedTrigger):

    def get_workflow(self, evt_mgr, wf_mgr):
        raise Exception('not implementation')

    @staticmethod
    def build(
        wf_name=None,
        params=None,
        event=None,
        ctx_id=None,
        decision=None,
        comment=''
    ):
        if decision and ctx_id:
            return UserDecisionTrigger(ctx_id, decision, comment)
        else:
            return CompoundTrigger(wf_name, event, params)


class EventTrigger(Trigger):

    def get_workflow(self, evt_mgr, wf_mgr):
        ids, wfs = [], []

        wfs.extend(wf_mgr.get_wf_from_event(self.event))
        wfs.extend(evt_mgr.get_wf_from_event(self.event))

        return wfs


class ParamsTrigger(Trigger):
    def __init__(self, wf_name, params, **kwargs):
        super(ParamsTrigger, self).__init__(params=params, **kwargs)
        self.wf_name = wf_name

    def get_workflow(self, evt_mgr, wf_mgr):
        wf = wf_mgr.get_workflow(self.wf_name)
        # wf.set_request(self.params)
        return [wf]


class CompoundTrigger(Trigger):
    def __init__(self, wf_name=None, event=None, params=None, **kwargs):
        super(CompoundTrigger, self).__init__(event=event, params=params, **kwargs)
        self.et = EventTrigger(event)
        self.wf_name = wf_name
        self.params = params
        self.event = event

    def get_workflow(self, evt_mgr, wf_mgr):
        wfs = self.et.get_workflow(evt_mgr, wf_mgr)
        if self.wf_name:
            wf = wf_mgr.get_workflow(self.wf_name)
            if wf:
                for w in wfs:
                    if w.name == wf.name:
                        break
                else:
                    wfs.append(wf)
        return wfs


class UserDecisionTrigger(Trigger):
    def __init__(self, ctx_id, decision, comment, **kwargs):
        super(UserDecisionTrigger, self).__init__(decision=decision, comment=comment, **kwargs)
        self.ctx_id = ctx_id

    def get_workflow(self, evt_mgr, wf_mgr):
        wf = wf_mgr.get_wf_from_ctx(ctx_id=self.ctx_id)
        wf.make_decision(self.decision, self.comment)
        return [wf]


class TimeoutTrigger(Trigger):
    def get_workflow(self, evt_mgr, wf_mgr):
        pass
