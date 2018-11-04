from .workflow import Workflow
from .executor import ContextProxy

__all__ = [
    'Workflow',
    'context'
]

context = ContextProxy()