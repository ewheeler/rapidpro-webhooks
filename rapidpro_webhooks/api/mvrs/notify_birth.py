from flask import abort, g, request

from rapidpro_webhooks.api.api import api  # Circular, but safe
from rapidpro_webhooks.api.decorators import limit
from rapidpro_webhooks.api.helpers import create_response, rule_link


@api.route('/mvrs/notify-birth', methods=['POST'])
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
