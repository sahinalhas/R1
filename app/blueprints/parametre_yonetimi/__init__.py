"""
Parametre Yönetimi blueprint'i.
Bu blueprint, okul bilgileri, ders saatleri ve danışman görüşme konuları gibi
sistem çapında kullanılan sabit verileri yönetir.
"""

from flask import Blueprint

parametre_yonetimi_bp = Blueprint('parametre_yonetimi', __name__, template_folder='templates')