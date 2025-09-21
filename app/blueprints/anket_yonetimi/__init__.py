"""
Anket Yönetimi blueprint'i.
Bu blueprint, anket oluşturma, düzenleme, öğrencilere atama ve cevapları toplu şekilde 
sisteme yükleme işlemlerini yönetir.
"""

from flask import Blueprint

anket_yonetimi_bp = Blueprint('anket_yonetimi', __name__, template_folder='templates')

# Blueprint routes will be imported in app/__init__.py to avoid circular imports