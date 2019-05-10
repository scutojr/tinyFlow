import os.path as op
from ConfigParser import ConfigParser


HOME = op.abspath(op.join(op.dirname(__name__), '..'))


_built_in_vars = [
    ('HOME', HOME), # root dir of this project
]


configuration = None
 

def _render(value):
    for tag, v in _built_in_vars:
        value.replace('$' + tag, v)
    return value


def load(file_path):
    """
    rtype: Configuration
    """
    global configuration
    section, conf = 'tinyFlow', Configuration()
    parser = ConfigParser()
    if parser.read(file_path) < 1:
        raise Exception('failed to load %s, it may not exist!' % (file_path))
    for name, value in parser.items(section):
        conf.set(name, _render(value))
    configuration = conf
    return conf


class Configuration(object):
    def __init__(self):
        self.props = {}

    def get(self, name, default=None):
        return self.props.get(name, default)

    def set(self, name, value):
        self.props[name] = value
