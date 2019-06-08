import sys
import time
import logging
from threading import Thread

import stomp


__all__ = [
    'EventListener'
]


class EventListener(stomp.ConnectionListener):

    def __init__(self, host_and_ports, topic, username=None, password=None):
        self.topic = topic
        self.host_and_ports = host_and_ports
        self.username = username
        self.password = password
        self.should_reconnect = True
        self.conn = stomp.Connection()
        self.logger = logging.getLogger(EventListener.__name__)

    def _connect_and_subscribe(self):
        # log here
        conn.set_listener('', self)
        conn.start()
        conn.connect(self.username, self.password, wait=True)
        conn.subscribe(destination=self.topic, id=1, ack='client')

    def _disconnect(self):
        self.conn.disconnect()

    def start_listening(self):
        self.should_reconnect = True
        self._connect_and_subscribe()

    def stop_listening(self):
        self.should_reconnect = False
        self._disconnect()

    def on_connecting(self, host_and_port):
        pass

    def on_disconnected(self):
        # TODO: if exception occurs here, will the listener exit?
        if self.should_reconnect:
            self._connect_and_subscribe()

    def on_message(self, headers, message):
        print('received a message "%s"' % message)

    def on_error(self, headers, message):
        print('received an error "%s"' % message)


def main():
    host_and_ports = [('host', 'port')]
    listener = EventListener(host_and_ports, 'test')


if __name__ == '__main__':
    main()
