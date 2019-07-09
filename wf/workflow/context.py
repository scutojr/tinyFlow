import mongoengine as me
from bson.objectid import ObjectId

from wf.utils import now_ms
from wf.server.reactor import Event, BasedTrigger
from .decision import UserDecision


class Context(me.Document):
    wf = me.StringField(default='')
    props = me.DictField()
    msgs = me.ListField()
    start = me.IntField()

    source_event = me.ReferenceField(Event)
    exec_history = me.ListField(me.StringField())
    next_task = me.StringField(default='')
    state = me.StringField(default='')

    callbacks = me.ListField()

    user_decision = me.EmbeddedDocumentField(UserDecision)

    trigger = me.EmbeddedDocumentField(BasedTrigger)

    meta = {
        'indexes': [
            'start',
        ]
    }

    def get_prop(self, key, default=None):
        return self.props.get(key, default)

    def set_prop(self, key, value):
        self.props[key] = value

    def save(self):
        event = self.source_event
        if event and not event.id:
            event.save()
        super(Context, self).save()

    def log(self, msg, time_ms=None, phase=None):
        self.msgs.append((
            time_ms or now_ms(),
            phase or self.next_task,
            msg
        ))

    def set_callback(self, callback_name, on_timeout):
        self.callbacks.append((callback_name, on_timeout))

    def get_latest_callback(self, timeout=False):
        if timeout:
            return self.callbacks[-1][1]
        else:
            return self.callbacks[-1][0]

    def create_decision(self, desc, *options):
        self.user_decision = UserDecision(desc=desc, options=options)

    def make_decision(self, decison, comment):
        self.user_decision.make_decision(decison, comment)
        self.next_task = self.callbacks[-1][0]

    @staticmethod
    def new_context(workflow, start_ms=None):
        if not start_ms:
            start_ms = now_ms()
        return Context(wf=workflow.name, start=start_ms)

    @staticmethod
    def from_ctx_id(ctx_id):
        return Context.objects(id=ObjectId(ctx_id)).first()

    @staticmethod
    def get_asking_context():
        """
        :return: list of context that is asking user for decision
        """
        from wf.executor import WfStates
        return Context.objects(state=WfStates.asking.state)

    @staticmethod
    def get_log(ctx_id):
        ctx = Context.objects(id=ObjectId(ctx_id)).first()
        if ctx == None:
            return ctx
        return ctx.msgs
