from random import randint

# TODO: organize the EventState to a proper package
# TODO: so that the client lib know as little detail of server code as possible
from wf.server.reactor import EventState
from wf import context, WorkflowBuilder, EventSubcription


event_name = 'server_down'
wf_name = 'waited_workflow'


wf = WorkflowBuilder(wf_name, event_subscriptions=[
    EventSubcription(event_name, 'critical')
])


WAIT_MS = 2 * 1000


@wf.task('handle_server_down', entrance=True)
def handle_server_down():
    # import pudb
    # pudb.set_trace()
    maintainant = False
    if maintainant:
        context.log('server is already under maintainance mode')
        wf.end()
        return
    context.log('receiving server down. wait %s ms for its recovery.' % WAIT_MS)
    event = context.source_event
    # TODO: implement "goto" of wait method
    # TODO: implement "on_timeout" of wait method
    wf.wait(
        event, EventState.INFO, WAIT_MS,
        goto='reboot_succeed',
        on_timeout='reboot_failed'
    )


@wf.task('reboot_succeed')
def reboot_succeed():
    context.log('check rebbot reason: ' + 'kernel panic')
    wf.goto('check_server_health', 'check server health after server reboot.')


@wf.task('check_server_health')
def check_server_health():
    context.log('the server is healthy')
    num = randint(1, 2)
    if num == 1:
        wf.goto('start_all_service', 'server is healthy')
    else:
        wf.goto('start_all_service', 'server is unhealthy, there is some hardware error')


@wf.task('start_all_service')
def start_all_service():
    context.log('start: dn, nn, regionServer')
    wf.end()


@wf.task('repair_the_server')
def repair_the_server():
    context.log('trigger repair workflow')
    wf.end()


@wf.task('reboot_failed')
def reboot_failed():
    key_node = False
    if key_node:
        wf.goto('notify_admin')
        return
    context.log()
    event = context.source_event
    wf.wait(
        event, EventState.INFO, WAIT_MS,
        goto='reboot_succeed',
        on_timeout='reboot_failed'
    )


@wf.task('notify_admin')
def notify_admin():
    num = randint(1, 2)
    if num == 1:
        context.log('notify instantly')
    else:
        context.log('notify _at_work_hour')
