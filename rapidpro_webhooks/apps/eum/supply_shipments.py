import datetime
import json
import random

from flask import abort, Blueprint, g, request

from rapidpro_webhooks.apps.core.decorators import limit
from rapidpro_webhooks.apps.core.helpers import create_response, rule_link, slugify

eum_bp = Blueprint('eum', __name__)
demo_commodities = ['bednets', 'ors', 'plumpynut', 'textbooks']
demo_vendors = ['Acme', 'Parner Org.', 'Local NGO']


def _format_phone(phone):
    """ expects E164 msisdn, returns without leading + """
    assert phone is not None
    # TODO rapidpro will send E164, but this should ensure E164 so
    # other callers can be easily supported
    return phone


def _generate_shipment(phone=None):
    assert phone is not None
    shipment = {
        'amount': random.randrange(100, 20000),
        'commodity': random.choice(demo_commodities),
        'vendor': random.choice(demo_vendors),
        'expected': (datetime.datetime.utcnow().date() + datetime.timedelta(days=random.randrange(3, 180))).isoformat()
    }
    return shipment


def _update_shipment_status(request, labels):
    if request.json is not None:
        data = request.json
    else:
        data = request.values.to_dict()
        data.update({k: json.loads(v) for k, v in data.items()
                     if k in ['values', 'steps']})
    if data:
        phone = _format_phone(data.get('phone'))

        values = data.get('values')

        if phone:
            shipment_data = {}
            for value in values:
                if value['label'].upper() in labels:
                    shipment_data.update({slugify(value['label']):
                                          value['value']})

            shipment_data.update({'webhook_data': data})
            return shipment_data


@eum_bp.route('/shipments', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def expected_shipments_for_contact():
    if request.json is not None:
        data = request.json
    else:
        data = request.values

    if data:
        phone = _format_phone(data.get('phone'))
        if phone:
            return create_response({'shipment': data.pop(), '_links': {'self': rule_link(request.url_rule)}})
    abort(400)


SHIPMENT_RECEIVED_FIELDS = ['RECEIPT OF COMMODITY', 'DATE RECEIVED',
                            'AMOUNT RECEIVED', 'SHIPMENT CONDITION']


@eum_bp.route('/shipment-received', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def shipment_received():
    """ Called when shipment has been received by end user """
    shipment = _update_shipment_status(request, SHIPMENT_RECEIVED_FIELDS)
    if shipment:
        return create_response({'shipment': shipment,
                                '_links': {'self':
                                           rule_link(request.url_rule)}})
    abort(400)


SHIPMENT_UPDATE_FIELDS = ['RECEIPT OF COMMODITY', 'INFORMED OF DELAY',
                          'REVISED DATE ESTIMATE']


@eum_bp.route('/update-shipment', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def update_shipment():
    """ Called when shipment status is updated by end user """
    shipment = _update_shipment_status(request, SHIPMENT_UPDATE_FIELDS)

    # TODO if we have a revised date estimate,
    # then schedule flow for after revised date

    if shipment:
        return create_response({'shipment': shipment,
                                '_links': {'self':
                                           rule_link(request.url_rule)}})
    abort(400)


@eum_bp.route('/', methods=['GET'])
def home():
    return create_response({'app': 'Supply Shipments'})
