from ..api import api  # Circular, but safe

from flask import request
from flask import abort
from flask import g

from ..decorators import limit
from ..helpers import rule_link
from ..helpers import create_response


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
