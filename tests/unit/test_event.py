import unittest
from mock import Mock, patch
from wf.server.reactor.event import Event, EventState

import tests.utils.db as db


class TestEvent(unittest.TestCase):

    def setUp(self):
        db.connect()
        self._generate_data()

    def tearDown(self):
        db.drop(Event)
        db.disconnect()

    def _generate_data(self):
        self.names = ['name-' + str(n) for n in xrange(10)]
        self.entities = ['host-' + str(n) for n in xrange(10)]
        tags = [
            ['key-' + str(k), 'value-' + str(v)]
            for k in xrange(5)
            for v in xrange(3)
        ]
        self.tags = [
            dict(tags[0::3]), dict(tags[1::3]), dict(tags[2::3])
        ]
        starts = [100, 200, 300, 400, 500]

        for state in EventState.alls:
            for i in xrange(len(self.names)):
                name, entity = self.names[i], self.entities[i]
                for ts in self.tags:
                    for start in starts:
                        Event(
                            name=name, entity=entity, tags=ts, start=start
                        ).save()

    def test_get_names(self):
        names = Event.get_names()
        self.assertTrue(
            set(names) == set(self.names)
        )

    def test_get_entities(self):
        entities = Event.get_entities()
        self.assertTrue(
            set(entities) == set(self.entities)
        )

    def test_get_tags(self):
        target_tags = set()
        for ts in self.tags:
            for k, v in ts.iteritems():
                target_tags.add('%s=%s' % (k, v))

        tags = Event.get_tags()
        print tags
        self.assertTrue(tags == target_tags)

    def test_query(self):
        all_event = Event.query()
        cnt_all = all_event.count()

        def test_time_based_query():
            events_1 = Event.query(start_after=300)
            events_2 = Event.query(start_before=300)
            events_3 = Event.query(start_after=200, start_before=400)

            self.assertTrue(events_1.count()*10 == cnt_all*4)
            self.assertTrue(events_2.count()*10 == cnt_all*6)
            self.assertTrue(events_3.count()*10 == cnt_all*4)

        test_time_based_query()
        query_by_name = Event.query(name=self.names[0])
        query_by_entity= Event.query(entity=self.entities[0])
        self.assertTrue(query_by_name.count() == query_by_entity.count())


if __name__ == '__main__':
    unittest.main()
