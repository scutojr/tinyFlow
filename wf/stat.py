from time import time
from md5 import md5
from threading import Thread, Timer
from Queue import Queue, Empty

import mongoengine as me

from wf.utils import now_ms
from wf.reactor import Event, EventState


TTR_CNT = 10
LAST_24H_MS = 24 * 3600 * 1000
INFO = EventState.INFO


class StatDriver(Thread):
    def __init__(self):
        super(StatDriver, self).__init__()
        self.q = Queue()
        self.running = False
        self.timer = None

    def add_event(self, event):
        self.q.put(event)

    def _compute_ttr(self, event):
        TTR.update_ttr(event)

    def _compute_mttr(self, continued=True):
        ttrs = TTR.objects.fields(slice__ttrs=-1*TTR_CNT).only('id', 'ttrs', 'mttr')
        for ttr in ttrs:
            ttr.update_mttr()
        if continued:
            self._setup_timer()

    def _setup_timer(self):
        now = int(time())
        next_midnight =  LAST_24H_MS - now % LAST_24H_MS
        self.timer = Timer(next_midnight, self._compute_mttr)
        self.timer.start()

    def run(self):
        self.running = True
        self._setup_timer()
        while self.running:
            try:
                event = self.q.get(timeout=5)
                self._compute_ttr(event)
            except Empty as e:
                pass

    def stop(self):
        self.running = False
        self.timer.cancel()
        self.join()


class TTR(me.Document):
    id = me.StringField(primary_key=True)
    name = me.StringField()
    entity = me.StringField()
    tags = me.DictField()

    state = me.StringField(default='')
    timestamp = me.IntField(default=0)
    ttrs = me.ListField() # element: [<timestamp>, <ttr>]

    mttr = me.FloatField(default=0)

    meta = {
        'indexes': [
            'mttr'
        ]
    }

    def update_mttr(self):
        id = self.id
        assert id != None
        size = len(self.ttrs)
        if size == 0:
            return 0
        else:
            mttr = sum([ttr for t, ttr in self.ttrs]) * 1.0 / len(self.ttrs)
            self.modify(set__mttr=mttr)

    @classmethod
    def get_in_descending(cls, skip, limit):
        return (
            cls.objects
            .skip(skip)
            .limit(limit)
            .order_by('-mttr')
            .exclude('ttrs')
        )

    @classmethod
    def get_ttr_timeline(cls, ttr_id, skip, limit):
        """
        :return: None or TTR instance
        """
        return (
            cls.objects(id=ttr_id)
            .fields(slice__ttrs=[skip, limit])
            .first()
        )

    @staticmethod
    def from_event(event):
        id = TTR.compute_id(event.name, event.entity, event.tags)
        return TTR.objects(id=id).first()

    @staticmethod
    def compute_id(name, entity, tags):
        m = md5()
        m.update(name + ',' + entity)
        if tags:
            items = tags.items()
            items.sort(key=lambda e: e[0])
            for k, v in items:
                m.update(k + ',' + v)
        return m.hexdigest()

    @staticmethod
    def update_ttr(event):
        id = TTR.compute_id(event.name, event.entity, event.tags)
        ttr = TTR.objects(id=id).fields(state=1, timestamp=1).first()
        if ttr:
            if event.state == INFO:
                if ttr.state != INFO:
                    diff = event.start - ttr.timestamp
                    ttr.modify(
                        set__state=INFO,
                        set__timestamp=event.start,
                        push__ttrs=[ttr.timestamp, diff]
                    )
            elif ttr.state == INFO:
                ttr.modify(
                    set__state=event.state,
                    set__timestamp=event.start
                )
        else:
            ttr = TTR(
                id=id,
                name=event.name,
                entity=event.entity,
                tags=event.tags,
                state=event.state,
                timestamp=event.start
            )
            ttr.save()

