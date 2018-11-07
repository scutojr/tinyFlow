from time import sleep

from wf import context, WorkflowBuilder


wf = WorkflowBuilder('sleepy_wf')
SLEEP_S = 2


@wf.task('task start', **{
    'succeed': 'task b',
    'fail': 'task c',
})
def start():
    msg = 'I am task start. Go to task b.'
    context.set_prop('task start', 'yes')
    context.log(msg)
    wf.goto('sleepy task')


@wf.task('sleepy task')
def sleepy():
    msg = 'I am sleepy task. Go to task end.'
    context.set_prop('sleepy task', 'yes')
    context.log(msg)
    sleep(SLEEP_S)
    wf.goto('task end')


@wf.task('task end')
def end():
    msg = 'This is end task'
    print 'show wf topology:', str(wf)
    context.set_prop('task end', 'yes')
    context.log(msg)
    wf.end()
