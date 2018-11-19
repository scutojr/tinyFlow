import os
import logging
import platform
import os.path as op

from mongoengine import connect

from wf import service_router
from wf.server import HttpServer
from wf.workflow import WorkFlowManager
from wf.execution.executor import WorkflowExecutor
from wf.server.reactor import EventManager


def get_pack_dir_for_test():
    os_type = platform.system()
    if os_type == 'Windows':
        # return 'C:\\Users\\90786\\dev\\workflow\\tests\\workflows'
        return 'C:\\Users\\90786\\dev\\workflow\\tests'
    else:
        return '/tmp/ojr/tests'


def setup_logger(log_file, max_byte, backup_count):
    dirname = op.dirname(log_file)
    if not op.exists(dirname):
        os.mkdir(dirname)
    logging.basicConfig(filename=log_file,
                        level=logging.INFO,
                        format="%(asctime)s - %(process)d - %(levelname)s - %(name)s - %(message)s")
    root_logger = logging.getLogger()
    # Add the log message handler to the logger
    log_roller = logging.handlers.RotatingFileHandler(
                  log_file, maxBytes=max_byte, backupCount=backup_count)
    root_logger.addHandler(log_roller)


def connect_db():
    db = 'test'
    host, port = 'mongo_test_server', 27017
    connect(db, host=host, port=port)


def main():
    app_name = 'workflow'
    log_dir = '/var/log/' + app_name

    setup_logger(log_dir + '/' + 'server.log', 100 * 1024 ** 2, 10)
    pack_dir = get_pack_dir_for_test()
    connect_db()

    wf_manager = WorkFlowManager(pack_dir)
    wf_executor = WorkflowExecutor()
    event_manager = EventManager(wf_manager)

    service_router.set_wf_manager(wf_manager)
    service_router.set_wf_executor(wf_executor)
    service_router.set_event_manager(event_manager)

    http_server = HttpServer('workflow', 54321)
    http_server.start()


main()
