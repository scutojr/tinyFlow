import platform

from wf import service_router
from wf.server import HttpServer
from wf.workflow import WorkflowManager
from wf.executor import WorkflowExecutor


def get_pack_dir_for_test():
    os_type = platform.system()
    if os_type == 'Windows':
        return 'C:\\Users\\90786\\dev\\workflow\\tests\\workflows'
    else:
        return '/tmp/ojr/tests/workflows'


def main():
    pack_dir = get_pack_dir_for_test()
    wf_manager = WorkflowManager(pack_dir)
    wf_executor = WorkflowExecutor()

    service_router.set_wf_manager(wf_manager)
    service_router.set_wf_executor(wf_executor)

    http_server = HttpServer('workflow', 54321)
    http_server.start()


main()
