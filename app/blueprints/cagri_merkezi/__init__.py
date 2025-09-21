
from flask import Blueprint

cagri_merkezi_bp = Blueprint('cagri_merkezi', __name__, template_folder='templates')

from app.blueprints.cagri_merkezi import routes
