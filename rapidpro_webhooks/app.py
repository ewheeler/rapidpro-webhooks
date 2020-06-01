from flask import Flask, jsonify

from werkzeug.exceptions import default_exceptions, HTTPException


def make_json_app(import_name, **kwargs):
    """
    Creates a JSON-oriented Flask app.

    All error responses that you don't specifically
    manage yourself will have application/json content
    type, and will contain JSON like this (just an example):

    { "message": "405: Method Not Allowed" }
    http://flask.pocoo.org/snippets/83/
    """
    def make_json_error(ex):
        response = jsonify(message=str(ex))
        response.status_code = (ex.code
                                if isinstance(ex, HTTPException)
                                else 500)
        return response

    app = Flask(import_name, static_folder='rapidpro_webhooks/static', **kwargs)

    for code in default_exceptions.keys():
        @app.errorhandler(code)
        def page_not_found(error):
            return make_json_error(error), code

    return app
