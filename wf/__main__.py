import platform

from mongoengine import connect

from wf import service_router
from wf.server import HttpServer
from wf.workflow import WorkFlowManager
from wf.execution.executor import WorkflowExecutor
from wf.server.reactor import EventManager


def get_pack_dir_for_test():
    os_type = platform.system()
    if os_type == 'Windows':
        return 'C:\\Users\\90786\\dev\\workflow\\tests\\workflows'
    else:
        return '/tmp/ojr/tests/workflows'


def connect_db():
    db = 'test'
    host, port = 'mongo_test_server', 27017
    connect(db, host=host, port=port)


def config_log():
    pass


def main():
    pack_dir = get_pack_dir_for_test()
    config_log()
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
