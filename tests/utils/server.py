import os.path as op
import time
from threading import Thread
from commands import getstatusoutput

import wf.cmd.tobot as tobot


def start_server():
    config_file = op.abspath(
        op.dirname(__file__) + '/../../' + 'config/wf.ini.template'
    )
    args = ['-f', config_file]
    thread = Thread(target=tobot.main, args=(args, ))
    thread.setDaemon(True)
    thread.start()
    time.sleep(1)


def stop_server():
    tobot.stop_services()
