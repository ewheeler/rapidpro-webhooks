import datetime

from flask import abort, request

from api.v1.api import api  # Circular, but safe
from api.v1.decorators import limit
from api.v1.helpers import create_response, rule_link


@api.route('/ureport/birth-year', methods=['POST'])
@limit(max_requests=10, period=60, by="ip")
def categorize_birth_year():
    data = request.json
    if data:
        values = data.get('values')
        years = [value for value in values
                 if value.get('label') == 'born']
        if years:
            year = years[0]['value']
            try:
                year = int(year)
            except BaseException:
                year = int(year.split(' ')[0])
            age = datetime.datetime.utcnow().year - year
            if age <= 13:
                category = 'child'
            elif 14 < age < 18:
                category = 'youth'
            elif age >= 18:
                category = 'adult'
            else:
                abort(400)

            return create_response({'age': age,
                                    'age_category': category,
                                    '_links': {'self': rule_link(request.url_rule)}})
    abort(400)
