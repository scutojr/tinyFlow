from .admin import bp as admin
from .workflow import bp as workflow
from .prop_mgr import bp as prop_mgr
from .web import bp as web


__all__ = [
    'admin',
    'workflow',
    'prop_mgr',
    'web'
]
