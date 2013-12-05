from flask import jsonify
from flask import Response
from flask import current_app

from api import api
import exceptions
from resources import base
from resources import contact


@api.errorhandler(contact.ValidationError)
def handle_contact_validation_error(error):
    response = jsonify({
        'type': 'validation',
        'msg': error.message,
        'field': error.field})
    response.status_code = 400
    return response


@api.errorhandler(base.ResourceUnavailableError)
def handle_resource_unavailable_error(error):
    response = jsonify({
        'type': 'server',
        'msg': error.message,
        'resource': error.resource})
    response.status_code = 500
    return response


@api.errorhandler(exceptions.RateLimitError)
def handle_rate_limit_error(error):
    response = jsonify({
        'type': 'client',
        'msg': error.message,
        'resource': error.resource})
    response.status_code = error.code
    return response


@current_app.errorhandler(exceptions.APIError)
def handle_api_error(error):
    response = jsonify({
        'type': 'client',
        'msg': error.message,
        'resource': error.resource,
        'field': error.field})
    response.status_code = error.code
    return Response(response)
