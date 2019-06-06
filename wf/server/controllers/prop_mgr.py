import logging

import bson.json_util as json
from flask import request
from flask.blueprints import Blueprint

from wf import service_router


FAILED = 'FAILED'
SUCCESSFUL = 'SUCCESSFUL'


bp = Blueprint('prop_mgr', __name__)
logger = logging.getLogger(__name__)
prop_mgr = service_router.get_prop_mgr()


def manage_prop(name=''):
    '''
    POST schema:
        {
            ["name": <name>,]
            ["value": "",]
            ["description": "",]
            ["vtype": ""]
        }
    response schema:
        {
            "status": "failed" | "successful",
            ["response": <dict or str or int>]    # on success
            ["exception": <exception info>]    # on failure
        }
    '''
    namespace = request.args.get('namespace', '')
    method = request.method

    rsp = {}

    try:
        if method == 'GET':
            ans = prop_mgr.get_property(name, namespace)
            if ans:
                if isinstance(ans, list):
                    ans = (p.to_mongo() for p in prop_mgr.get_property(namespace=namespace))
                else:
                    ans = ans.to_mongo()
            else:
                ans = None
            rsp['response'] = ans
        elif method == 'POST':
            body = json.loads(request.data)
            if prop_mgr.get_property(name, namespace) == None:
                body.update(name=name)
                prop_mgr.create_property(namespace=namespace, **body)
            else:
                new_name = body.pop('name', None)
                prop_mgr.update_property(name, new_name=new_name, namespace=namespace, **body)
        elif method == 'DELETE':
            prop_mgr.remove_property(name, namespace)
    except Exception as e:
        logger.exception(e)
        rsp['status'] = FAILED
        rsp['exception'] = str(e)
    else:
        rsp['status'] = SUCCESSFUL
    return json.dumps(rsp)


bp.add_url_rule(
    '/properties/',
    'list_properties',
    manage_prop,
    methods=['GET']
)

bp.add_url_rule(
    '/properties/<name>',
    'get_or_set_property',
    manage_prop,
    methods=['GET', 'POST', 'DELETE']
)
