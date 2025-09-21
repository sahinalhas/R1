from flask import Blueprint

rapor_yonetimi_bp = Blueprint('rapor_yonetimi', __name__, template_folder='templates', url_prefix='/rapor-yonetimi')

from app.blueprints.rapor_yonetimi import routes, models