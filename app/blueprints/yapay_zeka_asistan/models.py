"""
Yapay Zeka Asistanı modülü için veritabanı modelleri.
Bu modül, yapay zeka modelleri, analizler ve öneriler için gerekli veritabanı modellerini içerir.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db

class YapayZekaModel(db.Model):
    """Yapay zeka modellerini temsil eden model sınıfı"""
    __tablename__ = 'yapay_zeka_modelleri'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    model_adi = db.Column(db.String(150), nullable=False)
    model_turu = db.Column(db.String(50), nullable=False)  # akademik_risk, davranis_risk, kariyer, vb.
    aciklama = db.Column(db.Text)
    model_dosya_yolu = db.Column(db.String(255))  # Disk üzerindeki model dosyasının yolu
    aktif = db.Column(db.Boolean, default=True)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    son_guncelleme = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Model başarı metrikleri
    egitim_dogrulugu = db.Column(db.Float, default=0.0)  # Accuracy on training data
    test_dogrulugu = db.Column(db.Float, default=0.0)    # Accuracy on test data
    
    # İlişkiler
    analizler = relationship("YapayZekaAnaliz", back_populates="model", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<YapayZekaModel {self.model_adi}>"

class YapayZekaAnaliz(db.Model):
    """Yapay zeka analiz sonuçlarını temsil eden model sınıfı"""
    __tablename__ = 'yapay_zeka_analizleri'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('yapay_zeka_modelleri.id'), nullable=False)
    analiz_adi = db.Column(db.String(150), nullable=False)
    analiz_turu = db.Column(db.String(50), nullable=False)
    aciklama = db.Column(db.Text)
    sonuclar = db.Column(db.Text)  # JSON formatında saklanacak sonuçlar
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    
    # İlişkiler
    model = relationship("YapayZekaModel", back_populates="analizler")
    ogrenci_analizleri = relationship("OgrenciAnaliz", back_populates="analiz", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<YapayZekaAnaliz {self.analiz_adi}>"

class OgrenciAnaliz(db.Model):
    """Öğrenciler için yapılan analizleri temsil eden model sınıfı"""
    __tablename__ = 'ogrenci_analizleri'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenciler.id'), nullable=False)
    analiz_id = db.Column(db.Integer, db.ForeignKey('yapay_zeka_analizleri.id'), nullable=False)
    analiz_tarihi = db.Column(db.DateTime, default=datetime.now)
    
    # Analiz sonuçları
    risk_seviyesi = db.Column(db.Float, default=0.0)  # 0-1 arası risk seviyesi
    yorumlar = db.Column(db.Text)
    # ham_sonuclar sütunu veritabanında yok, geçici olarak kaldırıldı
    # ham_sonuclar = db.Column(db.Text)  # JSON formatında saklanacak veriler
    
    # İlişkiler
    ogrenci = relationship("Ogrenci", backref="yapay_zeka_analizleri")
    analiz = relationship("YapayZekaAnaliz", back_populates="ogrenci_analizleri")
    oneriler = relationship("OgrenciOneri", back_populates="analiz", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<OgrenciAnaliz {self.id} - Öğrenci: {self.ogrenci_id}>"

class OgrenciOneri(db.Model):
    """Analiz sonucunda öğrenci için oluşturulan önerileri temsil eden model sınıfı"""
    __tablename__ = 'ogrenci_onerileri'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    analiz_id = db.Column(db.Integer, db.ForeignKey('ogrenci_analizleri.id'), nullable=False)
    oneri_metni = db.Column(db.Text, nullable=False)
    oneri_turu = db.Column(db.String(50), nullable=False)  # mudahale, kaynak, aktivite, vb.
    oncelik = db.Column(db.Integer, default=0)  # 0: Düşük, 1: Orta, 2: Yüksek
    
    # Uygulama durumu
    uygulamaya_alindi = db.Column(db.Boolean, default=False)
    uygulama_tarihi = db.Column(db.DateTime)
    uygulama_sonucu = db.Column(db.Text)
    
    # İlişkiler
    analiz = relationship("OgrenciAnaliz", back_populates="oneriler")
    
    def __repr__(self):
        return f"<OgrenciOneri {self.id}>"

class DuyguAnalizi(db.Model):
    """Öğrenciler için yapılan duygu analizini temsil eden model sınıfı"""
    __tablename__ = 'duygu_analizleri'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenciler.id'), nullable=False)
    metin = db.Column(db.Text, nullable=False)
    metin_kaynagi = db.Column(db.String(50))  # kompozisyon, anket_cevabi, refleksiyon, gorusme_notu, vb.
    analiz_tarihi = db.Column(db.DateTime, default=datetime.now)
    
    # Analiz sonuçları
    baskın_duygu = db.Column(db.String(50))  # olumlu, olumsuz, notr
    olumlu_skor = db.Column(db.Float, default=0.0)
    olumsuz_skor = db.Column(db.Float, default=0.0)
    notr_skor = db.Column(db.Float, default=0.0)
    sonuc_detay = db.Column(db.Text)  # JSON formatında saklanacak detaylı analiz sonuçları
    
    # İlişkiler
    ogrenci = relationship("Ogrenci", backref="duygu_analizleri")
    
    def __repr__(self):
        return f"<DuyguAnalizi {self.id} - Öğrenci: {self.ogrenci_id}>"