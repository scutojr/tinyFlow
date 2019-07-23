from random import randint

from wf.reactor import EventState
from wf import WorkflowBuilder, Subscription


event_name = 'stop_service'
wf_name = 'user_decision'


wf = WorkflowBuilder(wf_name, event_subscriptions=[
    Subscription(event_name, 'critical'),
    Subscription(event_name, 'info'),
    Subscription(event_name, 'warning')
])


WAIT_MS = 2 * 1000


trigger = wf.trigger


@wf.task('receive_service_stop_alert', entrance=True)
def receive_service_stop_alert():
    wf.ask(
        'try to stop service, but threshold has been reached today',
        ['yes', 'no'],
        'handle_user_decision'
    )

@wf.task('handle_user_decision')
def handle_user_decision():
    wf.log('user decison is ' + trigger.judgement.decision)
    wf.end()
