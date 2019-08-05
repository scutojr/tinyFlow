import socket

from config import *
from wf import service_router as router


def silent(func):
    def internal(*args, **kwarg):
        try:
            return func(*func, **kwarg)
        except:
            pass
    return internal


def get_http_host_and_port(self, port=54321):
    port = self.get(HTTP_PORT, port)
    host = socket.gethostbyname(socket.getfqdn())
    return (host, port)


@silent
def on_load_pack(version):
    mode = configuration.get(EXECUTOR_MODE)
    role = configuration.role
    if mode == 'distributed' and role == 'tobot':
        executor = router.get_wf_executor()
        runner_api = executor.get_runner()
        host, port = configuration.get_http_host_and_port()
        runner_api.load(host, port, version)
