import time
import unittest

from mock import patch

from wf.server.async.arpc import AsyncRpcBuilder, route

import tests.utils.mq as mq


class MasterApi(object):
    @route('heartbeat')
    def heartbeat(self, hostname, version=0):
        pass

    @route('execute')
    def execute(self, app_id):
        pass


class TestArpc(unittest.TestCase):
    def setUp(self):
        self.topic = 'test_arpc'

    def _setup_server_and_client(self, topic, cls, obj):
        arpc_builder = AsyncRpcBuilder(mq.host_and_ports)

        server = arpc_builder.server(topic, obj)
        client = arpc_builder.client(topic, cls)

        server.start()
        client.connect()
        return (server, client)

    def test_server_and_client(self):
        master_api = MasterApi()
        with patch.object(master_api, 'heartbeat') as heartbeat:
            route('heartbeat')(heartbeat)
            server, client = self._setup_server_and_client(
                self.topic, MasterApi, master_api
            )
            try:
                args = [
                    ['host1'],
                    ['host1', 1],
                    ['host2'],
                    ['host2', 2]
                ]
                for arg in args:
                    client.heartbeat(*arg)
                    time.sleep(0.5)
                    heartbeat.assert_called_with(*arg)
            finally:
                client.disconnect()
                server.stop()


if __name__ == '__main__':
    unittest.main()
