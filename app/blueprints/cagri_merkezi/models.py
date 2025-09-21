
"""
Çağrı Merkezi Modülü için veri modelleri.
Bu modül, rehberlik servisine yapılan başvuruları takip etmek için
gerekli veri modellerini içerir.
"""

from datetime import datetime
from app.extensions import db
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship

class CagriDurumu:
    YENI = "yeni"
    ACIK = "açık"
    BEKLEMEDE = "beklemede"
    COZULDU = "çözüldü"
    KAPATILDI = "kapatıldı"

class Cagri(db.Model):
    """Rehberlik servisine yapılan çağrıları temsil eden model"""
    __tablename__ = 'cagriler'
    
    id = Column(Integer, primary_key=True)
    baslik = Column(String(150), nullable=False)
    aciklama = Column(Text, nullable=True)
    olusturma_tarihi = Column(DateTime, default=datetime.now)
    son_guncelleme = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    durum = Column(String(20), default=CagriDurumu.YENI)
    
    # İlişkiler
    ogrenci_id = Column(Integer, ForeignKey('ogrenciler.id'), nullable=True)
    ogrenci = relationship("Ogrenci", backref="cagriler")
    atanan_kullanici_id = Column(Integer, nullable=True)  # İleride kullanıcı sistemi eklenirse
    
    # Takip yorumları
    yorumlar = relationship("CagriYorum", back_populates="cagri", cascade="all, delete-orphan")
    
    # Gerekirse priorite
    oncelik = Column(Integer, default=0)  # 0: Normal, 1: Yüksek, 2: Acil
    
    @property
    def oncelik_metni(self):
        if self.oncelik == 0:
            return "Normal"
        elif self.oncelik == 1:
            return "Yüksek"
        else:
            return "Acil"

class CagriYorum(db.Model):
    """Çağrı takip yorumları"""
    __tablename__ = 'cagri_yorumlari'
    
    id = Column(Integer, primary_key=True)
    icerik = Column(Text, nullable=False)
    tarih = Column(DateTime, default=datetime.now)
    
    # İlişkiler
    cagri_id = Column(Integer, ForeignKey('cagriler.id'), nullable=False)
    cagri = relationship("Cagri", back_populates="yorumlar")
    kullanici_id = Column(Integer, nullable=True)  # İleride kullanıcı sistemi eklenirse
