import json

from stomp import *


class Publisher(object):
    def __init__(self, host_and_ports, topic):
        self.conn = Connection(host_and_ports)
        self.topic = topic

    def publish(self, message, routing_key=''):
        msg = {
            'payload': message,
            'routing_key': routing_key
        }
        self.conn.send(self.topic, json.loads(msg))
