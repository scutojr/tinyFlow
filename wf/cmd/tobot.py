from .common import *


def main(argv):
    conf = set_up(argv)
    conf.set_role('tobot')
    mode = conf.get(EXECUTOR_MODE)

    start_services(conf)
    start_http_server(conf)
    atexit.register(stop_services)

