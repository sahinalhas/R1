"""
Etkinlik Kayıt Modülü blueprint'i.
Bu blueprint, rehberlik servisinin yaptığı etkinlikleri kaydetmek, 
listelemek ve raporlamak için kullanılır.
"""

from flask import Blueprint

etkinlik_kayit_bp = Blueprint('etkinlik_kayit', __name__, template_folder='templates')

# Blueprint routes are imported in app/__init__.py to avoid circular imports
# No need to import routes here