"""
Görüşme Defteri blueprint'i.
Bu blueprint, öğrenci ve veli görüşmelerinin kaydedilmesi, listelenmesi ve
MEBBİS sistemine aktarılması işlemlerini yönetir.
"""

from flask import Blueprint

gorusme_defteri_bp = Blueprint('gorusme_defteri', __name__, template_folder='templates')

from app.blueprints.gorusme_defteri import routes