from flask import Response
from flask import request
from flask import url_for
from flask import current_app

from api import api  # Circular, but safe
from .decorators import limit
from .helpers import get_serializer
from .resources.contact import ContactResource
from .resources.group import GroupResource

# TODO should we use
# http://flask-restful.readthedocs.org/en/latest/quickstart.html
contacts = ContactResource()
groups = GroupResource()


def _create_serialized_response(response_data):
    """ Convenience method to serialize a python dict to
        json or msgpack based on request's `format` argument
    """
    # if request includes format argument, use it.
    # otherwise use json by default
    response_format = request.args.get('format', 'json').upper()
    # get appropriate serializer function and content type
    # for the requested format
    func, response_content_type = get_serializer(response_format)
    # return response object with serialized data and content_type
    return Response(func(response_data), content_type=response_content_type)


@api.route('/contact', methods=['GET'])
@limit(max_requests=10, period=60, by="ip")
def get_contact():
    result = contacts.get()
    return _create_serialized_response({'contacts': result})


@api.route('/group/list', methods=['GET'])
@limit(max_requests=10, period=60, by="ip")
def list_groups():
    result = groups.list()
    return _create_serialized_response({'groups': result})


@api.route('/', methods=['GET'])
@limit(max_requests=10, period=60, by="ip")
def list_resources():
    result = {}
    # TODO this seems like a hacky way to do this..
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint.startswith(api.name):
            result.update({rule.endpoint.split('.')[-1]:
                           {"href": url_for(rule.endpoint, _external=True),
                            "methods": list(rule.methods)}})
    return _create_serialized_response({'resources': result})
