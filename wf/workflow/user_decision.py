import mongoengine as me

from wf.utils import *


class UserDecision(me.EmbeddedDocument):
    desc = me.StringField()
    options = me.ListField(me.StringField())
    decision = me.StringField()
    comment = me.StringField()

    created_time = me.IntField()
    decided_time = me.IntField()

    def __init__(self, *args, **kwargs):
        super(UserDecision, self).__init__(*args, **kwargs)
        self.created_time = now_ms()

    def add_option(self, *option):
        for op in option:
            self.options[op] = ''

    def make_decision(self,  decision, comment=''):
        if decision not in self.options:
            raise Exception('decision from user is not in the list of options')
        self.decision = decision
        self.comment = comment
        self.decided_time = now_ms()
