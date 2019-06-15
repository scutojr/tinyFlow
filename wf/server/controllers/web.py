import bson.json_util as json

from flask import request
from flask.blueprints import Blueprint

from wf.server.reactor.event import Event


bp = Blueprint('workflow', __name__)


# TODO: introduce cache


def get_event_names():
    return json.dumps(Event.get_names())


def get_entities():
    return json.dumps(Event.get_entities())


def get_tags():
    return json.dumps(Event.get_tags())


def get_events():
    args = request.args

    name = args.get('name', None)
    entity = args.get('entity', None)
    tags = json.loads(args.get('tags', '{}'))
    state = args.get('state', None)
    start_before = args.get('startBefore', None)
    start_after = args.get('startAfter', None)

    limit = args.get('limit', 100)

    events = Event.query(
        name=name,
        entity=entity,
        tags=tags,
        state=state,
        start_before=start_before,
        start_after=start_after
    )
    events.limit(limit)
    return json.dumps(events.as_pymongo())
