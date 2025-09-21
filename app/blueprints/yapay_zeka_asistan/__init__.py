"""
Yapay Zeka Destekli Danışmanlık Asistanı blueprint'i.
Bu blueprint, rehberlik servisinin veri analizi ve karar alma süreçlerini yapay zeka teknolojileriyle 
destekleyerek daha etkili ve verimli danışmanlık hizmetleri sunmasını sağlar.
"""

from flask import Blueprint

yapay_zeka_asistan_bp = Blueprint(
    'yapay_zeka_asistan', 
    __name__,
    template_folder='templates'
)

from . import routes  # noqa: E402, F401