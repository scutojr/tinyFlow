import json

from flask import request
from flask.blueprints import Blueprint

from wf import service_router
from wf.server.reactor import Event, EventState


bp = Blueprint('workflow', __name__)
wf_manager = service_router.get_wf_manager()
wf_executor = service_router.get_wf_executor()
event_manager = service_router.get_event_manager()

_source = 'http-api'
_event_state = EventState.alls
_wf_actions = {
    'exec'
}


@bp.route('/workflows', methods=['GET'])
def list_workflow():
    workflows = wf_manager.get_workflows()
    return json.dumps({
        wf.name: wf.get_metadata() for wf in workflows
    })


@bp.route('/reactor/workflows/<wf_name>', methods=['POST'])
def run_wf(wf_name):
    """
    TODO: make wf_name meaningful
    :http param async:
    :return:
    """
    ids = []
    async_res = []
    is_async = request.args.get('async', False)
    event = Event.from_json(request.data) # we should get the workflow by the incoming event
    new_wfs = wf_manager.get_wf_from_event(event)
    hooks = event_manager.get_hooks(event)

    for wf in new_wfs:
        ctx_id, async_result = wf_executor.execute_async(wf, event)
        ids.append(str(ctx_id))
        async_res.append(async_result)
    for wf, ctx in hooks:
        _, async_result = wf_executor.execute_async(wf, event, ctx)
        ids.append(str(ctx.id))
        async_res.append(async_result)
    if not is_async:
        for ar in async_res:
            ar.wait()
    return json.dumps(ids)


@bp.route('/workflows/info/<wf_id>', methods=['GET'])
def wf_info(wf_id):
    return wf_executor.get_wf_state(wf_id).to_json()
