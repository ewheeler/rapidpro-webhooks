import datetime

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

NOMENKLATURA_URL = "http://nomenklatura.uniceflabs.org/api/2/datasets"
NOMENKLATURA_API_KEY = "e5d2155a-d0e5-477f-97ba-762ed14af407"


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
                                '_links': {'self':
                                           rule_link(request.url_rule)}})

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
        return 'We have recorded your %(loc_type)s as %(match)s'
    if lang.lower() == 'nep':
        return ('Tapaile lekhnubhayeko %(loc_type)s '
                'lai %(match)s bhani record gariyo')


def _format_type(loc_type):
    if loc_type.lower() in ['vdc', 'nepal-vdcs']:
        return 'VDC/Municipality'
    else:
        return 'District'


def _clean_query(query):
    exclude = set(['DISTRICT', 'VDC', 'MUNICIPALITY', 'CITY', 'TOWN',
                   'GABISA', 'NAGARPALIKA', 'JILLA'])
    query_words = set(query.upper().split())
    cleaned = query_words.difference(exclude)
    # only try to match against the first three words
    return ' '.join(list(cleaned)[:2])


def _url_for_datatype(datatype):
    if datatype == 'VDC':
        return NOMENKLATURA_URL + '/nepal-vdcs/reconcile'
    if datatype == 'District':
        return NOMENKLATURA_URL + '/nepal-districts/reconcile'


def _url_for_dataset(dataset):
    return NOMENKLATURA_URL + '/' + dataset + '/reconcile'


@api.route('/nomenklatura/reconcile', methods=['GET', 'POST'])
@limit(max_requests=1000, period=60, by="ip")
def nomenklatura():
    # TODO better logging
    log = dict({'timestamp': datetime.datetime.utcnow().isoformat()})

    if request.json is not None:
        data = request.json
    else:
        data = request.values

    if data:
        try:
            # `data` is likely werkzeug's ImmutableDict inside a
            # CombinedMultiDict so try to cast with `to_dict`
            log.update({'request_data': data.to_dict()})
        except AttributeError:
            # `data` can also be a vanilla dict
            log.update({'request_data': data})

        payload = {'format': 'json'}
        # titlecase the query for better chance of exact match
        payload['query'] = _clean_query(data['query']).title()
        payload['api_key'] = NOMENKLATURA_API_KEY

        log.update({'nomenklatura_payload': payload})
        result = requests.get(_url_for_dataset(data['dataset']),
                              params=payload)
        results = result.json()

        matches = list()
        for match in results['result']:
            if match['match'] is True:
                matches.append(match)
            else:
                if match['score'] >= 50:
                    matches.append(match)

        log.update({'nomenklatura_response': results})
        log.update({'matches': matches})
        g.db.save_doc(log)

        if len(matches) < 1:
            return create_response({'message': _localized_fail(data.get('lang', 'eng')) % _format_type(data['dataset']),
                                    'match': None,
                                    '_links': {'self':
                                               rule_link(request.url_rule)}})
        else:
            return create_response({'message': _localized_success(data.get('lang', 'eng')) % {'loc_type': _format_type(data['dataset']), 'match': matches[0]['name']},
                                    'match': matches[0]['name'],
                                    '_links': {'self':
                                               rule_link(request.url_rule)}})

    abort(400)
