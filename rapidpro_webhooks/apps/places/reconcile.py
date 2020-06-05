import datetime

from flask import abort, g, request

import requests
from simplejson import JSONDecodeError

from rapidpro_webhooks.apps.core import exceptions
from rapidpro_webhooks.apps.core.decorators import limit
from rapidpro_webhooks.apps.core.helpers import create_response, rule_link
from rapidpro_webhooks.apps.places import places_bp
from rapidpro_webhooks.apps.places.views import NOMENKLATURA_API_KEY, NOMENKLATURA_URL, NOMINATUM_URL

EXCLUDE = {'DISTRICT', 'VDC', 'MUNICIPALITY', 'CITY', 'TOWN', 'GABISA', 'NAGARPALIKA', 'JILLA', 'HELLO', 'FROM', 'LIVE'}


@places_bp.route('/nominatum/reconcile', methods=['GET', 'POST'])
@limit(max_requests=10, period=60, by="ip")
def nominatum():
    """ Look up a given place name on OSM via
        http://wiki.openstreetmap.org/wiki/Nominatim

        Nominatim does not do any fuzzy matching, so
        not so helpful for user-provided spellings.
    """
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
    # discard tokens of one or two chars
    # TODO this isnt safe for Nepal VDCs bc of Ot
    query_words = [word.upper() for word in query.split() if len(word) > 2]
    cleaned = set(query_words).difference(EXCLUDE)
    return ' '.join(list(cleaned))


def ngrams(tokens, n=2):
    return zip(*[tokens[i:] for i in range(n)])


def _url_for_dataset(dataset):
    return NOMENKLATURA_URL + 'datasets/' + dataset + '/reconcile'


def _try_harder(data, query, n=2):
    tokens = query.split()
    if len(tokens) > n:
        ngram_matches = list()
        for ngram in ngrams(tokens, n):
            payload = {
                'format': 'json', 'api_key': NOMENKLATURA_API_KEY,
                'query': ' '.join(ngram)
            }
            result = requests.get(_url_for_dataset(data['dataset']), params=payload)
            results = result.json()

            for match in results['result']:
                if match['match'] is True:
                    ngram_matches.append(match)
                else:
                    if match['score'] >= 50:
                        ngram_matches.append(match)
        if len(ngram_matches) > 0:
            return ngram_matches
    return None


@places_bp.route('/nomenklatura/reconcile', methods=['GET', 'POST'])
@limit(max_requests=1000, period=60, by="ip")
def nomenklatura():
    # TODO better logging
    log = dict({'timestamp': datetime.datetime.utcnow().isoformat()})

    data = request.values

    if data:
        try:
            # `data` is likely werkzeug's ImmutableDict inside a
            # CombinedMultiDict so try to cast with `to_dict`
            log.update({'request_data': data.to_dict()})
        except AttributeError:
            # `data` can also be a vanilla dict
            log.update({'request_data': data})

        if 'query' not in data:
            raise exceptions.APIError(message='Missing field: query',
                                      field='query',
                                      resource=rule_link(request.url_rule))
        if 'dataset' not in data:
            raise exceptions.APIError(message='Missing field: dataset',
                                      field='dataset',
                                      resource=rule_link(request.url_rule))

        payload = {'format': 'json'}

        # titlecase the query for better chance of exact match
        query = data['query'].title()
        payload['query'] = query
        payload['api_key'] = NOMENKLATURA_API_KEY

        log.update({'nomenklatura_payload': payload})
        result = requests.get(_url_for_dataset(data['dataset']),
                              params=payload)
        try:
            results = result.json()
        except JSONDecodeError:
            results = []

        matches = list()
        if len(results) > 0:
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
            # attempt to match each token of query
            match = _try_harder(data, query, 1)
            if match is None:
                # attempt to match each bigram of query
                match = _try_harder(data, query, 2)
                if match is None:
                    return create_response({
                        'message': _localized_fail(data.get('lang', 'eng')) % _format_type(data['dataset']),
                        'match': None,
                        '_links': {'self': rule_link(request.url_rule)}
                    })
            if match is not None:
                # dataset_name = match[0]['type'][0]['name']
                return create_response({
                    'message': _localized_success(data.get('lang', 'eng')) % {
                        'loc_type': _format_type(data['dataset']),
                        'match': match[0]['name']
                    },
                    'match': match[0]['name'],
                    '_links': {'self': rule_link(request.url_rule)}
                })

        else:
            # dataset_name = matches[0]['type'][0]['name']
            return create_response({
                'message': _localized_success(data.get('lang', 'eng')) % {
                    'loc_type': _format_type(data['dataset']),
                    'match': matches[0]['name']
                },
                'match': matches[0]['name'],
                '_links': {'self': rule_link(request.url_rule)}
            })

    abort(400)
