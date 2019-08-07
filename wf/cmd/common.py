import sys
import logging
import os
import os.path as op
from optparse import OptionParser

from mongoengine import connect

from wf.stat import StatDriver
from wf import config
from wf import service_router
from wf.server import HttpServer
from wf.workflow import WorkflowManager
from wf.executor import MultiThreadExecutor
from wf.config import (
    PropertyManager,
    DB_HOST,
    DB_PORT,
    DB_NAME,
    LOG_DIR,
    EXECUTOR_MODE,
    EXECUTOR_MASTER_TOPIC,
    EXECUTOR_RUNNER_TOPIC
)
from wf.reactor import Reactor
from wf.mq import EventListener


PACK_DIR = 'pack_dir'
HTTP_PORT = 'http_port'

_is_stopped = False


def parse_opts(args):
    parser = OptionParser()
    parser.add_option('-f', '--file', dest='file',
                      default='',
                      help='configuration file path')
    (options, args) = parser.parse_args(args)
    if options.file == '':
        parser.error('you need to provide a configuration file by -f')
    return options


def _connect_db(conf):
    def ensure_index():
        from wf.reactor.event import Event
        Event.ensure_indexes()
    db, host, port = (
        conf.get(DB_NAME, 'test'),
        conf.get(DB_HOST, 'mongo_test_server'),
        conf.get(DB_PORT, 27017),
    )
    connect(db, host=host, port=port)
    ensure_index()


def _config_log(conf, log_name):
    log_dir = conf.get(LOG_DIR, '/var/log/tobot')
    if not op.exists(log_dir):
        os.mkdir(log_dir)

    log_file, max_byte, backup_count = (
        op.join(log_dir, log_name),
        100 * 1024 * 1024 * 1024,
        10
    )
    log_format = '%(asctime)s - %(process)d - %(levelname)s - %(name)s - %(message)s'
    log_roller = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_byte,
        backupCount=backup_count,
    )
    log_roller.setFormatter(logging.Formatter(log_format))
    root = logging.getLogger()
    root.addHandler(log_roller)
    root.setLevel(logging.INFO)


def set_up(argv, log_name):
    options = parse_opts(argv)
    conf = config.load(options.file)
    _config_log(conf, log_name)
    _connect_db(conf)
    return conf


def _create_and_start_mq_listener(conf, reactor, stat_driver):
    enable = conf.get(config.MQ_EVENT_LISTENER_ENABLE, 'false').lower()
    listener = None
    if enable == 'true':
        topic = conf.get(config.MQ_TOPIC)
        host_and_ports = conf.get(config.MQ_ADDRESS)

        assert topic, 'topic format error: ' + topic
        hap = []
        for hp in host_and_port.split(','):
            hp = hp.strip()
            host, port = hp.split(':')
            hap.append((host, int(port)))
        listener = EventListener(hap, topic)
        listener.start_listening(reactor)
    return listener


def _create_executor(conf):
    # mode in 'local' and 'distributed'
    mode, role = conf.mode, conf.role
    if mode == 'local':
        return MultiThreadExecutor()
    elif mode == 'distributed':
        if role == 'runner':
            return MultiThreadExecutor()
        else:
            from wf.executor.distributed import Runner, MasterExecutor
            from wf.server.async.arpc import AsyncRpcBuilder

            topic_master, queue_runner = get_topic_and_queue(conf)

            builder = AsyncRpcBuilder(conf.get_mq_host_and_ports())

            runner_api = builder.client(queue_runner, Runner)
            runner_api.connect()

            executor = MasterExecutor(runner_api, conf)
            server = builder.server(topic_master, executor)
            server.start()

            return executor
    else:
        raise Exception('unknown executor mode: ' + mode)


def get_topic_and_queue(conf):
    """
    :return: (topic name of the master, queue name of the runner)
    """
    mode = conf.get(EXECUTOR_MODE, 'local').strip()
    assert mode == 'distributed'
    return (
        conf.get(EXECUTOR_MASTER_TOPIC, 'topic_master'),
        conf.get(EXECUTOR_RUNNER_TOPIC, 'topic_runner'),
    )


def start_services(conf):
    pack_dir = config.configuration.get(PACK_DIR)
    mode, role = conf.mode, conf.role

    wf_executor = _create_executor(conf)
    reactor = Reactor(wf_executor)
    wf_manager = WorkflowManager(conf, reactor, wf_executor)
    prop_mgr = PropertyManager()

    if mode == 'local' or role == 'tobot':
        stat_driver = StatDriver()
        stat_driver.start()
        service_router.set_stat_driver(stat_driver)

        listener = _create_and_start_mq_listener(conf, reactor, stat_driver)
        service_router.set_event_listener(listener)

    wf_manager.load_legacy()

    reactor.setDaemon(True)
    reactor.start()

    service_router.set_wf_manager(wf_manager)
    service_router.set_wf_executor(wf_executor)
    service_router.set_reactor(reactor)
    service_router.set_prop_mgr(prop_mgr)


def stop_services():
    global _is_stopped

    if _is_stopped:
        return

    _is_stopped = True
    service_router.get_http_server().stop()
    service_router.get_reactor().stop()

def start_http_server(conf):
    port = conf.get(HTTP_PORT, 54321)
    http_server = HttpServer('workflow', port)
    http_server.start()
    service_router.set_http_server(http_server)

