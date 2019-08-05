
class WorkflowNotFoundError(Exception):
    def __init__(self, name='', version=0):
        self.name = name
        self.version = version

    @property
    def message(self):
        return 'no workflow is found for %s-%s' % (self.name, self.version)
