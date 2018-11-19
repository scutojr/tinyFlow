import mongoengine as me

from wf.utils import *
from .user_decision import UserDecision
from wf.server.reactor.event import Event


RUNNING = 0
WAITING = 1
SUCCESSFUL = 2


class Task(me.EmbeddedDocument):
    state = me.IntField(default=RUNNING)
    name = me.StringField()
    msgs = me.ListField()

    event = me.ReferenceField(Event)
    user_decision = me.EmbeddedDocumentField(UserDecision)
    callbacks = me.DictField()

    @staticmethod
    def create(name):
        return Task(name=name)

    def log(self, msg, time_ms=None):
        self.msgs.append((time_ms or now_ms(), msg))

    def create_decision(self, desc, *options, **callbacks):
        self.user_decision = UserDecision(desc=desc, options=options)
        self.callbacks.update(callbacks)

    def make_decision(self, decison, comment):
        """
        :param decison:
        :param comment:
        :return: next task name
        """
        self.user_decision.make_decision(decison, comment)
        try:
            task_name = self.callbacks[decison]
        except:
            task_name = self.callbacks['default']
        return task_name

    def set_callback(self, **callbacks):
        self.callbacks.update(callbacks)
