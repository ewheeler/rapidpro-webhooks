from flask import Blueprint, render_template


ui = Blueprint('ui', __name__)

@ui.route('/', methods=['GET'])
def index():
    return render_template('dashboard.html')