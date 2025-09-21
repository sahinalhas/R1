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


def get_aktif_ogrenci():
    """
    Aktif öğrenciyi döndür.
    
    Returns:
        Ogrenci: Aktif öğrenci nesnesi veya None
    """
    try:
        if 'aktif_ogrenci_id' in session:
            return Ogrenci.query.get(session['aktif_ogrenci_id'])
    except Exception:
        # Herhangi bir hata durumunda None döndür
        pass
    return None


# Aktif öğrenciyi temizleme fonksiyonu kaldırıldı