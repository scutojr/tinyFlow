from flask import request, send_file
from flask.blueprints import Blueprint

from wf.utils import now_ms
from wf import service_router


bp = Blueprint('admin', __name__)

wf_manager = service_router.get_wf_manager()


@bp.route('/admin/load', methods=['GET'])
def load_workflow():
    wf_manager.load_new()
    return ''


@bp.route('/admin/wf_mgr/legacy', methods=['GET'])
@bp.route('/admin/wf_mgr/legacy/', methods=['GET'])
@bp.route('/admin/wf_mgr/legacy/<version>', methods=['GET'])
def get_legacy_as_tar(version=None):
    path = wf_manager.compress_legacy_dir(version)
    return send_file(path)
