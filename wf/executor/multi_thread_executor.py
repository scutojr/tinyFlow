import logging
from threading import local
from traceback import format_exc
from multiprocessing.dummy import Pool

from bson.objectid import ObjectId

from .state import WfStates, State
from wf.workflow import Context
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

    def execute(self, workflow, event=None, ctx=None):
        """
        :param event:
        :param workflow:
        :return:  (workflow, context)
        """
        exec_id, async_result = self.execute_async(workflow, event=event, ctx=ctx)
        return async_result.get()

    def execute_async(self, workflow, event=None, ctx=None):
        """
        :param event:
        :param workflow:
        :return:  (execution id, instance of AsyncResult)
        """
        if not ctx:
            ctx = Context.new_context(workflow)
            ctx.source_event = event
        elif not event:
            # append to list of event and provide a method to get the latest event
            pass
        ctx.state = WfStates.scheduling.state
        ctx.save()
        async_result = self.pool.apply_async(self._run, (workflow, ctx))
        return (ctx.id, async_result)

