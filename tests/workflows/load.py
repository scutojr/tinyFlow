from wf import context, WorkflowBuilder, EventSubcription


wf = WorkflowBuilder('load', event_subscriptions= [
    EventSubcription('load', 'critical')
])

@wf.task('task start', entrance=True, **{
    'succeed': 'task b',
    'fail': 'task c',
})
def start():
    msg = 'I am task start. Go to task b.'
    context.set_prop('task start', 'yes')
    context.log(msg)
    wf.goto('task b')


@wf.task('task b')
def b():
    msg = 'I am b. Go to task end.'
    context.set_prop('task b', 'yes')
    context.log(msg)
    wf.goto('task end')


@wf.task('task c')
def c():
    msg = 'I am c. Go to task end.'
    context.set_prop('task c', 'yes')
    context.log(msg)
    wf.goto('task end')


@wf.task('task end')
def end():
    msg = 'This is end task'
    print 'show wf topology:', str(wf)
    context.set_prop('task end', 'yes')
    context.log(msg)
    wf.end()
