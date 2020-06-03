from flask import abort, Blueprint, g, request

from rapidpro_webhooks.apps.core.decorators import limit
from rapidpro_webhooks.apps.core.helpers import create_response, rule_link

mvrs_bp = Blueprint('mvrs', __name__)


@mvrs_bp.route('/', methods=['GET'])
def home():
    return create_response({'app': 'MVRS'})


@mvrs_bp.route('/notify-birth', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def notify_birth():
    data = request.json
    if data:
        data.update({'type': 'birth'})
        g.db.save_doc(data)
        docid = data['_id']

        return create_response({'id': docid,
                                '_links': {'self': rule_link(request.url_rule)}})
    abort(400)


@mvrs_bp.route('/notify-death', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def notify_death():
    data = request.json
    if data:
        data.update({'type': 'death'})
        g.db.save_doc(data)
        docid = data['_id']

        return create_response({'id': docid,
                                '_links': {'self': rule_link(request.url_rule)}})
    abort(400)
