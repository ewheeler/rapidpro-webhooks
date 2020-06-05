from flask import Blueprint, redirect, render_template

import couchdbkit
# import endpoints AFTER defining blueprint and registering serializers
from flask_login import current_user, login_required

from rapidpro_webhooks.apps.core import serializers
# register msgpack serializer (json is registered by default)
from rapidpro_webhooks.apps.core.forms import LoginForm
from rapidpro_webhooks.apps.core.models import User

serializers.registry.register(serializers.MsgpackSerializer, 'msgpack')


core_bp = Blueprint('core', __name__)

# TODO should load options from settings!
# TODO should this live here or in server.py
cdb_server = couchdbkit.Server()


@core_bp.route('/', methods=['GET'])
def index():
    return render_template('dashboard.html')


# @api_bp.before_request
# def select_datastore():
#     """
#     TODO this gets/creates a couchdb database with the name of
#     whatever comes next after /api/v1/ in the path.
#     which assumes the convention of grouping endpoints
#     by path fragment. would like to use the enclosing
#     module (e.g., all endoints in the mvrs module) but
#     that might be less flexible...
#     this smells error-prone, though...
#     """
#     # remove empty strings
#     fragments = [fragment for fragment in request.url_rule.rule.split('/') if fragment]
#
#     if len(fragments) > 2:
#         # ['api', 'v1']
#         service = fragments[2]
#     else:
#         service = 'rpwebhooks'
#
#     g.db = cdb_server.get_or_create_db(service)
#
#
# @api_bp.after_request
# def inject_rate_limit_headers(response):
#     try:
#         max_requests, remaining, reset = map(int, g.view_limits)
#     except (AttributeError, ValueError):
#         return response
#     else:
#         response.headers.add('X-RateLimit-remaining', remaining)
#         response.headers.add('X-RateLimit-limit', max_requests)
#         response.headers.add('X-RateLimit-reset', reset)
#         return response
#
#
# @api_bp.after_request
# def inject_debug_headers(response):
#     for attr in current_app.env_attrs.keys():
#         response.headers.add('X-RPWebhooks-Debug-%s' % (attr),
#                              getattr(current_app, attr))
#     return response


@core_bp.route('login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.login(form.password.data):
            return redirect('/admin')
    return render_template("admin/login.html", form=form)


@core_bp.route('logout', methods=['GET'])
@login_required
def logout():
    user = current_user
    user.logout()
    return redirect('/admin')
