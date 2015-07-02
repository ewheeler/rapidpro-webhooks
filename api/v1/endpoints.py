from flask import request
from flask import current_app
from flask import jsonify

from api import api  # Circular, but safe

from .decorators import limit
from .helpers import create_response
from .helpers import rule_link
from . import exceptions

# import endpoints in other modules
import thousand
import ureport
import mvrs
import eum
import places
from vouchers.views import validate_voucher


@api.route('/', methods=['GET'])
@limit(max_requests=10, period=60, by="ip")
def list_resources():
    # http://en.wikipedia.org/wiki/HATEOAS
    children = []
    for rule in current_app.url_map.iter_rules():
        # e.g, `api.list_resources`
        if rule.endpoint.startswith(api.name):

            # don't add current endpoint as child
            if rule.endpoint != request.url_rule.endpoint:
                children.append(rule_link(rule))

    return create_response({'_links': {
                            'self': rule_link(request.url_rule),
                            'child': children}})


@api.route('/fail', methods=['GET', 'POST'])
def fail():
    return create_response({'lolz': 1 / 0})


@api.errorhandler(exceptions.RateLimitError)
def handle_rate_limit_error(error):
    response = jsonify({
        'type': 'client',
        'message': error.message,
        'resource': error.resource})
    response.status_code = error.status_code or 429
    return response


@api.errorhandler(exceptions.APIError)
def handle_api_error(error):
    response = jsonify({
        'type': 'client',
        'message': error.message,
        'resource': error.resource,
        'field': error.field})
    response.status_code = error.status_code or 400
    return response
