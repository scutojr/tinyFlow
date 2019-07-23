import logging
from threading import local
from traceback import format_exc
from multiprocessing.dummy import Pool
from multiprocessing.pool import AsyncResult

from bson.objectid import ObjectId

from .state import WfStates, State

from .simple_executor import SimpleExecutor


class MultiThreadExecutor(SimpleExecutor):

    def __init__(self, size=10):
        super(MultiThreadExecutor, self).__init__()
        self.pool = Pool(size)
        self.LOGGER = logging.getLogger(MultiThreadExecutor.__name__)

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

    def execute_async(self, workflow):
        """
        :param workflow:
        :return:  (execution id, instance of AsyncResult)
        """
        async_result = self.pool.apply_async(self._run, (workflow,))
        async_result.wf_id = workflow.id
        return async_result

