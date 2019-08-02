from bson import ObjectId

from .proxy import WorkflowProxy
from .topology import Topology
from .workflow import Workflow


class WorkflowBuilder(WorkflowProxy):

    def __init__(self, name, desc='', event_subscriptions=None):
        """
        :param name:
        :param desc:
        :param event_subscriptions:
        """
        if event_subscriptions is None:
            event_subscriptions = []

        self._name = name
        self.version = 0
        self.reactor = None
        self._subscriptions = event_subscriptions
        self._vars = []
        self.topology = Topology(name, desc)
        self._is_built = False

    def setup(self, version, reactor):
        self._immutable()
        self.version = version
        self.reactor = reactor

    def task(self, task_name, entrance=False, **to):
        def internal(func):
            self.add_task(task_name, func, entrance, **to)
            return func
        return internal

    def add_task(self, task_name, func, entrance=False, **to):
        self._immutable()
        if self._is_built:
            raise Exception('Workflow can not be redefined after first building.')
        return self.topology.add_task(task_name, func, entrance=entrance, **to)

    def validate(self):
        entrance = self.topology.entrance
        assert entrance is not None, 'entrance of the workflow must be defined'
        assert self.version != '', 'version must be set before building'

        repeat = set()
        for sub in self.subscriptions:
            key = sub.to_key()
            assert key not in repeat, 'repeated subscription is not allowed'
            repeat.add(key)

    def _immutable(self):
        if self._is_built:
            raise Exception('workflow is immutable after building!')

    def build(self, workflow=None):
        """
        TODO:
            1. check building validation such as entrace must be called to set up the entrace task
            2. after build is  called, changing to the wf is prevented
        """
        self._is_built = True
        if workflow is None:
            workflow = Workflow(name=self._name, version=self.version)
        workflow.construct(self.topology, self.reactor)
        if not workflow.id:
            workflow.save()
        return workflow

    @property
    def name(self):
        return self._name

    @property
    def workflow_info(self):
        """
        :return: dict
        """
        return self.topology.workflow_info()

    @property
    def subscriptions(self):
        return self._subscriptions

    @property
    def variables(self):
        return self._vars

    def add_variable(self, variable):
        self._vars.append(variable)

