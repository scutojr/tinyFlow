from random import randint

from wf.server.reactor import EventState
from wf import WorkflowBuilder, EventSubcription


event_name = 'stop_service'
wf_name = 'user_decision'


wf = WorkflowBuilder(wf_name, event_subscriptions=[
    EventSubcription(event_name, 'critical'),
    EventSubcription(event_name, 'info'),
    EventSubcription(event_name, 'warning')
])


WAIT_MS = 2 * 1000


@wf.task('receive_service_stop_alert', entrance=True)
def receive_service_stop_alert():
    wf.ask(
        'try to stop service, but threshold has been reached today',
        ['yes', 'no'],
        'handle_user_decision'
    )

@wf.task('handle_user_decision')
def handle_user_decision():
    wf.log('user decison is ' + wf.get_decision())
    wf.end()
