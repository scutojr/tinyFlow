import time
import json
import unittest

from tests import http
from wf.executor import WfStates
from wf.server.reactor import Event, EventState


HOST, PORT = 'localhost', 54321


class TestAPI(unittest.TestCase):

    def _get_wf_state(self, wf_id):
        endpoint = '/workflows/info/' + wf_id
        status, reason, msg = http.get(HOST, PORT, endpoint)
        wf = json.loads(msg)
        return wf['state']

    def _get_event(self, name, entity='ojr-test', state='critical'):
        return Event(
            name=name, entity=entity, state=state,
            tags={'cluster': 'jy', 'role': 'DataNode', 'ip': '10.11.12.13'}
        )

    def test_async_wf_and_wf_state(self):
        wf_name = 'sleepy_wf'
        endpoint = '/reactor/workflows/%s?async=yes' % wf_name
        event = self._get_event('sleepy_test')
        status, reason, wf_ids = http.post(HOST, PORT, endpoint, event.to_json())
        wf_ids = json.loads(wf_ids)
        time.sleep(0.5)
        for wf_id in wf_ids:
            self.assertTrue(self._get_wf_state(wf_id) == WfStates.running.state)
        time.sleep(2)
        for wf_id in wf_ids:
            self.assertTrue(self._get_wf_state(wf_id) == WfStates.successful.state)

    def test_event_driven(self):
        wf_name = 'waited_workflow'
        event_name = 'server_down'

        endpoint = '/reactor/workflows/%s?async=yes' % wf_name
        event = self._get_event(event_name)
        status, reason, wf_ids = http.post(HOST, PORT, endpoint, event.to_json())

        wf_ids = json.loads(wf_ids)
        time.sleep(0.5)
        for wf_id in wf_ids:
            # self.assertTrue(self._get_wf_state(wf_id) == WfStates.waiting.state)
            print '@@@@@@@@@@@@@@@:', wf_id, self._get_wf_state(wf_id)
        time.sleep(2)

        endpoint = '/reactor/workflows/%s?async=yes' % wf_name
        event = self._get_event(event_name, state=EventState.INFO)
        status, reason, wf_ids = http.post(HOST, PORT, endpoint, event.to_json())

        time.sleep(2)
        wf_ids = json.loads(wf_ids)
        for wf_id in wf_ids:
            # self.assertTrue(self._get_wf_state(wf_id) == WfStates.successful.state)
            print '@@@@@@@@@@@@@@@:', wf_id, self._get_wf_state(wf_id)


if __name__ == '__main__':
    unittest.main()
