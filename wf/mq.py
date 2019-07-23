import sys
import time
import json
import logging
from threading import Thread

from stomp import ConnectionListener, Connection
from stomp.exception import ConnectFailedException

from wf.reactor import Event


__all__ = [
    'EventListener'
]


class EventListener(ConnectionListener):

    def __init__(self, host_and_ports, topic, username=None, password=None):
        self.topic = topic
        self.host_and_ports = host_and_ports
        self.username = username
        self.password = password
        self.should_reconnect = True
        self.conn = Connection(host_and_ports)
        self.conn.set_listener('', self)
        self.logger = logging.getLogger(EventListener.__name__)
        self.subscription_id = 94

    def _connect_and_subscribe(self, ack='auto'):
        conn = self.conn
        try:
            self.logger.info('tring to connect AMQ: ' + str(self.host_and_ports))
            conn.connect(self.username, self.password, wait=True)
            conn.subscribe(destination=self.topic, id=self.subscription_id, ack=ack)
        except ConnectFailedException as e:
            self.logger.exception(
                'failed to connect AMQ: ' + str(self.host_and_ports)
            )

    def _disconnect(self):
        self.conn.disconnect()

    def start_listening(self, reactor, ack='auto'):
        """
        :param ack: either auto, client or client-individual
        """
        self.should_reconnect = True
        self.reactor = reactor
        self._connect_and_subscribe(ack)

    def stop_listening(self):
        self.should_reconnect = False
        self._disconnect()

    def on_connecting(self, host_and_port):
        pass

    def on_disconnected(self):
        # TODO: if exception occurs here, will the listener exit?
        self.logger.warn(
            'connection to amq %s is closed unexpectedly' % str(self.host_and_ports)
        )
        while self.should_reconnect:
            try:
                self._connect_and_subscribe()
            except ConnectFailedException as e:
                self.logger.exception(
                    'failed to reconnect to amq: ' + str(self.host_and_ports)
                )
                time.sleep(5)
            else:
                break

    def on_message(self, headers, message):
        # TODO: should we validate the message format and field type here?
        try:
            event = Event.from_json(message)
            self.reactor.dispatch_event(event)
        except:
            self.logger.exception('failed to process message: ' + message)
        else:
            msg_id = headers['message-id']
            self.conn.ack(msg_id, self.subscription_id)

    def on_ggGerror(self, headers, message):
        print('received an error "%s"' % message)


if __name__ == '__main__':
    main()
