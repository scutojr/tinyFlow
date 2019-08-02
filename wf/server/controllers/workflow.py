import bson.json_util as json
from bson import ObjectId

from flask import request, Response
from flask.blueprints import Blueprint

from wf import service_router
from wf.workflow import Workflow, state_str
from wf.utils import now_ms
from wf.reactor import Event


bp = Blueprint('workflow', __name__)
wf_manager = service_router.get_wf_manager()
wf_executor = service_router.get_wf_executor()
reactor = service_router.get_reactor()


@bp.route('/workflows', methods=['GET'])
def list_workflow_info():
    wf_builders = wf_manager.get_wf_builders()
    return json.dumps({
        b.name: b.workflow_info for b in wf_builders
    })


@bp.route('/workflows/<name>', methods=['GET'])
def get_workflow_info(name):
    builder = wf_manager.get_wf_builder(name)
    info = None
    if builder:
        info = builder.workflow_info
    return json.dumps({'workflow': info})


@bp.route('/workflows/<name>/subscriptions', methods=['GET'])
def get_workflow_subscriptions(name):
    builder = wf_manager.get_wf_builder(name)
    if builder:
        subs = builder.subscriptions
        return json.dumps({
            'subscriptions': (sub.to_json() for sub in subs)
        })
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
    is_async = request.args.get('async', False)

    event, req = None, request.args
    if request.method == 'POST':
        event = Event.from_json(request.data)
        event.save()
        async_results = reactor.dispatch_event(event=event, wf_name=wf_name, req=req)
    else:
        async_results = reactor.dispatch_req(wf_name, req, event=event)

    if not is_async:
        for ar in async_results:
            ar.wait()
    return json.dumps([ar.wf_id for ar in async_results])


@bp.route('/executions/<wf_id>/execution', methods=['GET'])
def get_wf_execution(wf_id):
    execution = wf_manager.get_workflow_execution(ObjectId(wf_id))
    return execution.to_mongo()

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

    wfs = (wf_executor
            .get_execution_history(name=name, startBefore=startBefore)
            .limit(limit)
            .order_by('-start')
            .skip(skip)
           )
    def transform(wf):
        s = wf.execution.state
        wf.execution.state = state_str(s)
        return wf.to_mongo()
    return json.dumps(transform(wf) for wf in wfs)


@bp.route('/executions/<id>', methods=['GET'])
def get_execution(id):
    wf = wf_executor.get_execution_history(id=ObjectId(id))
    return json.dumps(wf.to_mongo())


@bp.route('/executions/<id>/workflow', methods=['GET'])
def get_wf_info(id):
    wf_info = wf_manager.get_workflow_info(wf_id=ObjectId(id))
    return json.dumps(wf_info)


@bp.route('/variables/', methods=['GET'])
def get_wf_var():
    """

    :http param wf_id:
    """
    args = request.args
    wf_id = args.get('wf_id', None)
    if wf_id is None:
        return Response(status=400)
    vars = wf_manager.get_variables_from_id(ObjectId(wf_id), filled_value=True)
    return json.dumps(vars)


#@bp.routwf_manager.get_variables(wf.name)e('/userDecisions/<id>', methods=['GET', 'POST'])
#@bp.route('/userDecisions/', methods=['GET', 'POST'], endpoint='user_decision_02')
@bp.route('/userDecisions/<id>', methods=['GET', 'POST'])
@bp.route('/userDecisions/', methods=['GET'])
def user_decision(id=''):
    """
    TODO: the url is wrong for GET request
    POST body:
        {
            'judge': '<>',
            'comment': '<>'
        }
    :param id of the judgementHandler:
    :return:
    """
    if request.method == 'GET':
        if id:
            h = Workflow.get_judgement_handler(ObjectId(id))
            return json.dumps({'judgement': h.as_pymongo()})
        else:
            hs = Workflow.get_judgement_handlers()
            return json.dumps(hs.as_pymongo())
    else:
        body = json.loads(request.data)
        judge, comment = body['judge'], body.get('comment', '')
        handler = Workflow.get_judgement_handler(ObjectId(id))
        judgement = handler.judgement
        judgement.judge(judge, comment)
        results = reactor.dispatch_judgement(handler.wf_id, judgement)

        return json.dumps([r.wf_id for r in results])


@bp.route('/reactor/events', methods=['GET'])
def get_events():
    # introduce cache here?
    pass
