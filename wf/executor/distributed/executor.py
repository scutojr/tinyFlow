import logging
from threading import RLock
from traceback import format_exc
from multiprocessing.pool import AsyncResult

from bson.objectid import ObjectId


class Master(object):
    def update_workflow(self, wf_id, state_code):
        pass


class DistributedExecutor(object):

    def __init__(self, size=10):
        super(MultiThreadExecutor, self).__init__()
        self.pool = Pool(size)
        self.LOGGER = logging.getLogger(MultiThreadExecutor.__name__)

        self.workflows = {}
        self.lock = RLock()

    def _run(self, wf):
        try:
            super(MultiThreadExecutor, self)._run(wf)
        finally:
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

    def execute_async(self, workflow):
        """
        :param workflow:
        :return:  (execution id, instance of AsyncResult)
        """
        self._add_workflow(workflow)
        async_result = self.pool.apply_async(self._run, (workflow,))
        async_result.wf_id = workflow.id
        return async_result

