import logging
from traceback import format_exc

from bson.objectid import ObjectId

from .state import WfStates
from wf.workflow import Context


class SimpleExecutor(object):

    def __init__(self):
        self.LOGGER = logging.getLogger(SimpleExecutor.__name__)

        from . import set_cur_ctx, set_cur_wf
        self.set_ctx = set_cur_ctx
        self.set_wf = set_cur_wf

    def _run(self, workflow, ctx):
        self.set_ctx(ctx)
        self.set_wf(workflow)
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
        return workflow, ctx

    def execute(self, workflow, event=None, ctx=None):
        """
        :param event:
        :param workflow:
        :return:  (workflow, context)
        """
        if not ctx:
            ctx = Context.new_context(workflow)
            ctx.source_event = event
        return self._run(workflow, ctx)

    @staticmethod
    def get_wf_state(wf_ctx_id):
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

