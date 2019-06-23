import bson.json_util as json

from flask import request
from flask.blueprints import Blueprint

from wf import service_router
from wf.workflow import Context
from wf.utils import now_ms
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


@bp.route('/workflows/<name>', methods=['GET'])
def get_workflow(name):
    wf = wf_manager.get_workflow(name)
    if wf:
        wf = wf.get_metadata()
    return json.dumps(wf)


@bp.route('/reactor/workflows/<wf_name>', methods=['GET', 'POST'])
def run_wf(wf_name=''):
    """
    TODO:
        1. make wf_name meaningful
        2. refact it so as to reduce redundant code
        3. how to response gracefully if error/exception occurs
        4. the response should be contained the state of the workflow triggered
    :http param async:
    :return:
    """
    event, extra_params = None, request.args
    is_async = request.args.get('async', False)
    ids, async_res = event_manager.receive_event(event, wf_name, extra_params)
    if not is_async:
        for ar in async_res:
            ar.wait()
    return json.dumps(ids)

bp.add_url_rule(
    '/reactor/workflows/',
    run_wf.__name__ + '_001',
    run_wf, methods=['GET', 'POST']
)


@bp.route('/workflows/execution/<wf_id>', methods=['GET'])
def get_wf_execution_info(wf_id):
    return wf_executor.get_wf_state(wf_id).to_json()


@bp.route('/workflows/execution', methods=['GET'])
def get_executions():
    """
    get list of workflow execution info, log info will not be returned

    :http param name: specify the workflow name
    :http param limit: specify max number of execution info returned
                       on each request
    :http param startBefore: workflows start before this time in ms
    :http param skip: number of element to skip, this is used for pagination
    """
    args = request.args
    name = args.get('name', None)
    limit = int(args.get('limit', 100))
    startBefore = int(args.get('startBefore', now_ms()))
    skip = int(args.get('skip', 0))

    ctxs = (wf_executor
            .get_wf_history(name=name, startBefore=startBefore)
            .limit(limit)
            .exclude('msgs')
            .order_by('-start')
            .skip(skip)
           )
    return json.dumps(ctxs.as_pymongo())


@bp.route('/userDecisions/<ctx_id>', methods=['GET', 'POST'])
def user_decision(ctx_id):
    """
    TODO: the url is wrong for GET request
    http params:
        decision;
        comment
    :param ctx_id:
    :return:
    """
    if request.method == 'GET':
        return Context.get_asking_context().to_json()
    else:
        args = request.args
        context = Context.from_ctx_id(ctx_id)
        decision = args['decision']
        comment = args['comment']

        context.make_decision(decision, comment)

        wf = wf_manager.get_workflow(context.wf)
        wf_executor.execute_async(workflow=wf, ctx=context)

        return str(context.id)


@bp.route('/reactor/events', methods=['GET'])
def get_events():
    # introduce cache here?
    pass
