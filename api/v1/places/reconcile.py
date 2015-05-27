from ..api import api  # Circular, but safe

from flask import request
from flask import abort
from flask import g
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


def _localized_fail(lang=None):
    # TODO
    if lang.lower() == 'eng':
        return 'Sorry. You have entered an invalid %s'
    if lang.lower() == 'nep':
        return 'Tapaile lekhnubhayeko %s milena'


def _localized_success(lang=None):
    # TODO
    if lang.lower() == 'eng':
        return 'Thanks, we have recorded your %(loc_type)s as %(match)s'
    if lang.lower() == 'nep':
        return 'Tapaile lekhnubhayeko %(loc_type)s lai %(match)s bhane record gariyo'


@api.route('/nomenklatura/reconcile', methods=['GET', 'POST'])
@limit(max_requests=1000, period=60, by="ip")
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
        # titlecase the query for better chance of exact match
        payload['query'] = data['query'].title()
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
                # TODO analyze logs so we can see
                # if 75 is a resonable threshold
                if match['score'] >= 75:
                    matches.append(match)

        log.update({'nomenklatura_response': results})
        log.update({'matches': matches})
        g.db.save_doc(log)

        if len(matches) < 1:
            return create_response({'message': _localized_fail(data.get('lang', 'nep')) % data['type'],
                                    'match': None,
                                    '_links': {'self': rule_link(request.url_rule)}})
        else:
            return create_response({'message': _localized_success(data.get('lang', 'nep')) % {'loc_type': data['type'], 'match': matches[0]['name']},
                                    'match': matches[0]['name'],
                                    '_links': {'self': rule_link(request.url_rule)}})

    abort(400)
