import datetime
import json

from ..api import api  # Circular, but safe

from flask import request
from flask import abort
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

def _url_for_entity(entity_id):
    return NOMENKLATURA_URL + '/' + entity_id


@api.route('/nomenklatura/entity', methods=['GET',])
@limit(max_requests=1000, period=60, by="ip")
def nomenklatura_retrieve_entity_attributes():

    data = request.values

    if data:
        if 'entity' not in data:
            raise exceptions.APIError(message='Missing field: entity',
                                      field='entity',
                                      resource=rule_link(request.url_rule))

        payload = {'format': 'json'}
        payload['api_key'] = NOMENKLATURA_API_KEY

        result = requests.get(_url_for_entity(data['entity']),
                              json=payload)
        results = result.json()

        if 'attribute' in data:
            query = data['attribute']
            if (results.get('attributes') is not None) and (query in results['attributes'].keys()):
                return create_response({'entity': results,
                                        query: results['attributes'][query],
                                        '_links': {'self':
                                                    rule_link(request.url_rule)}})
            else:
                return create_response({'entity': results,
                                        query: None,
                                        '_links': {'self':
                                                    rule_link(request.url_rule)}})

        return create_response({'entity': results,
                                '_links': {'self':
                                            rule_link(request.url_rule)}})

    abort(400)

@api.route('/nomenklatura/entity', methods=['POST',])
@limit(max_requests=1000, period=60, by="ip")
def nomenklatura_update_entity_attributes():
    data = request.values

    if data:
        if 'entity' not in data:
            raise exceptions.APIError(message='Missing field: entity',
                                      field='entity',
                                      resource=rule_link(request.url_rule))
        if 'attributes' not in data:
            raise exceptions.APIError(message='Missing field: attributes',
                                      field='attributes',
                                      resource=rule_link(request.url_rule))

        # rapidpro doesnt send json post data. instead we'll have a form field
        # with a json string inside rather than a dict from request.json
        if not isinstance(data['attributes'], dict):
            try:
                # request.values is a CombinedMultiDict, so convert to dict
                data = data.to_dict()
                data['attributes'] = json.loads(data['attributes'])
            except json.JSONDecodeError:
                # we didn't get json or anything json-like, so abort
                abort(400)

        payload = {'format': 'json'}
        payload['api_key'] = NOMENKLATURA_API_KEY

        result = requests.get(_url_for_entity(data['entity']),
                              json=payload)
        results = result.json()

        # update endpoint requires name
        payload['name'] = results['name']
        updated_attributes = results['attributes']
        updated_attributes.update(data['attributes'])

        # attribute values for nomenklatura must be strings (no ints!)
        # as nomenklatura uses postgres' hstore to store attribute kv pairs
        # TODO this smells dodgy
        payload['attributes'] = {str(k): str(v) for k,v in updated_attributes.items()}

        result = requests.post(_url_for_entity(data['entity']),
                               headers=NOMENKLATURA_HEADERS,
                               json=payload)

        # TODO pass on a better error message from nomenklatura if non200
        if result.status_code == requests.codes.ok:
            return create_response({'entity': result.json(),
                                    '_links': {'self':
                                                rule_link(request.url_rule)}})
    abort(400)
