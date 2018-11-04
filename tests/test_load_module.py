import pudb
import platform
import os.path as op

from wf.workflow import WorkflowManager

# pudb.set_trace()


WINDOW = 'Windows'
LINUX = 'Linux'


cur_sys = platform.system()
pack_dir = op.dirname(op.abspath(__file__)) + (cur_sys == WINDOW and '\\' or '/') + 'workflows'
manager = WorkflowManager(pack_dir)
print manager.get_workflows()
