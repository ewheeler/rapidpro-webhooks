from ..api import api  # Circular, but safe

from flask import request
from flask import abort
from flask import g
import couchdbkit
import requests

from ..decorators import limit
from ..helpers import rule_link
from ..helpers import create_response


# TODO move these to settings!
NOMINATUM_URL = "http://nominatim.openstreetmap.org/search"

NOMENKLATURA_URL = "http://nomenklatura.uniceflabs.org/api/2/reconcile"
NOMENKLATURA_API_KEY = "er6ey12q06e63cxti91q4alpo"


@api.route('/nominatum/reconcile', methods=['GET', 'POST'])
@limit(max_requests=10, period=60, by="ip")
def nominatum():
    """ Look up a given place name on OSM via
        http://wiki.openstreetmap.org/wiki/Nominatim

        Nominatim does not do any fuzzy matching, so
        not so helpful for user-provided spellings.
    """
    if request.json is not None:
        data = request.json
    else:
        data = request.values

    if data:
        payload = {'format': 'json'}
        payload['q'] = data['query']
        country = data.get('country')
        if country:
            payload['countrycodes'] = country

        result = requests.get(NOMINATUM_URL, params=payload)
        results = result.json()

        matches = list()
        for match in results:
            if match['type'] == 'village':
                if match['class'] == 'place':
                    matches.append(match)
        return create_response({'matches': matches,
                                '_links': {'self': rule_link(request.url_rule)}})

    abort(400)


@api.route('/nomenklatura/reconcile', methods=['GET', 'POST'])
@limit(max_requests=10, period=60, by="ip")
def nomenklatura():
    # TODO better logging
    log = dict()
    if request.json is not None:
        data = request.json
    else:
        data = request.values


    if data:
        log.update({'request_data': data.to_dict()})

        payload = {'format': 'json'}
        payload['query'] = data['query']
        payload['api_key'] = NOMENKLATURA_API_KEY

        if data.get('type'):
            payload['type'] = data['type']

        log.update({'nomenklatura_payload': payload})
        result = requests.get(NOMENKLATURA_URL, params=payload)
        results = result.json()

        matches = list()
        for match in results['result']:
            if match['match'] is True:
                matches.append(match)
            else:
                # TODO log all these matches so we can see
                # if 75 is a resonable threshold
                if match['score'] >= 75:
                    matches.append(match)

        log.update({'nomenklatura_response': results})
        log.update({'matches': matches})
        g.db.save_doc(log)

        if len(matches) < 1:
            # TODO send contact's preferred language in request
            # so that these messages can be localized
            return create_response({'message': 'Sorry. You have entered an invalid %s' % data['type'],
                                    'match': None,
                                    '_links': {'self': rule_link(request.url_rule)}})
        else:
            return create_response({'message': 'Thanks, we have recorded your %s as %s' % (data['type'], matches[0]['name']),
                                    'match': matches[0]['name'],
                                    '_links': {'self': rule_link(request.url_rule)}})

    abort(400)
