import json

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
    wf = wf_manager.get_workflow(wf_name)
    _, ctx = wf_executor.execute(wf)
    print ctx.msgs
    return ''
