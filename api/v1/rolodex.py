from flask import request

from api import api  # Circular, but safe

from .decorators import limit
from .helpers import rule_link
from .helpers import create_response

from .resources.contact import ContactResource
from .resources.group import GroupResource

contacts = ContactResource()
groups = GroupResource()


@api.route('/contact', methods=['GET'])
@limit(max_requests=10, period=60, by="ip")
def get_contact():
    result = contacts.get()
    return create_response({'contacts': result,
                            '_links': {'self': rule_link(request.url_rule)}})


@api.route('/group/list', methods=['GET'])
@limit(max_requests=10, period=60, by="ip")
def list_groups():
    result = groups.list()
    return create_response({'groups': result,
                            '_links': {'self': rule_link(request.url_rule)}})
