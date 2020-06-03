import datetime

from flask import abort, Blueprint, request

from rapidpro_webhooks.apps.core.decorators import limit
from rapidpro_webhooks.apps.core.helpers import create_response, rule_link

thousand_bp = Blueprint('thousand', __name__)


@thousand_bp.route('/', methods=['GET'])
def home():
    return create_response({'app': 'THOUSAND'})


@thousand_bp.route('/last-menses', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def calculate_last_menses():
    data = request.json
    if data:
        values = data.get('values')
        weeks = [value for value in values
                 if value.get('label') == 'weeks_since_last_menses']
        if weeks:
            weeks = weeks[0]['value']
            try:
                weeks = int(weeks)
            except BaseException:
                weeks = int(weeks.split(' ')[0])
            days_since_menses = weeks * 7
            last_menses_date = datetime.datetime.utcnow() - \
                datetime.timedelta(days=days_since_menses)
            expected_delivery_date = last_menses_date + \
                datetime.timedelta(days=280)
            return create_response({'days_since_menses': days_since_menses,
                                    'last_menses': last_menses_date,
                                    'expected_delivery_date': expected_delivery_date,
                                    '_links': {'self': rule_link(request.url_rule)}})
    abort(400)
