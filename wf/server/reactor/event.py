from time import time
from bson.objectid import ObjectId
import mongoengine as me


def now_ms():
    return int(time() * 1000)


class EventState(object):
    INFO = 'info'
    WARN = 'warning'
    CRITICAL = 'critical'

    alls = (INFO, WARN, CRITICAL)


class Event(me.Document):
    name = me.StringField(required=True)
    entity = me.StringField(required=True)
    tags = me.DictField()

    start = me.IntField(default=0)
    state = me.StringField(default=EventState.INFO)
    params = me.DictField()
    message = me.StringField(default='')

    source = me.StringField(default='')

    meta = {
        'allow_inheritance': True
    }


class EventWithHook(Event):
    ctx_id = me.ObjectIdField()
    deadline = me.IntField()
    is_processed = me.BooleanField(default=False)

    @staticmethod
    def from_event(event, to_state, ctx_id=None, deadline_ms=None):
        """
        TODO: copy from event, not just reference
        create an EventWithHook instance from an event
        :param event:
        :return:
        """
        ewh = EventWithHook()

        ewh.ctx_id = ObjectId(ctx_id)
        ewh.deadline = deadline_ms

        ewh.name = event.name
        ewh.entity = event.entity
        ewh.tags = event.tags
        ewh.start = event.start
        ewh.state = to_state
        ewh.params = event.params
        ewh.message = event.message
        ewh.source = event.source

        return ewh
