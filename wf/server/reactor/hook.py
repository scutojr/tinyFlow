import mongoengine as me
from bson.objectid import ObjectId

from .event import Event


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
