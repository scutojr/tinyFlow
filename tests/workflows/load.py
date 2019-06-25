from wf import WorkflowBuilder, EventSubcription


wf = WorkflowBuilder('load', event_subscriptions= [
    EventSubcription('load', 'critical')
])

@wf.task('task start', entrance=True, **{
    'succeed': 'task b',
    'fail': 'task c',
})
def start():
    msg = 'I am task start. Go to task b.'
    wf.set_prop('task start', 'yes')
    wf.log(msg)
    wf.goto('task b')


@wf.task('task b')
def b():
    msg = 'I am b. Go to task end.'
    wf.set_prop('task b', 'yes')
    wf.log(msg)
    wf.goto('task end')


@wf.task('task c')
def c():
    msg = 'I am c. Go to task end.'
    wf.set_prop('task c', 'yes')
    wf.log(msg)
    wf.goto('task end')


@wf.task('task end')
def end():
    msg = 'This is end task'
    print 'show wf topology:', str(wf)
    wf.set_prop('task end', 'yes')
    wf.log(msg)
    wf.end()
