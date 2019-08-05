import os
import uuid
import socket
import httplib
import logging
from time import sleep
from httplib import HTTPConnection
from threading import Thread, RLock

from bson import ObjectId
from filelock import FileLock

from wf.exception import WorkflowNotFoundError
from wf.config import EXECUTOR_POOL_SIZE, EXECUTOR_MASTER_HOST, EXECUTOR_MASTER_PORT
from wf.executor.multi_thread_executor import MultiThreadExecutor
from wf.workflow import WorkflowManager
import wf.workflow.execution as execution
from wf.server.async.arpc import route


HEARTBEAT_INTERVAL_MS = 'heartbeat_interval_ms'


class Runner(Thread):
    def __init__(self, master, wf_mgr, executor, conf):
        super(Runner, self).__init__()

        self.logger = logging.getLogger(self.__class__.__name__)
        self.conf = conf
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
        self._results = {}
        self.flock = FileLock('/tmp/tobot_runner_for_legacy_dir.lock')

    def _on_wf_finished(self, wf):
        self._results.pop(wf.id, None)
        self.workflows.pop(wf.id, None)
        self.master.report_workflow(
            wf.id,
            wf.execution.state,
            self.hostname,
            self.pid
        )

    def initialize(self):
        self.logger.info('initializing workflow dir')
        host = self.conf.get(EXECUTOR_MASTER_HOST, 'localhost')
        http_port = self.conf.get(EXECUTOR_MASTER_PORT, 54321)
        self.load(host, http_port)

    @route()
    def execute(self, wf_id):
        try:
            wf = self.wf_mgr.get_workflow(wf_id=wf_id)
        except WorkflowNotFoundError as e:
            host, port = self.conf.master_host, self.conf.http_port
            self.load(host, port, wf.version)
            raise e

        if wf is None:
            # TODO: send a message back to master
            raise Exception('workflow is not found in DB: ', wf_id)

        self._results[wf.id] = self.executor.execute_async(wf, self._on_wf_finished)
        self.workflows[wf.id] = wf
        # TODO: is this the correct state to report?
        self.master.report_workflow(
            wf.id,
            execution.STATE_RUNNING,
            self.hostname,
            self.pid
        )

    @route()
    def load(self, master_host, http_port, version=None):
        """
        this methodis process-safe
        """
        if version and version <= self.wf_mgr.latest_version:
            return
        version = '' if version is None else version
        with self.flock:
            dir = self.wf_mgr.get_legacy_dir(self.conf, version)
            if not os.path.exists(dir):
                self.logger.info('workflow dir: %s does not exist, get it from master by http' % dir)
                conn = HTTPConnection(master_host, http_port)
                conn.request('GET', '/tobot/admin/wf_mgr/legacy/' + version)
                rsp = conn.getresponse()
                # TODO: abnormal case: 400, 500

                size = 32 * 1024 * 1024
                tmp_file = '/tmp/' + str(uuid.uuid4())
                with open(tmp_file, 'wb') as sink:
                    part = rsp.read(size)
                    while part != '':
                        sink.write(part)
                        part = rsp.read(size)

                with open(tmp_file, 'rb') as src:
                    self.wf_mgr.decompress_legacy_dir(src)
                conn.close()
        if version:
            self.wf_mgr.load_new(version)
        else:
            self.wf_mgr.load_legacy()

    def get_workflow(self, wf_id):
        return self.workflows.get(ObjectId(wf_id), None)

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

