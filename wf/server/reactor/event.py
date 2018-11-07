import mongoengine as me


class Event(me.Document):
    tags = me.DictField()
    name = me.StringField(required=True)
    entity = me.StringField(required=True)

    start = me.IntField(default=0)
    status = me.StringField(default='')
    params = me.DictField()
    message = me.StringField(default='')

    source = me.StringField(default='')

    _meta = [
        'start'
    ]
