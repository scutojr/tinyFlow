from wf.reactor import EventState


class Subscription(object):
    def __init__(self, event_name, event_state):
        if event_state not in EventState.alls:
            raise Exception('value of event state must be one of: ' + ','.join(EventState.alls))
        self.name = event_name
        self.state = event_state

    def to_key(self):
        return (self.name, self.state)

    def to_json(self):
        return {
            'name': self.name,
            'state': self.state
        }

    @staticmethod
    def key_from_event(event):
        return event.name, event.state

