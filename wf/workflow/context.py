import mongoengine as me
from bson.objectid import ObjectId

from wf.utils import now_ms
from wf.server.reactor import Event, UserDecision


class Context(me.Document):
    wf = me.StringField(default='') # TODO: should i rename it to name so as to make naming more convergent
    props = me.DictField()
    msgs = me.ListField()

    source_event = me.ReferenceField(Event)
    exec_history = me.ListField(me.StringField())
    next_task = me.StringField(default='')
    state = me.StringField(default='')

    callbacks = me.ListField()

    user_decision = me.EmbeddedDocumentField(UserDecision)

    def __init__(self, *args, **kwargs):
        super(Context, self).__init__(*args, **kwargs)

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
    def new_context(workflow):
        return Context(wf=workflow.name)

    @staticmethod
    def from_ctx_id(ctx_id):
        return Context.objects(id=ObjectId(ctx_id)).first()

    @staticmethod
    def get_asking_context():
        """
        :return: list of context that is asking user for decision
        """
        return Context.objects(state=WfStates.asking.state)

    @staticmethod
    def get_log(ctx_id):
        ctx = Context.objects(id=ObjectId(ctx_id)).first()
        if ctx == None:
            return ctx
        return ctx.msgs
