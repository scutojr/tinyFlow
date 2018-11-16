from time import sleep

from wf.workflow import WorkFlowBuilder, EventSubcription


wf = WorkFlowBuilder('sleepy_wf', event_subscriptions=[
    EventSubcription('sleepy_test', 'critical')
])


SLEEP_S = 2


@wf.task('task start', **{
    'succeed': 'task b',
    'fail': 'task c',
})
def start():
    msg = 'I am task start. Go to task b.'
    wf.set_prop('task start', 'yes')
    wf.log(msg)
    wf.goto('sleepy task')


@wf.task('sleepy task')
def sleepy():
    msg = 'I am sleepy task. Go to task end.'
    wf.set_prop('sleepy task', 'yes')
    wf.log(msg)
    sleep(SLEEP_S)
    wf.goto('task end')


@wf.task('task end')
def end():
    msg = 'This is end task'
    print 'show wf topology:', str(wf)
    wf.set_prop('task end', 'yes')
    wf.log(msg)
    wf.end()
