import sys
from optparse import OptionParser

from mongoengine import connect

from wf import config
from wf import service_router
from wf.server import HttpServer
from wf.workflow import WorkflowManager
from wf.executor import MultiThreadExecutor
from wf.config import PropertyManager
from wf.reactor import Reactor
from wf.mq import EventListener


PACK_DIR = 'pack_dir'

http_server = None


def parse_opts(args):
    parser = OptionParser()
    parser.add_option('-f', '--file', dest='file',
                      default='',
                      help='configuration file path')
    (options, args) = parser.parse_args(args)
    if options.file == '':
        parser.error('you need to provide a configuration file by -f')
    return options


def _connect_db():
    def ensure_index():
        from wf.reactor.event import Event

        Event.ensure_indexes()
    db = 'test'
    host, port = 'mongo_test_server', 27017
    connect(db, host=host, port=port)
    ensure_index()


def _config_log():
    pass


def set_up(argv, db = True, log = True):
    options = parse_opts(argv)
    conf = config.load(options.file)
    _config_log()
    _connect_db()
    return conf


def _create_and_start_mq_listener(conf, reactor):
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
        listener.start_listening()
    return listener


def start_services(conf):
    pack_dir = config.configuration.get(PACK_DIR)

    wf_executor = MultiThreadExecutor()
    reactor = Reactor(wf_executor)
    wf_manager = WorkflowManager(conf, reactor, wf_executor)
    prop_mgr = PropertyManager()
    listener = _create_and_start_mq_listener(conf, reactor)

    wf_manager.load_legacy()

    service_router.set_wf_manager(wf_manager)
    service_router.set_wf_executor(wf_executor)
    service_router.set_reactor(reactor)
    service_router.set_prop_mgr(prop_mgr)
    service_router.set_event_listener(listener)


def main(argv):
    conf = set_up(argv)
    start_services(conf)

    global http_server
    http_server = HttpServer('workflow', 54321)
    http_server.start()


if __name__ == '__main__':
    main(sys.argv)
