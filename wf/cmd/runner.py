import os
import time
import atexit
import socket
import shutil
from itertools import count
from httplib import HTTPConnection
from commands import getstatusoutput

from filelock import FileLock, Timeout

from .common import *
import wf.utils as utils
from wf import service_router as router
from wf.workflow import WorkflowManager
from wf.config import EXECUTOR_MASTER_HOST, EXECUTOR_MASTER_PORT
from wf.server.async.arpc import AsyncRpcBuilder
from wf.executor.distributed import Runner, MasterExecutor


def get_log_name():
    counter = count(1)
    while True:
        name = 'runner-%s.log' % counter.next()
        flock = FileLock(os.path.join('/tmp', '.' + name), timeout=1)
        try:
            flock.acquire()
        except Timeout as e:
            continue
        else:
            return flock, name


def _get_log_name():
    path = '/tmp/.runner_suffix'
    flock = FileLock(path + '.lock')
    with flock:
        def cnt_runner():
            rc, msg = getstatusoutput(
                'ps -ef|grep python|grep runner|grep -v grep|wc -l'
            )
            return int(msg.strip())
        if os.path.exists(path):
            try:
                f = open(path, 'r+')
                content = f.read().strip()
                if content == '':
                    ordinal = 1
                else:
                    ordinal = int(content) + 1
                f.seek(0)
                f.write(str(ordinal))
            except ValueError as e:
                raise Exception('unknow value in %s, it should be int.' % path)
            finally:
                f.close()
        else:
            ordinal = 1
            with open(path, 'w+') as f:
                f.write(str(ordinal))
                f.close()

    return 'runner-%s.log' % str(ordinal)


def start_runner(conf):
    builder = AsyncRpcBuilder(conf.get_mq_host_and_ports())

    topic_master, queue_runner = get_topic_and_queue(conf)

    master_api = builder.client(topic_master, MasterExecutor)
    master_api.connect()

    runner = Runner(
        master_api,
        router.get_wf_manager(),
        router.get_wf_executor(),
        conf
    )
    runner.initialize()
    runner.start()

    server = builder.server(queue_runner, runner)
    server.start()

    return master_api, server, runner


def main(argv):
    flock, log_name = get_log_name()
    conf = set_up(argv, log_name)
    conf.role = 'runner'

    start_services(conf)
    master, server, runner = start_runner(conf)

    def hook():
        try:
            runner.stop()
            master.disconnect()
            server.stop()
            stop_services()
        finally:
            flock.release()

    atexit.register(hook)

