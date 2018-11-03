from multiprocessing.dummy import Pool


class WorkflowManager(object):
    # 1. get registered workflow information
    # 2. get running state and result of workflow
    pass


class WorkflowExecutor(object):
    def __init__(self, size=10):
        self.pool = Pool(size)

    def _run(self, workflow):
        workflow.execute()

    def execute(self, workflow):
        self.pool.apply(self._run, (workflow,))

    def execute_async(self, workflow):
        async_result = self.pool.apply_async(self._run, (workflow,))
        return async_result