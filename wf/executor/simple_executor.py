import logging
from traceback import format_exc

from bson.objectid import ObjectId

from .state import WfStates
from ..workflow import Context


class SimpleExecutor(object):

    def __init__(self):
        self.LOGGER = logging.getLogger(SimpleExecutor.__name__)

        from . import set_cur_wf
        self.set_wf = set_cur_wf

    def _run(self, workflow, trigger=None):
        self.set_wf(workflow)
        workflow.set_state(WfStates.running.state)
        workflow.save()
        try:
            workflow.execute(trigger)
        except:
            print format_exc()
            workflow.set_state(WfStates.failed.state)
            workflow.log(format_exc())
        else:
            if workflow.should_wait():
                workflow.set_state(WfStates.waiting.state)
            elif workflow.is_asking():
                workflow.set_state(WfStates.asking.state)
            else:
                workflow.set_state(WfStates.successful.state)
        workflow.save()
        return workflow, workflow.get_ctx()

    def execute(self, workflow, trigger=None):
        """
        :param event:
        :param workflow:
        :return:  (workflow, context)
        """
        return self._run(workflow, trigger)

    @staticmethod
    def get_wf_state(wf_ctx_id):
        ctxs = Context.objects(id=ObjectId(wf_ctx_id))
        return ctxs.first()

    @staticmethod
    def get_execution_history(id=None, name=None, with_log=False, startBefore=None):
        """
        get execution history of the workflow

        :param name: select workflow with this name
        :return: iterator for Context instance
        """
        if id:
            ctx = Context.objects(id=id).first()
            return ctx
        qry = {}
        if name:
            qry['wf'] = name
        if startBefore is not None:
            qry['start'] = {'$lte': startBefore}
        cursor = Context.objects(__raw__=qry)

        if with_log:
            cursor = cursor.exclude('msgs')
        return cursor

