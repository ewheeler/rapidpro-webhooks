from flask import Response
from flask import request

from api import api  # Circular, but safe
from .decorators import limit
from .helpers import get_serializer


def _create_serialized_response(response_data):
    # if request includes format argument, use it.
    # use json by default
    response_format = request.args.get('format', 'json')
    # get appropriate serializer function and content type
    # for the requested format
    func, response_content_type = get_serializer(response_format)
    # return response object with serialized data and content_type
    return Response(func(response_data), content_type=response_content_type)


@api.route('/contact', methods=['GET'])
@limit(max_requests=10, period=60, by="ip")
def contact():
    return _create_serialized_response({'contacts': [{'name': 'evan',
                                        'identity': {'mode': 'msisdn',
                                                     'id': '1234'},
                                        'product': 'ureport',
                                        'location': 'kampala'}]})
