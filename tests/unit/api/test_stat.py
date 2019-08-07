import time
import json
import unittest
from random import randint

import tests.utils.http as http
import tests.utils.db as db

from wf.stat import TTR


HOST, PORT = 'localhost', 54321


class TestStatApi(unittest.TestCase):

    def setUp(self):
        db.connect()
        self.cnt_ttr = 0
        self.cnt_point = 10
        self.qry_key = ''
        self._create_ttrs()

    def tearDown(self):
        db.drop(TTR)

    def _create_ttrs(self):
        self.cnt_ttr = 20
        self.cnt_point = 10
        self.qry_key = 'name-0,localhost,cluster=test_cluster,realm=test'
        names = ['name-' + str(i) for i in xrange(self.cnt_ttr)]

        cnt_point = self.cnt_point
        interval = 20 * 1000
        start = int(time.time()) * 1000 - cnt_point * interval
        ttrs = [[start + interval * i, randint(1, 10)] for i in xrange(cnt_point)]
        mttr = sum([t[1] for t in ttrs]) / cnt_point
        for name in names:
            ttr = TTR(
                name=name,
                entity='localhost',
                tags={'cluster': 'test_cluster', 'realm': 'test'},
                state='info',
                timestamp=ttrs[-1][0],
                mttr=0.1,
                ttrs=ttrs
            )
            ttr.id = TTR.compute_id(ttr.name, ttr.entity, ttr.tags)
            ttr.save()

    def test_get_ttrs(self):
        endpoint = '/tobot/stat/ttrs/'
        status, reason, msg = http.get(HOST, PORT, endpoint)

        self.assertTrue(status == 200)
        ttrs = json.loads(msg)
        self.assertTrue(len(ttrs) == self.cnt_ttr)
        for ttr in ttrs:
            # ensure the ttrs array is not returned, which will get
            # giant as time go by
            self.assertTrue(not ttr.get('ttrs', None))

        # ensure descending order of mttr value
        for i in xrange(1, len(ttrs)):
            self.assertTrue(ttrs[i]['mttr'] >= ttrs[i-1]['mttr'])

        # test pagination
        skip, limit = int(self.cnt_ttr/2), 2
        ttr = ttrs[skip]
        endpoint = '%s?skip=%s&limit=%s' % (endpoint, skip, limit)
        status, reason, msg = http.get(HOST, PORT, endpoint)
        ttrs = json.loads(msg)
        self.assertTrue(status == 200)
        self.assertTrue(ttr == ttrs[0])
        self.assertTrue(len(ttrs) > 0 and len(ttrs) <= 2)

    def test_get_ttr_timeline(self):
        endpoint = '/tobot/stat/ttrs/%s/?limit=5' % self.qry_key
        status, reason, msg = http.get(HOST, PORT, endpoint)

        self.assertTrue(status == 200)
        ttr = json.loads(msg)
        self.assertTrue(len(ttr['ttrs']) == 5)


if __name__ == '__main__':
    unittest.main()
