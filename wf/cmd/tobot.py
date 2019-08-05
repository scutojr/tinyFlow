import atexit

from .common import *


def main(argv):
    conf = set_up(argv, 'tobot.log')
    conf.role = 'tobot'

    start_services(conf)
    start_http_server(conf)
    atexit.register(stop_services)

