import time
import unittest
from mock import Mock, patch

from stomp import Connection
from stomp.exception import ConnectFailedException

from wf.mq import EventListener


class TestMq(unittest.TestCase):
    def setUp(self):
        self.topic = 'testEventListening'
        self.host_and_ports = [('amq_test_server', 61613)]

        self.listener = EventListener(
            self.host_and_ports, self.topic
        )
        self.listener.start_listening()

        self.sender_client = Connection(self.host_and_ports)
        self.sender_client.start()
        self.sender_client.connect(wait=True)

    def tearDown(self):
        self.sender_client.disconnect()
        self.listener.stop_listening()

    def _send(self, topic, msg):
        self.sender_client.send(body=msg, destination=topic)

    def test_msg_receiving(self):
        listener = self.listener
        with patch.object(listener, 'on_message') as on_message:
            on_message.return_value = None
            self.assertTrue(listener.on_message.call_count == 0)
            self._send(self.topic, 'this is a test msg')
            time.sleep(1)
            self.assertTrue(listener.on_message.call_count == 1)
            self._send(self.topic, 'this is a test msg')
            time.sleep(1)
            self.assertTrue(listener.on_message.call_count == 2)

    def test_reconnect(self):
        # ensure it's connecting to AMQ
        self.test_msg_receiving()
        se =  ConnectFailedException,
        with patch.object(self.listener, '_connect_and_subscribe', side_effect=se) as m:
            self.assertTrue(m.call_count == 0)
            self.listener.conn.disconnect()
            time.sleep(1)
            self.assertTrue(m.call_count == 1)
            time.sleep(6)
            self.assertTrue(m.call_count == 2)
        time.sleep(1)

        # ensure reconnecting is successful
        self.test_msg_receiving()

    def test_qos(self):
        topic = 'topic_for_ack'
        cnt_msg = 5
        listener = EventListener(self.host_and_ports, topic)
        listener.start_listening('client')
        for i in xrange(cnt_msg):
            self._send(topic, 'msg for testing ack')
        listener.stop_listening()

        def se(headers, msg):
            msg_id = headers['message-id']
            listener.conn.ack(msg_id, listener.subscription_id)

        with patch.object(listener, 'on_message', side_effect=se) as m:
            listener.start_listening('client')
            time.sleep(1)
            self.assertTrue(m.call_count == cnt_msg)

        listener.stop_listening()
        time.sleep(1)
        with patch.object(listener, 'on_message', side_effect=se) as m:
            listener.start_listening('client')
            time.sleep(1)
            self.assertTrue(m.call_count == 0)

        listener.stop_listening()


if __name__ == '__main__':
    unittest.main()
