from wf import context, WorkflowBuilder, EventSubcription
from wf.workflow import Parameter, ParamSource


p1 = Parameter('change', 1)
p2 = Parameter('unchange', 2)
p3 = Parameter('cluster', 'bj', ParamSource.event_tag)

wf = WorkflowBuilder('define_param_wf', event_subscriptions = [
    EventSubcription('test_event_param', 'warning'),
])


@wf.task('task start', entrance=True)
def start(change=p1, unchange=p2, cluster=p3):
    if not (change != p1 and change != p1.default) or unchange != p2.default or cluster not in ['bj', 'sh', 'jy']:
        raise Exception('wrong input parameter')
    wf.goto('task end')


@wf.task('task end')
def end():
    wf.end()
