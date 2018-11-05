from flask import request
from flask.blueprints import Blueprint


bp = Blueprint('admin', __name__)


@bp.route('/admin/load', methods=['GET'])
def load_workflow():
    pass
