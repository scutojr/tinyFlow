import time
import json
import unittest

from tests import http
from wf.executor import WfStates


HOST, PORT = 'localhost', 54321


class TestAPI(unittest.TestCase):

    def _get_wf_state(self, wf_id):
        endpoint = '/workflows/info/' + wf_id
        status, reason, msg = http.get(HOST, PORT, endpoint)
        wf = json.loads(msg)
        return wf['state']

    def test_async_wf(self):
        wf_name = 'sleepy_wf'
        endpoint = '/workflows/%s/actions/run?async=yes' % wf_name
        status, reason, wf_id = http.get(HOST, PORT, endpoint)
        time.sleep(0.5)
        self.assertTrue(self._get_wf_state(wf_id) == WfStates.running.state)
        time.sleep(2)
        self.assertTrue(self._get_wf_state(wf_id) == WfStates.successful.state)


if __name__ == '__main__':
    unittest.main()
