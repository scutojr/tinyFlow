from .admin import bp as admin
from .workflow import bp as workflow
from .prop_mgr import bp as prop_mgr
from .web import bp as web
from .stat import bp as stat


__all__ = [
    'admin',
    'workflow',
    'prop_mgr',
    'web',
    'stat'
]
