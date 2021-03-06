from flask import Blueprint
from flask import g
from flask import request
from flask import current_app
import couchdbkit

import serializers

# register msgpack serializer (json is registered by default)
serializers.registry.register(serializers.MsgpackSerializer, 'msgpack')

# define blueprint
api = Blueprint('api', __name__)

# import endpoints AFTER defining blueprint and registering serializers
import endpoints

# TODO should load options from settings!
# TODO should this live here or in server.py
cdb_server = couchdbkit.Server()


@api.before_request
def select_datastore():
    # TODO this gets/creates a couchdb database with the name of
    # whatever comes next after /api/v1/ in the path.
    # which assumes the convention of grouping endpoints
    # by path fragment. would like to use the enclosing
    # module (e.g., all endoints in the mvrs module) but
    # that might be less flexible...
    # this smells error-prone, though...

    # remove empty strings
    fragments = [fragment for fragment in request.url_rule.rule.split('/') if fragment]

    if len(fragments) > 2:
        # ['api', 'v1']
        service = fragments[2]
    else:
        service = 'rpwebhooks'

    g.db = cdb_server.get_or_create_db(service)


@api.after_request
def inject_rate_limit_headers(response):
    try:
        max_requests, remaining, reset = map(int, g.view_limits)
    except (AttributeError, ValueError):
        return response
    else:
        response.headers.add('X-RateLimit-remaining', remaining)
        response.headers.add('X-RateLimit-limit', max_requests)
        response.headers.add('X-RateLimit-reset', reset)
        return response


@api.after_request
def inject_debug_headers(response):
    for attr in current_app.env_attrs.keys():
        response.headers.add('X-RPWebhooks-Debug-%s' % (attr),
                             getattr(current_app, attr))
    return response
