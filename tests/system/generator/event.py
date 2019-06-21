import time
import abc
import random
import itertools

import tests.utils.db as db
from wf.server.reactor.event import Event


event_name = [
    "disk_error",
    "memory_exceed",
    "no_space_left",
    "packet_loss",
    "host_down"
]

event_entity_host = [
    "host-1",
    "host-2",
    "host-3",
    "host-4",
    "host-5",
]

event_entity_server = [
    "server-1",
    "server-2",
    "server-3",
    "server-4",
    "server-5"
]

dc_1 = {
    "dc": "guangzhou",
    "cluster": "game"
}

dc_2 = {
    "dc": "shenzhen",
    "cluster": "recommendation"
}

state = [
    "INFO",
    "WARNING",
    "CRITICAL",
    "INFO"
]

params = {
    'disk_error': {
        "reason": "dell error",
        "device": "sd1"
    }
}


def permutation(name=None, entity=None, tags=None):
    if name != None and not isinstance(name, list):
        name = [name]
    if entity != None and not isinstance(entity, list):
        entity = [entity]
    if tags != None and not isinstance(tags, list):
        tags = [tags]
    for n in name:
        for e in entity:
            for t in tags:
                yield {
                    'name': n,
                    'entity': e,
                    'tags': t
                }


class Publisher(object):
    @abc.abstractmethod
    def publish(self, event):
        pass


class StdoutPublisher(Publisher):
    def publish(self, event):
        print event.to_mongo()


class MongoPublisher(Publisher):
    def __init__(self):
        db.connect()

    def publish(self, event):
        event.save()


class EventFactory(object):

    SENTINEL = 1

    def __init__(self, publisher):
        self.running = True
        self.publisher = publisher

    def start(self):
        self.running = True
        self.run()

    def stop(self):
        pass

    def run(self):
        evolves = set()
        states = ('INFO', 'WARNING', 'CRITICAL', 'INFO')
        while self.running:
            if len(evolves) <= 0:
                evolves = {
                    self.evolve(raw_event, states)
                    for raw_event in self.populate()
                }
            to_del = set()
            for e in evolves:
                try:
                    e.next()
                except StopIteration:
                    to_del.add(e)
            else:
                for ele in to_del:
                    evolves.remove(ele)
            time.sleep(5)

    def evolve(self, raw_event, states):
        next_shot = 0
        for state in states:
            while True:
                now = time.time()
                if next_shot < now:
                    raw_event['state'] = state
                    next_shot = now + random.randint(5, 10)
                    break
                else:
                    yield
            raw_event['start'] = int(time.time() * 1000)
            self.publisher.publish(Event(**raw_event))

    def populate(self):
        return permutation(
            name=event_name,
            entity=event_entity_host,
            tags=dc_1
        )


if __name__ == '__main__':
    publisher = MongoPublisher()
    factory = EventFactory(publisher)
    factory.start()
