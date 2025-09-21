from flask import Blueprint

deneme_sinavlari_bp = Blueprint('deneme_sinavlari', __name__, template_folder='templates', url_prefix='/deneme-sinavlari')

from app.blueprints.deneme_sinavlari import routes