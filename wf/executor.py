from threading import local
from multiprocessing.dummy import Pool

from wf.workflow import Context


__all__ = [
    'context',
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
        """
        :param workflow:
        :return:  (workflow, context)
        """
        _set_cur_ctx(Context())
        _set_cur_wf(workflow)
        workflow.execute()
        return workflow, _ctx.context

    def execute(self, workflow):
        """
        :param workflow:
        :return:  (workflow, context)
        """
        async_result = self.execute_async(workflow)
        return async_result.get()

    def execute_async(self, workflow):
        """
        :param workflow:
        :return:  instance of AsyncResult
        """
        async_result = self.pool.apply_async(self._run, (workflow,))
        return async_result


context = ContextProxy()