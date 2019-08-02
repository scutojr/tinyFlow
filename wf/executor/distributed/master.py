from threading import Condition, Lock
from multiprocessing import TimeoutError
from multiprocessing.pool import AsyncResult

from bson import json_util
from wf.utils import now_ms

from ..simple_executor import SimpleExecutor
from wf.server.async.arpc import route
from wf.workflow.execution import (
    STATE_SCHEDULING,
    STATE_RUNNING
)


_cache = {}


class WfResult(AsyncResult):
    def __init__(self, wf_id, on_success=None):
        super(WfResult, self).__init__(_cache, on_success)
        self.wf_id = wf_id


class WfInfo(object):
    def __init__(self, wf_id, state, hostname, pid):
        self.wf_id = wf_id
        self.state = state
        self.hostname = hostname
        self.pid = pid


class RunnerManager(object):
    class Runner(object):
        def __init__(self, hostname):
            self.hostname = hostname
            self.last = now_ms()

    def __init__(self):
        self.runners = {}

    def update_runner(self, hostname, **kwarg):
        runner = self.runners.get(hostname, None)
        if not runner:
            runner = self.Runner(hostname)
            self.runners[hostname] = runner
        for k, v in kwarg.iteritems():
            setattr(runner, k, v)
        runner.last = now_ms()


class MasterExecutor(SimpleExecutor):
    def __init__(self, runner_api, conf):
        super(MasterExecutor, self).__init__()

        self.runner_mgr = RunnerManager()
        self.runner_api = runner_api
        self._results = {}
        self._workflows = {}
        self._non_end_states = (STATE_SCHEDULING, STATE_RUNNING)

    def execute(self, workflow, timeout=None):
        result = self.execute_async(workflow)
        return result.get(timeout)

    def execute_async(self, workflow):
        workflow.save()
        wf_id = workflow.id
        self.runner_api.execute(wf_id)
        result = WfResult(wf_id)
        self._results[wf_id] = result
        return result

    @route()
    def update_workflow(self, wf_id, state, hostname, pid):
        from wf.workflow.execution import state_str

        if wf_id not in self._workflows:
            wf_info = WfInfo(wf_id, state, hostname, pid)
            self._workflows[wf_id] = wf_info
        else:
            wf_info = self._workflows[wf_id]
            wf_info.state = state
            wf_info.hostname = hostname
            wf_info.pid = pid

            if state not in self._non_end_states:
                result = self._results[wf_id]
                # TODO: AsyncResult should return a Workflow instance
                result._set(wf_id, (True, wf_id))

    @route()
    def heartbeat(self, hostname, pid):
        self.runner_mgr.update_runner(hostname, pid=pid)

