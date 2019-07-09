from threading import local


_ctx = local()
_wf = local()


def set_cur_ctx(ctx):
    _ctx.context = ctx


def get_cur_wf():
    return _wf.workflow


def set_cur_wf(wf):
    _wf.workflow = wf


class WorkflowProxy(object):

    def __getattribute__(self, name):
        wf = get_cur_wf()
        return getattr(wf, name)


workflow = WorkflowProxy()


from .state import State, WfStates
from .simple_executor import SimpleExecutor
from .multi_thread_executor import MultiThreadExecutor


__all__ = [
    'SimpleExecutor',
    'MultiThreadExecutor',
    'State',
    'WfStates',
    'wf_proxy',
]
