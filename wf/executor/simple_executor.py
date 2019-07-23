import logging
from traceback import format_exc

from bson.objectid import ObjectId

from wf.workflow import wf_proxy, Workflow


class SimpleExecutor(object):

    def __init__(self):
        self.LOGGER = logging.getLogger(SimpleExecutor.__name__)

    def _run(self, wf, trigger=None):
        wf_proxy.set_workflow(wf)
        try:
            wf.execute(trigger)
        except:
            wf.log(format_exc())
        wf.save()
        return wf

    def execute(self, workflow):
        """
        :param event:
        :param workflow:
        :return:  (workflow, context)
        """
        return self._run(workflow, trigger)

    @staticmethod
    def get_wf_state(wf_id):
        execution = Workflow.get_execution(wf_id)
        return execution.state_str

    @staticmethod
    def get_execution_history(id=None, name=None, with_log=False, startBefore=None):
        """
        get execution history of the workflow

        :param name: select workflow with this name
        :return: single or iterator of Workflow instance
        """
        if id:
            wf = Workflow.objects(id=id).first()
            return wf
        qry = {}
        if name:
            qry['name'] = name
        if startBefore is not None:
            qry['start'] = {'$lte': startBefore}
        cursor = Workflow.objects(__raw__=qry)

        if not with_log:
            cursor = cursor.exclude('logger')
        return cursor

