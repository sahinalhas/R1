"""
Etkinlik Kayıt Modülü için servis işlevleri.

Bu modül, etkinlik kayıtlarına ilişkin veri işlemleri ve 
iş mantığı operasyonlarını içerir.
"""

from datetime import datetime, date
from app.extensions import db
from app.blueprints.etkinlik_kayit.models import Etkinlik, ETKINLIK_TURLERI, HEDEF_TURLERI, CALISMA_YONTEMLERI

class EtkinlikService:
    """Etkinlik ile ilgili servis işlemleri"""
    
    @staticmethod
    def get_etkinlik_sayisi(baslangic_tarihi, bitis_tarihi):
        """
        Belirli bir tarih aralığındaki etkinlik sayısını getir
        
        Args:
            baslangic_tarihi: Başlangıç tarihi
            bitis_tarihi: Bitiş tarihi
            
        Returns:
            int: Etkinlik sayısı
        """
        return Etkinlik.query.filter(
            Etkinlik.etkinlik_tarihi >= baslangic_tarihi,
            Etkinlik.etkinlik_tarihi <= bitis_tarihi
        ).count()
    
    @staticmethod
    def get_yaklasan_etkinlikler(gun_sayisi=7):
        """
        Yaklaşan etkinlikleri getir
        
        Args:
            gun_sayisi: Kaç gün içindeki etkinlikleri getireceği
            
        Returns:
            List: Etkinlik listesi
        """
        bugun = date.today()
        from datetime import timedelta
        bitis_tarihi = bugun + timedelta(days=gun_sayisi)
        
        return Etkinlik.query.filter(
            Etkinlik.etkinlik_tarihi >= bugun,
            Etkinlik.etkinlik_tarihi <= bitis_tarihi
        ).order_by(Etkinlik.etkinlik_tarihi).all()
    
    @staticmethod
    def get_all_etkinlikler():
        """Tüm etkinlikleri tarih sırasına göre getirir"""
        return Etkinlik.query.order_by(Etkinlik.etkinlik_tarihi.desc()).all()
    
    @staticmethod
    def get_etkinlik_by_id(etkinlik_id):
        """ID'ye göre etkinliği getirir"""
        return Etkinlik.query.get(etkinlik_id)
    
    @staticmethod
    def create_etkinlik(form_data):
        """Yeni etkinlik kaydeder"""
        new_etkinlik = Etkinlik(
            etkinlik_tarihi=form_data['etkinlik_tarihi'],
            calisma_yontemi=form_data['calisma_yontemi'],
            aciklama=form_data['aciklama'],
            hedef_turu=form_data['hedef_turu'],
            faaliyet_turu=form_data['faaliyet_turu'],
            ogretmen_sayisi=form_data.get('ogretmen_sayisi', 0) or 0,
            veli_sayisi=form_data.get('veli_sayisi', 0) or 0,
            diger_katilimci_sayisi=form_data.get('diger_katilimci_sayisi', 0) or 0,
            erkek_ogrenci_sayisi=form_data.get('erkek_ogrenci_sayisi', 0) or 0,
            kiz_ogrenci_sayisi=form_data.get('kiz_ogrenci_sayisi', 0) or 0,
            sinif_bilgisi=form_data.get('sinif_bilgisi', ''),
            resmi_yazi_sayisi=form_data.get('resmi_yazi_sayisi', '')
        )
        
        db.session.add(new_etkinlik)
        db.session.commit()
        return new_etkinlik
    
    @staticmethod
    def update_etkinlik(etkinlik_id, form_data):
        """Etkinlik günceller"""
        etkinlik = Etkinlik.query.get(etkinlik_id)
        if not etkinlik:
            return None
        
        etkinlik.etkinlik_tarihi = form_data['etkinlik_tarihi']
        etkinlik.calisma_yontemi = form_data['calisma_yontemi']
        etkinlik.aciklama = form_data['aciklama']
        etkinlik.hedef_turu = form_data['hedef_turu']
        etkinlik.faaliyet_turu = form_data['faaliyet_turu']
        etkinlik.ogretmen_sayisi = form_data.get('ogretmen_sayisi', 0) or 0
        etkinlik.veli_sayisi = form_data.get('veli_sayisi', 0) or 0
        etkinlik.diger_katilimci_sayisi = form_data.get('diger_katilimci_sayisi', 0) or 0
        etkinlik.erkek_ogrenci_sayisi = form_data.get('erkek_ogrenci_sayisi', 0) or 0
        etkinlik.kiz_ogrenci_sayisi = form_data.get('kiz_ogrenci_sayisi', 0) or 0
        etkinlik.sinif_bilgisi = form_data.get('sinif_bilgisi', '')
        etkinlik.resmi_yazi_sayisi = form_data.get('resmi_yazi_sayisi', '')
        
        db.session.commit()
        return etkinlik
    
    @staticmethod
    def delete_etkinlik(etkinlik_id):
        """Etkinlik siler"""
        etkinlik = Etkinlik.query.get(etkinlik_id)
        if not etkinlik:
            return False
        
        db.session.delete(etkinlik)
        db.session.commit()
        return True
    
    @staticmethod
    def get_etkinlik_turleri():
        """Etkinlik türlerini döndürür"""
        return ETKINLIK_TURLERI
    
    @staticmethod
    def get_hedef_turleri():
        """Hedef türlerini döndürür"""
        return HEDEF_TURLERI
    
    @staticmethod
    def get_calisma_yontemleri():
        """Çalışma yöntemlerini döndürür"""
        return CALISMA_YONTEMLERI