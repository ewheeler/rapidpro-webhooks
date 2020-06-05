from flask import Blueprint, current_app

places_bp = Blueprint('places', __name__)
NOMENKLATURA_URL = "http://nomenklatura.uniceflabs.org/api/2/"
NOMENKLATURA_API_KEY = current_app.config['NOMENKLATURA_API_KEY']
NOMENKLATURA_HEADERS = {"Authorization": NOMENKLATURA_API_KEY}

NOMINATUM_URL = "http://nominatim.openstreetmap.org/search"
