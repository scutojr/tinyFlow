import sys
from optparse import OptionParser

from mongoengine import connect

from wf import config
from wf import service_router
from wf.server import HttpServer
from wf.workflow import WorkflowManager
from wf.executor import WorkflowExecutor
from wf.config import PropertyManager
from wf.server.reactor import EventManager
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
    db = 'test'
    host, port = 'mongo_test_server', 27017
    connect(db, host=host, port=port)


def _config_log():
    pass


def set_up(argv, db = True, log = True):
    options = parse_opts(argv)
    conf = config.load(options.file)
    _config_log()
    _connect_db()
    return conf


def _create_and_start_mq_listener():
    enable = conf.get(config.MQ_EVENT_LISTENER_ENABLE, 'false').lower()
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
        service_router.set_event_listener(listener)
        listener.start_listening()


def start_services(conf):
    pack_dir = config.configuration.get(PACK_DIR)

    wf_manager = WorkflowManager(pack_dir)
    wf_executor = WorkflowExecutor()
    event_manager = EventManager(wf_manager)
    prop_mgr = PropertyManager()

    _create_and_start_mq_listener()

    service_router.set_wf_manager(wf_manager)
    service_router.set_wf_executor(wf_executor)
    service_router.set_event_manager(event_manager)
    service_router.set_prop_mgr(prop_mgr)


def main(argv):
    conf = set_up(argv)
    start_services(conf)

    global http_server
    http_server = HttpServer('workflow', 54321)
    http_server.start()


if __name__ == '__main__':
    main(sys.argv)
