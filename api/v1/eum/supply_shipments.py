import datetime

from ..api import api  # Circular, but safe

from flask import request
from flask import abort
from flask import g

from ..decorators import limit
from ..helpers import rule_link
from ..helpers import create_response


@api.route('/eum/shipments', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def expected_shipments_for_contact():
    data = request.json
    if data:
        phone = data.get('phone')
        if phone:
            shipments_doc = g.db.open_doc('shipments-%s' % phone)
            shipments = shipments_doc.get('shipments')
            if shipments:
                # TODO should not have to eval this!!
                shipments = eval(shipments)

                return create_response({'shipment': shipments.pop(),
                                        '_links': {'self': rule_link(request.url_rule)}})
    abort(400)


@api.route('/eum/shipment-received', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def shipment_received():
    data = request.json
    if data:
        phone = data.get('phone')
        values = data.get('values')
        if phone:
            shipments_doc = g.db.open_doc('shipments-%s' % phone)
            shipments_received = shipments_doc.get('shipments-received', [])
            if shipments_received:
                shipment_data = {}
                shipment_data.update({'commodity': values['commodity']})
                shipment_data.update({'amount': values['amount']})
                shipment_data.update({'date_reported': datetime.datetime.utcnow()})
                shipment_data.update({'date_received': values['date_received']})

                shipments_received.append(shipment_data)
                shipments_doc.update({'shipments-received': shipments_received})
                g.db.save_doc(shipments_doc)

                return create_response({'shipment': shipment_data,
                                        '_links': {'self': rule_link(request.url_rule)}})
    abort(400)


@api.route('/eum/update-shipment', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def update_shipment():
    data = request.json
    if data:
#       # TODO
        pass
