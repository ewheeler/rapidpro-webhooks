import json

from flask import abort, jsonify, make_response, request

import requests

from rapidpro_webhooks.apps.core import exceptions
from rapidpro_webhooks.apps.core.decorators import limit
from rapidpro_webhooks.apps.core.helpers import create_response, rule_link
from rapidpro_webhooks.apps.places import places_bp
from rapidpro_webhooks.apps.places.views import NOMENKLATURA_API_KEY, NOMENKLATURA_HEADERS, NOMENKLATURA_URL


@places_bp.route('/nomenklatura/entities', methods=['POST', ])
@limit(max_requests=1000, period=60, by="ip")
def nomenklatura_create_entity():
    data = request.values

    if data:
        if 'name' not in data:
            raise exceptions.APIError(message='Missing field: name',
                                      field='name',
                                      resource=rule_link(request.url_rule))

        if 'attributes' in data:
            # rapidpro doesnt send json post data. instead we'll have a form field
            # with a json string inside rather than a dict from request.json
            if not isinstance(data['attributes'], dict):
                try:
                    # request.values is a CombinedMultiDict, so convert to dict
                    data = data.to_dict()
                    data['attributes'] = json.loads(data['attributes'])
                except ValueError:
                    # we didn't get json or anything json-like, so abort
                    abort(400)

        payload = {'format': 'json'}
        payload['api_key'] = NOMENKLATURA_API_KEY
        # nomenklatura complains if we don't include `attributes`
        payload['attributes'] = {}

        # attribute values for nomenklatura must be strings (no ints!)
        # as nomenklatura uses postgres' hstore to store attribute kv pairs
        # TODO this smells dodgy
        if 'attributes' in data:
            payload['attributes'] = {str(k): str(v) for k, v in data['attributes'].items()}

        payload['dataset'] = data['dataset']
        payload['name'] = data['name']
        if 'description' in data:
            payload['description'] = data['description']

        result = requests.post(NOMENKLATURA_URL + 'entities',
                               headers=NOMENKLATURA_HEADERS,
                               json=payload)

        if result.json().get('errors') is not None:
            abort(make_response(jsonify(message=result.json().get('errors')), 400))

        # TODO pass on a better error message from nomenklatura if non200
        if result.status_code == requests.codes.ok:
            return create_response({'entity': result.json(),
                                    '_links': {'self': rule_link(request.url_rule)}})
    abort(400)
