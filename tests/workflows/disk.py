from wf.workflow import (
    Variable,
    WorkflowBuilder,
    EventSubcription
)


desc = '''
this is a workflow for handling disk error automatically
'''

subscribe  = [
    EventSubcription('disk', 'warning'),
    EventSubcription('disk', 'critical')
]


v1 = Variable('is_task_start')
v2 = Variable('is_task_b_start')
v3 = Variable('is_task_c_start')
v4 = Variable('is_task_end')


wf = WorkflowBuilder('disk', desc=desc, event_subscriptions = subscribe)


@wf.task('task start', entrance=True, **{
    'succeed': 'task b',
    'fail': 'task c',
})
def start():
    msg = 'I am task start. Go to task b.'
    v1.set('yes')
    wf.log(msg)
    wf.goto('task b')


@wf.task('task b')
def b():
    msg = 'I am b. Go to task end.'
    wf.set_prop('task b', 'yes')
    v2.set('yes')
    wf.log(msg)
    wf.goto('task end')


@wf.task('task c')
def c():
    msg = 'I am c. Go to task end.'
    v3.set('yes')
    wf.log(msg)
    wf.goto('task end')


@wf.task('task end')
def end():
    msg = 'This is end task'
    print 'show wf topology:', str(wf)
    v4.set('yes')
    wf.log(msg)
    wf.end()
