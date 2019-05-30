import json

from flask import request
from flask.blueprints import Blueprint

from wf import service_router
from wf.workflow import Context
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
    def get():
        wf = wf_manager.get_workflow(wf_name)
        if not wf:
            raise Exception('no workflow with name "%s" is found.' % wf_name)
        wf.set_request(request.args)
        is_async = request.args.get('async', False)
        ctx_id, async_result = wf_executor.execute_async(wf)
        if not is_async:
            async_result.wait()
        return json.dumps([str(ctx_id)])

    def post():
        ids = []
        async_res = []
        is_async = request.args.get('async', False)
        event = Event.from_json(request.data) # we should get the workflow by the incoming event
        new_wfs = wf_manager.get_wf_from_event(event)
        hooks = event_manager.get_hooks(event)

        if wf_name:
            new_wfs = filter(lambda wf: wf.name == wf_name, new_wfs)
            hooks = filter(lambda hook: hook[0].name == wf_name, hooks)

        for wf in new_wfs:
            wf.set_request(request.args, event)
            ctx_id, async_result = wf_executor.execute_async(wf, event)
            ids.append(str(ctx_id))
            async_res.append(async_result)
        for wf, ctx in hooks:
            wf.set_request(request.args, event)
            _, async_result = wf_executor.execute_async(wf, event, ctx)
            ids.append(str(ctx.id))
            async_res.append(async_result)
        if not is_async:
            for ar in async_res:
                ar.wait()
        return json.dumps(ids)

    if request.method == 'GET':
        return get()
    elif request.method == 'POST':
        return post()

bp.add_url_rule(
    '/reactor/workflows/',
    run_wf.__name__ + '_001',
    run_wf, methods=['GET', 'POST']
)


@bp.route('/workflows/info/<wf_id>', methods=['GET'])
def wf_info(wf_id):
    return wf_executor.get_wf_state(wf_id).to_json()


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
