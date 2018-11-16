
class State(object):
    def __init__(self, state, reason):
        self.state = state
        self.reason = reason


class WfStates(object):
    scheduling = State('scheduling', 'the workflow is in the running queue of executor.')
    running = State('running', 'the workflow is running.')
    interacting = State('interacting', 'the workflow is waiting for user decision.')
    waiting = State('waiting', 'the workflow is waiting for specific event to occur.')
    asking = State('asking', 'the workflow is asking the user for decision.')
    successful = State('successful', 'the workflow is successful with no exception.')
    failed = State('failed', 'the workflow is failed with exception.')
    crashed = State('crashed', 'the workflow is failed because system is crash.')
