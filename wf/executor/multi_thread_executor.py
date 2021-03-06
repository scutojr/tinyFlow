import logging
from threading import local, RLock
from traceback import format_exc
from multiprocessing.dummy import Pool
from multiprocessing.pool import AsyncResult

from bson.objectid import ObjectId

from .state import WfStates

from .simple_executor import SimpleExecutor


class MultiThreadExecutor(SimpleExecutor):

    def __init__(self, size=10):
        super(MultiThreadExecutor, self).__init__()
        self.pool = Pool(size)
        self.LOGGER = logging.getLogger(MultiThreadExecutor.__name__)

        self.workflows = {}
        self.lock = RLock()

    def _run(self, wf, on_finished=None):
        try:
            super(MultiThreadExecutor, self)._run(wf)
            # TODO: if exception, what should we do?
        finally:
            if on_finished:
                on_finished(wf)
            self._remove_workflow(wf)

    def _add_workflow(self, wf):
        with self.lock:
            self.workflows[wf.id] = wf

    def _remove_workflow(self, wf):
        with self.lock:
            self.workflows.pop(wf.id, None)

    def get_workflow(self, wf_id):
        """
        :return: Workflow instance or None
        """
        return self.workflows.get(wf_id, None)

    def execute_async(self, workflow, on_finished=None):
        """
        :param workflow:
        :return:  (execution id, instance of AsyncResult)
        """
        self._add_workflow(workflow)
        async_result = self.pool.apply_async(self._run, (workflow, on_finished))
        async_result.wf_id = workflow.id
        return async_result

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
