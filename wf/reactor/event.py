from time import time
from bson.objectid import ObjectId
import mongoengine as me


def now_ms():
    return int(time() * 1000)


class EventState(object):
    INFO = 'info'
    WARN = 'warning'
    CRITICAL = 'critical'
    UNKNOWN = 'unknown'

    alls = (INFO, WARN, CRITICAL, UNKNOWN)


class EventTimeline(me.Document):
    name = me.StringField(required=True)
    entity = me.StringField(required=True)
    tags = me.DictField()
    state = me.StringField(default=EventState.INFO)

    events = me.ListField()


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
        'allow_inheritance': True,
        'indexes': [
            'start',
        ]
    }

    @staticmethod
    def get_names():
        """
        :return: list of distinct value for event name
        """
        return Event.objects().distinct('name')

    @staticmethod
    def get_entities():
        return Event.objects().distinct('entity')

    @staticmethod
    def get_tags():
        """
        :rtype: set of string like this: k1=v1
        """
        # TODO: optimize this method, it's too time comsuming
        raw_tags = Event.objects().fields(tags=1)
        tags = set()
        for rt in raw_tags:
            for k, v in rt['tags'].iteritems():
                tags.add('%s=%s' % (k, v))
        return tags

    @staticmethod
    def query(
        name=None, entity=None,
        state=None, start_before=None,
        start_after=None, tags={}
    ):
        """
        TODO: validate the type of start_before and start_after at controller
        :return: cursor for event
        """
        qry = {}
        name and qry.setdefault('name', name)
        entity and qry.setdefault('entity', entity)
        state and qry.setdefault('state', state)
        if start_before or start_after:
            qry.setdefault('start', {})
        start_before and qry['start'].setdefault('$lte', start_before)
        start_after and qry['start'].setdefault('$gt', start_after)
        tags and qry.setdefault('tags', tags)

        return Event.objects(__raw__=qry)

    def general_key(self):
        return (self.name, self.state)

    def specific_key(self):
        return (self.name, self.entity, self.state)
