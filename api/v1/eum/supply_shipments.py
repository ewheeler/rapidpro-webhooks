import datetime
import random
import json

from ..api import api  # Circular, but safe

from flask import request
from flask import abort
from flask import g
import couchdbkit

from ..decorators import limit
from ..helpers import rule_link
from ..helpers import create_response
from ..helpers import slugify


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
    shipment = {'amount': random.randrange(100, 20000),
                'commodity': random.choice(demo_commodities),
                'vendor': random.choice(demo_vendors),
                'expected': (datetime.datetime.utcnow().date() +
                             datetime.timedelta(days=random.randrange(3, 180)))
                             .isoformat()}
    return shipment


def _update_shipment_status(request, labels):
    if request.json is not None:
        data = request.json
    else:
        data = request.values
        data = {k: json.loads(v) for k, v in dict(request.values).iteritems()
                if k in ['values', 'steps']}
    if data:
        phone = _format_phone(data.get('phone'))

        values = data.get('values')

        if phone:
            shipments_doc = g.db.open_doc('shipments-%s' % phone)
            shipments_status = shipments_doc.get('shipments-status', [])
            shipment_data = {}
            for value in values:
                if value['label'].upper() in labels:
                    shipment_data.update({slugify(value['label']):
                                          value['value']})

            shipment_data.update({'rapidpro_data': data})

            shipments_status.append(shipment_data)
            shipments_doc.update({'shipments-status': shipments_status})
            g.db.save_doc(shipments_doc)
            return shipment_data


def get_or_create_shipments_doc(phone=None):
    assert phone is not None
    try:
        shipments_doc = g.db.open_doc('shipments-%s' % phone)
        shipments = shipments_doc.get('shipments', [])
        shipments_status = shipments_doc.get('shipments-status', [])
        # TODO actually check for an outstanding shipment
        if (shipments_status is None) or (len(shipments) == len(shipments_status)):
            shipments.append(_generate_shipment(phone))
            shipments_doc.update({'shipments': shipments})
            g.db.save_doc(shipments_doc)
    except couchdbkit.ResourceNotFound:
        shipments_doc = _generate_shipment()
    return shipments_doc


@api.route('/eum/shipments', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def expected_shipments_for_contact():
    if request.json is not None:
        data = request.json
    else:
        data = request.values

    if data:
        phone = _format_phone(data.get('phone'))
        if phone:
            shipments_doc = get_or_create_shipments_doc(phone)
            shipments_doc = g.db.open_doc('shipments-%s' % phone)
            shipments = shipments_doc.get('shipments')
            if shipments:
                return create_response({'shipment': shipments.pop(),
                                        '_links': {'self': rule_link(request.url_rule)}})
    abort(400)


SHIPMENT_RECEIVED_FIELDS = ['RECEIPT OF COMMODITY', 'DATE RECEIVED',
                            'AMOUNT RECEIVED', 'SHIPMENT CONDITION']


@api.route('/eum/shipment-received', methods=['POST'])
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


@api.route('/eum/update-shipment', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def update_shipment():
    """ Called when shipment status is updated by end user """
    shipment = _update_shipment_status(request, SHIPMENT_UPDATE_FIELDS)

    if shipment:
        return create_response({'shipment': shipment,
                                '_links': {'self':
                                           rule_link(request.url_rule)}})
    abort(400)
