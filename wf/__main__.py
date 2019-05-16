import sys
from optparse import OptionParser

from mongoengine import connect

from wf import config
from wf import service_router
from wf.server import HttpServer
from wf.workflow import WorkflowManager
from wf.executor import WorkflowExecutor
from wf.server.reactor import EventManager


PACK_DIR = 'pack_dir'


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


def set_up(db = True, log = True):
    options = parse_opts(sys.argv)
    config.load(options.file)
    _config_log()
    _connect_db()


def start_services():
    pack_dir = config.configuration.get(PACK_DIR)

    wf_manager = WorkflowManager(pack_dir)
    wf_executor = WorkflowExecutor()
    event_manager = EventManager(wf_manager)

    service_router.set_wf_manager(wf_manager)
    service_router.set_wf_executor(wf_executor)
    service_router.set_event_manager(event_manager)


def main():
    set_up()
    start_services()

    http_server = HttpServer('workflow', 54321)
    http_server.start()


if __name__ == '__main__':
    main()
