import atexit

from .common import *
from wf import service_router as router

from wf.server.async.arpc import AsyncRpcBuilder
from wf.executor.distributed import Runner, MasterExecutor


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
    runner.start()

    server = builder.server(queue_runner, runner)
    server.start()

    return master_api, server, runner


def main(argv):
    conf = set_up(argv)
    conf.set_role('runner')
    start_services(conf)
    master, server, runner = start_runner(conf)

    def hook():
        runner.stop()
        master.disconnect()
        server.stop()
        stop_services()

    atexit.register(hook)

