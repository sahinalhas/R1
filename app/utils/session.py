"""Oturum (session) ile ilgili yardımcı fonksiyonlar."""

from flask import session
from app.blueprints.ogrenci_yonetimi.models import Ogrenci

def set_aktif_ogrenci(ogrenci_id):
    """
    Aktif öğrenciyi oturumda (session) ayarla.
    
    Args:
        ogrenci_id: Aktif olarak ayarlanacak öğrencinin ID'si
    """
    session['aktif_ogrenci_id'] = ogrenci_id




# Aktif öğrenciyi temizleme fonksiyonu kaldırıldı