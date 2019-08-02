import os
import socket
import httplib
from time import sleep
from threading import Thread, RLock

from bson import ObjectId

from wf.config import EXECUTOR_POOL_SIZE
from wf.executor.multi_thread_executor import MultiThreadExecutor
from wf.workflow import WorkflowManager
import wf.workflow.execution as execution
from wf.server.async.arpc import route


HEARTBEAT_INTERVAL_MS = 'heartbeat_interval_ms'


class Runner(Thread):
    def __init__(self, master, wf_mgr, executor, conf):
        super(Runner, self).__init__()
        self.running = False
        self.interval = conf.get(HEARTBEAT_INTERVAL_MS, 5 * 1000)
        assert self.interval > 500
        self.interval /= 1000.0

        self.pid = os.getpid()
        self.hostname = socket.gethostname()

        self.master = master
        self.wf_mgr = wf_mgr
        self.executor = executor
        self.workflows = {}
        self.lock = RLock()

        self._results = {}

    def _on_wf_finished(self, wf):
        del self._results[wf.id]
        self.master.update_workflow(
            wf.id,
            wf.execution.state,
            self.hostname,
            self.pid
        )

    @route()
    def execute(self, wf_id):
        wf = self.wf_mgr.get_workflow(wf_id=wf_id)
        if wf is None:
            # TODO: send a message back to master
            raise Exception('workflow is not found in DB: ', wf_id)
        self._results[wf.id] = self.executor.execute_async(wf, self._on_wf_finished)
        # TODO: is this the correct state to report?
        self.master.update_workflow(
            wf.id,
            execution.STATE_RUNNING,
            self.hostname,
            self.pid
        )

    def _set_workflow(self, wf):
        with self.lock:
            self.workflows[wf.id] = wf

    def get_workflow(self, wf_id):
        with self.lock:
            return self.workflows.get(ObjectId(wf_id), None)

    def load(self):
        pass

    def loadall(self, master_host, master_port):
        self.wf_mgr = WorkflowManager()
        url = 'http://%s:%s/tobot/admin/wf_mgr/legacy' % (master_host, master_host)

    def _heartbeat(self):
        self.master.heartbeat(self.hostname, self.pid)

    def run(self):
        while self.running:
            self._heartbeat()
            sleep(self.interval)

    def start(self):
        self.running = True
        super(Runner, self).start()

    def stop(self, timeout=None):
        self.running = False
        self.join(timeout)

