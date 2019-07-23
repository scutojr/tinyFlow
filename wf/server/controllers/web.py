import bson.json_util as json

from flask import request
from flask.blueprints import Blueprint

from wf.reactor.event import Event
from wf.utils import CacheRef, now_ms
from wf.workflow import Workflow


TIMEOUT = 30 * 60 * 1000

bp = Blueprint('web', __name__)

cache_names = CacheRef(TIMEOUT)
cache_entities = CacheRef(TIMEOUT)
cache_tags = CacheRef(24 * 3600 * 1000)


@bp.route('/web/events/names', methods=['GET'])
def get_event_names():
    names = cache_names.set_if_expired_and_get(Event.get_names)
    return json.dumps(names)


@bp.route('/web/events/entities', methods=['GET'])
def get_entities():
    entities = cache_entities.set_if_expired_and_get(Event.get_entities)
    return json.dumps(entities)


@bp.route('/web/events/tags', methods=['GET'])
def get_tags():
    tags = cache_tags.set_if_expired_and_get(Event.get_tags)
    return json.dumps(tags)


@bp.route('/web/events', methods=['GET'])
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
        start_before=start_before and int(start_before),
        start_after=start_after and int(start_after)
    )
    events = events.limit(limit).order_by('-start')
    return json.dumps(events.as_pymongo())


@bp.route('/web/workflows/<wf_id>/log', methods=['GET'])
def get_lot(wf_id):
    logger = Workflow.get_logger(ObjectId(wf_id))
    return json.dumps({
        'logger': logger and logger.as_pymongo()
    })
