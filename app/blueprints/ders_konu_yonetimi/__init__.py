from flask import Blueprint

ders_konu_yonetimi_bp = Blueprint('ders_konu_yonetimi', __name__, template_folder='templates')

from app.blueprints.ders_konu_yonetimi import routes