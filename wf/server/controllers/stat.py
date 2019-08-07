import bson.json_util as json
from bson import ObjectId

from flask import request, Response
from flask.blueprints import Blueprint

from wf.stat import TTR
from wf import service_router
from wf.workflow import Workflow, state_str
from wf.utils import now_ms
from wf.reactor import Event


bp = Blueprint('statistic', __name__)


@bp.route('/stat/ttrs', methods=['GET'])
@bp.route('/stat/ttrs/', methods=['GET'])
def get_mttrs():
    """
    :http params: skip, 0 by default
    :http params: limit, 20 by default
    """
    args = request.args
    skip = int(args.get('skip', 0))
    limit = int(args.get('limit', 20))

    ttrs = TTR.get_in_descending(skip, limit)
    return json.dumps(ttrs.as_pymongo())


@bp.route('/stat/ttrs/<name_entity_tags>', methods=['GET'])
@bp.route('/stat/ttrs/<name_entity_tags>/', methods=['GET'])
def get_ttr_timeline(name_entity_tags):
    args = request.args
    skip = int(args.get('skip', 0))
    limit = int(args.get('limit', 20))

    name, entity, tags = name_entity_tags.split(',', 2)
    ts = {}
    for tag in tags.split(','):
        k, v = tag.split('=', 1)
        ts[k] = v

    id = TTR.compute_id(name, entity, ts)
    ttr = TTR.get_ttr_timeline(id, skip, limit)
    return json.dumps(ttr.to_mongo())

