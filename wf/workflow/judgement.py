import mongoengine as me
from wf.utils import now_ms


class Judgement(me.EmbeddedDocument):
    desc = me.StringField()
    options = me.ListField(me.StringField())

    # TODO: this name is not consistent
    decision = me.StringField(default='')
    comment = me.StringField(default='')

    created_time = me.IntField()
    judge_time = me.IntField()

    @staticmethod
    def construct(desc, options):
        return Judgement(desc=desc, options=options, created_time=now_ms())

    def judge(self,  decision, comment=''):
        if decision not in self.options:
            raise Exception('decision from user is not in the list of options')
        self.decision = decision
        self.comment = comment
        self.judge_time = now_ms()
