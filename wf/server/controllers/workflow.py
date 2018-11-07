import json

from flask import request
from flask.blueprints import Blueprint

from wf import service_router


bp = Blueprint('workflow', __name__)
wf_manager = service_router.get_wf_manager()
wf_executor = service_router.get_wf_executor()


@bp.route('/workflows', methods=['GET'])
def list_workflow():
    workflows = wf_manager.get_workflows()
    return json.dumps({
        wf.name: wf.get_metadata() for wf in workflows
    })


@bp.route('/workflows/<wf_name>/actions/<action>', methods=['GET'])
def manipulate_wf(wf_name, action):
    """
    :http param async:
    :return:
    """
    is_async = request.args.get('async', False)
    wf = wf_manager.get_workflow(wf_name)
    if is_async:
        ctx_id, async_result = wf_executor.execute_async(wf)
        return str(ctx_id)
    else:
        wf_executor.execute(wf)
        return '' # return failed or successful


@bp.route('/workflows/info/<wf_id>', methods=['GET'])
def wf_info(wf_id):
    return wf_executor.get_wf_state(wf_id).to_json()
