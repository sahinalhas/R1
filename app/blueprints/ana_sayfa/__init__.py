from flask import Blueprint

ana_sayfa_bp = Blueprint('ana_sayfa', __name__, template_folder='templates')

from app.blueprints.ana_sayfa import routes