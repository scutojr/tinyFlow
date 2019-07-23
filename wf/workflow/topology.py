
class Topology(object):
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self._tasks = {}
        self._graph = {}
        self._entrance = None

    def add_task(self, task_name, func, entrance=False, **to):
        self._tasks[task_name] = func
        self._graph[task_name] = to
        if entrance:
            self._entrance = task_name

    def get_task(self, task_name):
        """
        :return: func or None
        """
        return self._tasks.get(task_name, None)

    def default_end(self):
        pass

    def default_timeout_task(self):
        pass

    @property
    def entrance(self):
        return self._entrance

    def validate(self):
        assert self._entrance is not None

    def workflow_info(self):
        return {
            'name': self.name,
            'description': self.desc,
            'graph': self._graph,
            'entrance': self._entrance
        }
