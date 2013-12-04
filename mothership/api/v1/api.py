from flask import Blueprint
from flask import g
from flask import current_app

api = Blueprint('api', __name__)

import endpoints


@api.after_request
def inject_rate_limit_headers(response):
    try:
        max_requests, remaining, reset = map(int, g.view_limits)
    except (AttributeError, ValueError):
        return response
    else:
        response.headers.add('X-Startrac-RateLimit-remaining', remaining)
        response.headers.add('X-Startrac-RateLimit-limit', max_requests)
        response.headers.add('X-Startrac-RateLimit-reset', reset)
        return response


@api.after_request
def inject_debug_headers(response):
    for attr in current_app.env_attrs.keys():
        response.headers.add('X-Startrac-Debug-%s' % (attr),
                             getattr(current_app, attr))
    return response
