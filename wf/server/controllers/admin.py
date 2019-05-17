from flask import request
from flask.blueprints import Blueprint

from wf import service_router


bp = Blueprint('admin', __name__)

wf_manager = service_router.get_wf_manager()


@bp.route('/admin/load', methods=['GET'])
def load_workflow():
    wf_manager.load()
    return ''
