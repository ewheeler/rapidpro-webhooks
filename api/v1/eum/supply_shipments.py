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
from ..helpers import only_digits


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
                datetime.timedelta(days=random.randrange(3, 180))).isoformat()}
    return shipment


def get_or_create_shipments_doc(phone=None):
    assert phone is not None
    try:
        shipments_doc = g.db.open_doc('shipments-%s' % phone)
        shipments = shipments_doc.get('shipments', [])
        shipments_received = shipments_doc.get('shipments-received', [])
        # TODO actually check for an outstanding shipment
        if len(shipments) == len(shipments_received):
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


@api.route('/eum/shipment-received', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def shipment_received():
    if request.json is not None:
        data = request.json
    else:
        data = request.values

    if data:
        phone = _format_phone(data.get('phone'))
        values_str = data.get('values')
        values = json.loads(values_str)
        if phone:
            shipments_doc = g.db.open_doc('shipments-%s' % phone)
            shipments_received = shipments_doc.get('shipments-received', [])
            shipment_data = {}
            for value in values:
                if value['label'] == 'Receipt of commodity':
                    shipment_data.update({'received': value['value']})
                if value['label'] == 'Date received':
                    shipment_data.update({'date_received': value['value']})
                if value['label'] == 'Amount received':
                    shipment_data.update({'amount': value['value']})
                if value['label'] == 'Shipment Condition':
                    shipment_data.update({'condition': value['value']})

            shipments_received.append(shipment_data)
            shipments_doc.update({'shipments-received': shipments_received})
            g.db.save_doc(shipments_doc)

            return create_response({'shipment': shipment_data,
                                    '_links': {'self': rule_link(request.url_rule)}})
    abort(400)


@api.route('/eum/update-shipment', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def update_shipment():
    if request.json is not None:
        data = request.json
    else:
        data = request.values
    if data:
        # TODO
        pass
