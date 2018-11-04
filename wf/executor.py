from threading import local
from multiprocessing.dummy import Pool

from wf.workflow import Context


__all__ = [
    'context',
    'WorkflowExecutor'
]


_ctx = local()


class ContextProxy(object):

    def __getattribute__(self, name):
        ctx = getattr(_ctx, 'context', None)
        if not ctx:
            ctx = Context()
            _ctx.context = ctx
        return getattr(ctx, name)


class WorkflowManager(object):
    # 1. get registered wf information
    # 2. get running state and result of wf
    pass


class WorkflowExecutor(object):
    def __init__(self, size=10):
        self.pool = Pool(size)

    def _run(self, workflow):
        _ctx.context = Context()
        workflow.execute()

    def execute(self, workflow):
        self.pool.apply(self._run, (workflow,))

    def execute_async(self, workflow):
        async_result = self.pool.apply_async(self._run, (workflow,))
        return async_result


context = ContextProxy()