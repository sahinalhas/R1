"""
Etkinlik Kayıt Modülü için veri modelleri.

Bu modül, rehberlik servisinin etkinliklerini kaydetmek için gerekli
veri modellerini içerir.
"""

from datetime import datetime
from app.extensions import db
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict
import json

class Etkinlik(db.Model):
    """
    Rehberlik servisinin yaptığı etkinlikleri kaydeden model.
    """
    __tablename__ = 'etkinlikler'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    etkinlik_tarihi = db.Column(db.Date, nullable=False)
    calisma_yontemi = db.Column(db.String(100), nullable=False)
    aciklama = db.Column(db.Text, nullable=False)
    hedef_turu = db.Column(db.String(100), nullable=False)
    faaliyet_turu = db.Column(db.String(100), nullable=False)
    
    # Katılımcı sayıları
    ogretmen_sayisi = db.Column(db.Integer, default=0)
    veli_sayisi = db.Column(db.Integer, default=0)
    diger_katilimci_sayisi = db.Column(db.Integer, default=0)
    
    # Öğrenci sayıları
    erkek_ogrenci_sayisi = db.Column(db.Integer, default=0)
    kiz_ogrenci_sayisi = db.Column(db.Integer, default=0)
    sinif_bilgisi = db.Column(db.String(200), nullable=True)
    
    # Etkinlik resmi yazı bilgisi
    resmi_yazi_sayisi = db.Column(db.String(50), nullable=True)
    
    # Etkinlik kaydıyla ilgili tarih bilgileri
    olusturulma_tarihi = db.Column(db.DateTime, default=datetime.now)
    guncelleme_tarihi = db.Column(db.DateTime, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Etkinlik {self.id}: {self.faaliyet_turu} - {self.etkinlik_tarihi}>"
    
    @property
    def toplam_ogrenci_sayisi(self):
        """Toplam öğrenci sayısını hesaplar"""
        return self.erkek_ogrenci_sayisi + self.kiz_ogrenci_sayisi
    
    @property
    def toplam_katilimci_sayisi(self):
        """Toplam katılımcı sayısını hesaplar (öğrenciler dahil)"""
        return (self.ogretmen_sayisi + self.veli_sayisi + 
                self.diger_katilimci_sayisi + self.toplam_ogrenci_sayisi)

# Etkinlik türleri (faaliyet türleri) için sabit tanımlar
ETKINLIK_TURLERI = [
    "Bireysel Görüşme", 
    "Grup Rehberliği", 
    "Psikoeğitim", 
    "Seminer", 
    "Veli Toplantısı", 
    "Atölye Çalışması",
    "Saha Çalışması",
    "Diğer"
]

# Hedef türleri için sabit tanımlar
HEDEF_TURLERI = [
    "Akademik Gelişim",
    "Kişisel/Sosyal Gelişim",
    "Mesleki Gelişim",
    "Psikolojik Destek",
    "Diğer"
]

# Çalışma yöntemleri için sabit tanımlar
CALISMA_YONTEMLERI = [
    "Bilgilendirme",
    "Grup Çalışması",
    "Bireysel Görüşme",
    "Sunum",
    "Atölye",
    "Uygulama",
    "Diğer"
]