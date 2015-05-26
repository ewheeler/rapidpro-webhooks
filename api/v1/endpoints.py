from flask import request
from flask import current_app

from api import api  # Circular, but safe

from .decorators import limit
from .helpers import create_response
from .helpers import rule_link

# import endpoints in other modules
import thousand
import ureport
import mvrs
import eum
import places


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
