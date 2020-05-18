from flask import abort, g, request

from api.v1.api import api  # Circular, but safe
from api.v1.decorators import limit
from api.v1.helpers import create_response, rule_link


@api.route('/mvrs/notify-death', methods=['POST'])
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
