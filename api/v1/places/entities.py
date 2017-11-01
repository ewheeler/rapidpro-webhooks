import datetime
import json

from ..api import api  # Circular, but safe

from flask import request
from flask import abort
from flask import make_response
from flask import jsonify
from flask import g
import requests

from ..decorators import limit
from ..helpers import rule_link
from ..helpers import create_response
from .. import exceptions


# TODO move to config
NOMENKLATURA_URL = "http://nomenklatura.uniceflabs.org/api/2/entities"
NOMENKLATURA_API_KEY = "e5d2155a-d0e5-477f-97ba-762ed14af407"
NOMENKLATURA_HEADERS = {"Authorization": "e5d2155a-d0e5-477f-97ba-762ed14af407"}


@api.route('/nomenklatura/entities', methods=['POST',])
@limit(max_requests=1000, period=60, by="ip")
def nomenklatura_create_entity():
    if request.json is not None:
        data = request.json
    else:
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
            payload['attributes'] = {str(k): str(v) for k,v in data['attributes'].items()}
        
        payload['dataset'] = data['dataset']
        payload['name'] = data['name']
        if 'description' in data:
            payload['description'] = data['description']

        result = requests.post(NOMENKLATURA_URL,
                               headers=NOMENKLATURA_HEADERS,
                               json=payload)

        if result.json().get('errors') is not None:
            abort(make_response(jsonify(message=result.json().get('errors')), 400))

        # TODO pass on a better error message from nomenklatura if non200
        if result.status_code == requests.codes.ok:
            return create_response({'entity': result.json(),
                                    '_links': {'self':
                                                rule_link(request.url_rule)}})
    abort(400)
