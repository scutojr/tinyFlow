import bson.json_util as json
from bson import ObjectId

from flask import request, Response
from flask.blueprints import Blueprint

from wf import service_router
from wf.workflow import Context, Scope
from wf.utils import now_ms
from wf.server.reactor import Event, EventState, Trigger


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


@bp.route('/workflows/<name>/subscriptions', methods=['GET'])
def get_workflow_subscriptions(name):
    wf = wf_manager.get_workflow(name)
    if wf:
        subs = wf.get_subscriptions()
        return json.dumps((sub.to_json() for sub in subs))
    else:
        return Response(status=400)


@bp.route('/reactor/workflows/<wf_name>', methods=['GET', 'POST'])
@bp.route('/reactor/workflows/', methods=['GET', 'POST'], endpoint='run_wf_02')
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
    """
    event, extra_params = None, request.args
    if request.method == 'POST':
        event = Event.from_json(request.data)
    is_async = request.args.get('async', False)
    ids, async_res = event_manager.receive_event(event, wf_name, extra_params)
    if not is_async:
        for ar in async_res:
            ar.wait()
    return json.dumps(ids)
    """
    is_async = request.args.get('async', False)

    event, params = None, request.args
    if request.method == 'POST':
        event = Event.from_json(request.data)
        event.save()

    trigger = Trigger.build(wf_name=wf_name, event=event, params=params)
    ids, async_res = event_manager.dispatch(trigger)

    if not is_async:
        for ar in async_res:
            ar.wait()
    return json.dumps(ids)


@bp.route('/workflows/execution/<wf_id>', methods=['GET'])
def get_wf_execution_info(wf_id):
    return wf_executor.get_wf_state(wf_id).to_json()


@bp.route('/executions/', methods=['GET'])
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
            .get_execution_history(name=name, startBefore=startBefore)
            .limit(limit)
            .exclude('msgs')
            .order_by('-start')
            .skip(skip)
           )
    return json.dumps(ctxs.as_pymongo())


@bp.route('/executions/<id>', methods=['GET'])
def get_execution(id):
    ctx = wf_executor.get_execution_history(id=ObjectId(id))
    return json.dumps(ctx.to_mongo())


@bp.route('/executions/<id>/workflow', methods=['GET'])
def get_wf_from_execution(id):
    wf = wf_manager.get_wf_from_ctx(id)
    return json.dumps(wf.get_metadata())


@bp.route('/variables/', methods=['GET'])
def get_wf_var():
    """

    :http param wf_id:
    """
    args = request.args
    wf_id = args.get('wf_id', None)
    if wf_id is None:
        return Response(status=400)
    wf = wf_manager.get_wf_from_ctx(wf_id)
    vars = wf_manager.get_variables(wf.name)
    rsp = []
    for var in vars:
        serialize = var.to_json()
        serialize['value'] = var.get(workflow=wf)
        rsp.append(serialize)
    return json.dumps(rsp)


@bp.route('/userDecisions/<ctx_id>', methods=['GET', 'POST'])
@bp.route('/userDecisions/', methods=['GET', 'POST'], endpoint='user_decision_02')
def user_decision(ctx_id=None):
    """
    TODO: the url is wrong for GET request
    http params:
        decision;
        comment
    :param ctx_id:
    :return:
    """
    if request.method == 'GET':
        ctxs = Context.get_asking_context().fields(id=1, user_decision=1)
        return json.dumps(ctxs.as_pymongo())
    else:
        body = json.loads(request.data)
        try:
            decision = body['decision']
            comment = body.get('comment', '')
        except KeyError:
            raise Exception(
                'body must be a json like this: {"decision": "yy", "comment": "yy"}'
            )

        '''
        wf = wf_manager.get_wf_from_ctx(ctx_id=ctx_id)
        wf.make_decision(decision, comment)

        wf_executor.execute_async(workflow=wf)

        return str(wf.get_ctx().id)
        '''
        trigger = Trigger.build(ctx_id=ctx_id, decision=decision, comment=comment)
        ids, async_res = event_manager.dispatch(trigger)

        return json.dumps(ids)

@bp.route('/reactor/events', methods=['GET'])
def get_events():
    # introduce cache here?
    pass
