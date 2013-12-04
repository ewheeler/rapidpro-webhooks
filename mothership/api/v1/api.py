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
        h = response.headers
        h.add('X-RateLimit-Remaining', remaining)
        h.add('X-RateLimit-Limit', max_requests)
        h.add('X-RateLimit-Reset', reset)
        return response


@api.after_request
def inject_version_headers(response):
    h = response.headers
    h.add('X-startrac-git-latest-sha', getattr(current_app, 'git_latest_sha'))
    h.add('X-startrac-git-branch', getattr(current_app, 'git_branch'))
    h.add('X-startrac-git-tag', getattr(current_app, 'git_tag'))
    h.add('X-startrac-hostname', getattr(current_app, 'hostname'))
    return response
