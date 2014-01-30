from flask import request

from api import api  # Circular, but safe

from .decorators import limit
from .helpers import rule_link
from .helpers import create_response

from .resources.session import SessionResource

sessions = SessionResource()


@api.route('/session/new', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def create_session():
    identity = request.values.get('identity')
    source = request.values.get('source')
    product = request.values.get('product')
    session = sessions.create(identity=identity, source=source,
                              product=product)
    session.update({'_links': {'self': rule_link(request.url_rule)}})
    return create_response(session)


@api.route('/session', methods=['GET', 'POST'])
@limit(max_requests=10, period=60, by="ip")
def update_session():
    data = request.values.get('data')
    session_id = request.values.get('id')
    session = sessions.get(id=session_id)
    if session is not None:
        session = sessions.update(id=session_id, data=data)
        session.update({'_links': {'self': rule_link(request.url_rule)}})
    return create_response(session)
