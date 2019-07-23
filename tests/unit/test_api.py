import time
import json
import unittest

from tests import http
from wf.reactor import Event, EventState


HOST, PORT = 'localhost', 54321


class TestAPI(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_wf_state(self, wf_id):
        if isinstance(wf_id, dict):
            wf_id = wf_id['$oid']
        endpoint = '/tobot/workflows/' + wf_id + '/execution'
        status, reason, msg = http.get(HOST, PORT, endpoint)
        return msg.strip()

    def _get_event(self, name, entity='ojr-test', state='critical', tags={}):
        default = {'cluster': 'jy', 'role': 'DataNode', 'ip': '10.11.12.13'}
        default.update(tags)
        return Event(
            name=name, entity=entity, state=state,
            tags=default
        )

    def test_user_define_param(self):
        def call(change=None, event=None):
            wf_name = 'define_param_wf'
            endpoint = '/tobot/reactor/workflows/' + wf_name
            if change:
                endpoint += '?change=' + str(change)
            if event is None:
                rc, reason, wf_ids = http.get(HOST, PORT, endpoint)
            else:
                rc, reason, wf_ids = http.post(HOST, PORT, endpoint, event.to_json())
            return json.loads(wf_ids)

        ename, estate = 'test_event_param', 'warning'

        wf_ids = call('new_value')
        for wf_id in wf_ids:
            self.assertTrue(self._get_wf_state(wf_id) == 'succeed')

        wf_ids = call('new_value', self._get_event(ename, state=estate))
        for wf_id in wf_ids:
            self.assertTrue(self._get_wf_state(wf_id) == 'succeed')

        wf_ids = call('new_value', self._get_event(ename, state=estate, tags={'cluster': 'wrong cluster'}))
        for wf_id in wf_ids:
            self.assertTrue(self._get_wf_state(wf_id) == 'failed')

        wf_ids = call()
        for wf_id in wf_ids:
            self.assertTrue(self._get_wf_state(wf_id) == 'failed')

    def test_async_wf_and_wf_state(self):
        wf_name = 'sleepy_wf'
        endpoint = '/tobot/reactor/workflows/?async=yes'
        event = self._get_event('sleepy_test')
        status, reason, wf_ids = http.post(HOST, PORT, endpoint, event.to_json())
        wf_ids = json.loads(wf_ids)
        time.sleep(2)

        self.assertTrue(len(wf_ids) > 0)

        for wf_id in wf_ids:
            self.assertTrue(self._get_wf_state(wf_id) == 'running')
        time.sleep(2)
        for wf_id in wf_ids:
            self.assertTrue(self._get_wf_state(wf_id) == 'succeed')

    def test_event_driven(self):
        wf_name = 'waited_workflow'
        event_name = 'server_down'

        endpoint = '/tobot/reactor/workflows/%s?async=yes' % wf_name
        event = self._get_event(event_name)
        status, reason, msg = http.post(HOST, PORT, endpoint, event.to_json())

        wf_ids = json.loads(msg)
        self.assertTrue(len(wf_ids) > 0)
        time.sleep(0.5)

        for wf_id in wf_ids:
            self.assertTrue(self._get_wf_state(wf_id) == 'waiting')
        time.sleep(2)

        endpoint = '/tobot/reactor/workflows/%s?async=yes' % wf_name
        event = self._get_event(event_name, state=EventState.INFO)
        status, reason, msg = http.post(HOST, PORT, endpoint, event.to_json())
        tmp = json.loads(msg)
        for wf_id in wf_ids:
            self.assertTrue(wf_id in tmp)
        time.sleep(2)

        wf_ids = tmp
        for wf_id in wf_ids:
            self.assertTrue(self._get_wf_state(wf_id) == 'succeed')

    def test_user_decision(self):
        wf_name = 'user_decision'
        event_name = 'stop_service'

        def trigger_wfs():
            endpoint = '/tobot/reactor/workflows/%s?async=yes' % wf_name
            event = self._get_event(event_name)
            status, reason, wf_ids = http.post(HOST, PORT, endpoint, event.to_json())

            wf_ids = json.loads(wf_ids)
            self.assertTrue(len(wf_ids) > 0)
            time.sleep(2)
            for wf_id in wf_ids:
                self.assertTrue(self._get_wf_state(wf_id) == 'waiting')

        def make_decision():
            # TODO: refact this url so that it can be used as merely /userDecisions
            endpoint = '/tobot/userDecisions/'
            status, reason, msg = http.get(HOST, PORT, endpoint)
            jud_handlers = json.loads(msg)
            for jh in jud_handlers:
                j = jh['judgement']
                wf_id, options = jh['wf_id']['$oid'], j['options']
                url = endpoint + jh['_id']['$oid']
                body = {
                    'judge': options[0],
                    'comment': 'xx'
                }
                status, reason, msg = http.post(HOST, PORT, url, body=json.dumps(body))
                time.sleep(0.5)
                self.assertTrue(self._get_wf_state(wf_id) == 'succeed')

        trigger_wfs()
        time.sleep(2)
        make_decision()

    def test_get_wf_history(self):
        endpoint = '/tobot/executions/'
        _, _, rsp = http.get(HOST, PORT, endpoint)
        rsp = json.loads(rsp)
        self.assertTrue(len(rsp) > 0)
        name = rsp[0]['name']

        _, _, rsp = http.get(HOST, PORT, endpoint, **{'name': name})
        rsp = json.loads(rsp)
        for wf in rsp:
            self.assertTrue(wf['name'] == name)


    def test_exception(self):
        pass


if __name__ == '__main__':
    unittest.main()
