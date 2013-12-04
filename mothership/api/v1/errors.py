from flask import jsonify

from api import api

from resources import base
from resources import contact


@api.errorhandler(contact.ValidationError)
def handle_contact_validation_error(error):
    response = jsonify({
        'msg': error.message,
        'type': 'validation',
        'field': error.field})
    response.status_code = 400
    return response


@api.errorhandler(base.ResourceUnavailableError)
def handle_resource_unavailable_error(error):
    response = jsonify({
        'msg': error.message,
        'type': 'server',
        'resource': error.resource})
    response.status_code = 500
    return response
