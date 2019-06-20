import json
import time
import unittest

from mock import patch, Mock

from wf.server.reactor.event import Event
from tests.utils import (
    db,
    http,
    server
)


host, port = 'localhost', 54321


class TestWeb(unittest.TestCase):
    def setUp(self):
        server.start_server()

    def tearDown(self):
        try:
            server.stop_server()
            time.sleep(1)
        except:
            pass

    def test_get_event_names(self):
        names = ['n1', 'n2', 'n3']
        with patch.object(
            Event, 'get_names',
            **{'return_value': names}
        ) as m:
            endpoint = '/tobot/web/events/names'
            self.assertTrue(m.call_count == 0)
            for i in xrange(10):
                status, msg, rsp = http.get(host, port, endpoint)
                self.assertTrue(m.call_count == 1)
                self.assertTrue(status == 200)
                self.assertTrue(json.loads(rsp) == names)

    def test_get_event_entities(self):
        entities = ['e1', 'e2', 'e3']
        with patch.object(
            Event, 'get_entities',
            **{'return_value': entities}
        ) as m:
            endpoint = '/tobot/web/events/entities'
            self.assertTrue(m.call_count == 0)
            for i in xrange(10):
                status, msg, rsp = http.get(host, port, endpoint)
                self.assertTrue(m.call_count == 1)
                self.assertTrue(status == 200)
                self.assertTrue(json.loads(rsp) == entities)

    def test_get_event_tags(self):
        tags = ['k1=v1', 'k2=v2', 'k3=v3']
        with patch.object(
            Event, 'get_tags',
            **{'return_value': tags}
        ) as m:
            endpoint = '/tobot/web/events/tags'
            self.assertTrue(m.call_count == 0)
            for i in xrange(10):
                status, msg, rsp = http.get(host, port, endpoint)
                self.assertTrue(m.call_count == 1)
                self.assertTrue(status == 200)
                self.assertTrue(json.loads(rsp) == tags)

    def test_get_events(self):
        # ensure default limit
        endpoint = '/tobot/web/events'
        status, msg, rsp = http.get(host, port, endpoint)
        events = json.loads(rsp)
        self.assertTrue(len(events) <= 1000)


if __name__ == '__main__':
    unittest.main()
