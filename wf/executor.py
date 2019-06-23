import logging
from threading import local
from traceback import format_exc
from multiprocessing.dummy import Pool

from bson.objectid import ObjectId

from wf.workflow import Context


__all__ = [
    'context',
    'WfStates',
    'WorkflowExecutor'
]


_ctx = local()
_wf = local()


def _set_cur_ctx(ctx):
    _ctx.context = ctx


def get_cur_wf():
    return _wf.workflow


def _set_cur_wf(wf):
    _wf.workflow = wf


class State(object):
    def __init__(self, state, reason):
        self.state = state
        self.reason = reason


class WfStates(object):
    scheduling = State('scheduling', 'the workflow is in the running queue of executor.')
    running = State('running', 'the workflow is running.')
    interacting = State('interacting', 'the workflow is waiting for user decision.')
    waiting = State('waiting', 'the workflow is waiting for specific event to occur.')
    asking = State('asking', 'the workflow is asking the user for decision.')
    successful = State('successful', 'the workflow is successful with no exception.')
    failed = State('failed', 'the workflow is failed with exception.')
    crashed = State('crashed', 'the workflow is failed because system is crash.')


class ContextProxy(object):

    def __getattribute__(self, name):
        ctx = getattr(_ctx, 'context', None)
        return getattr(ctx, name)


class WorkflowExecutor(object):

    def __init__(self, size=10):
        self.pool = Pool(size)
        self.LOGGER = logging.getLogger(WorkflowExecutor.__name__)

    def _run(self, workflow, ctx):
        _set_cur_ctx(ctx)
        _set_cur_wf(workflow)
        ctx.state = WfStates.running.state
        ctx.save()
        try:
            workflow.set_ctx(ctx)
            workflow.execute()
        except:
            ctx.state = WfStates.failed.state
            ctx.log(format_exc())
        else:
            if workflow.should_wait():
                ctx.state = WfStates.waiting.state
            elif workflow.is_asking():
                ctx.state = WfStates.asking.state
            else:
                ctx.state = WfStates.successful.state
        ctx.save()
        return workflow, _ctx.context

    @staticmethod
    def reset_state_after_crash():
        """
        TODO
        :return:
        """
        normal_states = [WfStates.successful.state, WfStates.failed.state]
        ctxs = Context.objects()
        for ctx in ctxs:
            if ctx.state not in normal_states:
                ctx.state.state = WfStates.crashed.state
                ctx.save()

    def execute(self, workflow, event=None, ctx=None):
        """
        :param event:
        :param workflow:
        :return:  (workflow, context)
        """
        exec_id, async_result = self.execute_async(workflow, event=event, ctx=ctx)
        return async_result.get()

    def execute_async(self, workflow, event=None, ctx=None):
        """
        :param event:
        :param workflow:
        :return:  (execution id, instance of AsyncResult)
        """
        if not ctx:
            ctx = Context.new_context(workflow)
            ctx.source_event = event
        elif not event:
            # append to list of event and provide a method to get the latest event
            pass
        ctx.state = WfStates.scheduling.state
        ctx.save()
        async_result = self.pool.apply_async(self._run, (workflow, ctx))
        return (ctx.id, async_result)

    def get_wf_state(self, wf_ctx_id):
        ctxs = Context.objects(id=ObjectId(wf_ctx_id))
        return ctxs.first()

    @staticmethod
    def get_wf_history(name=None, with_log=False, startBefore=None):
        """
        get execution history of the workflow

        :param name: select workflow with this name
        :return: iterator for Context instance
        """
        qry = {}
        if name:
            qry['wf'] = name
        if startBefore is not None:
            qry['start'] = {'$lte': startBefore}
        cursor = Context.objects(__raw__=qry)

        if with_log:
            cursor = cursor.exclude('msgs')
        return cursor


context = ContextProxy()
