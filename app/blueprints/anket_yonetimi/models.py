"""
Anket Yönetimi modülü için veritabanı modelleri.
Bu modül, anket, anket soruları, cevap şablonları ve öğrenci cevapları için 
gerekli veritabanı modellerini içerir.
"""

from datetime import datetime
from app.extensions import db, relationship
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON

class AnketTuru(db.Model):
    """Anket türlerini tanımlayan model (psikolojik test, akademik anket, vb.)"""
    __tablename__ = 'anket_turleri'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tur_adi = db.Column(db.String(100), nullable=False, unique=True)
    aciklama = db.Column(db.Text, nullable=True)
    
    # İlişkiler
    anketler = relationship("Anket", back_populates="anket_turu")
    
    def __repr__(self):
        return f"<AnketTuru {self.tur_adi}>"

class CevapTuru(db.Model):
    """Cevap türlerini tanımlayan model (çoktan seçmeli, açık uçlu, ölçek, vb.)"""
    __tablename__ = 'cevap_turleri'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tur_adi = db.Column(db.String(50), nullable=False, unique=True)
    aciklama = db.Column(db.Text, nullable=True)
    
    # İlişkiler
    sorular = relationship("AnketSoru", back_populates="cevap_turu")
    
    def __repr__(self):
        return f"<CevapTuru {self.tur_adi}>"

class Anket(db.Model):
    """Anketleri tanımlayan ana model"""
    __tablename__ = 'anketler'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    anket_turu_id = db.Column(db.Integer, db.ForeignKey('anket_turleri.id'), nullable=False)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text, nullable=True)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    aktif = db.Column(db.Boolean, default=True)
    
    # İlişkiler
    anket_turu = relationship("AnketTuru", back_populates="anketler")
    sorular = relationship("AnketSoru", back_populates="anket", cascade="all, delete-orphan")
    ogrenci_anketleri = relationship("OgrenciAnket", back_populates="anket", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Anket {self.baslik}>"

class AnketSoru(db.Model):
    """Anket sorularını tanımlayan model"""
    __tablename__ = 'anket_sorulari'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    anket_id = db.Column(db.Integer, db.ForeignKey('anketler.id'), nullable=False)
    cevap_turu_id = db.Column(db.Integer, db.ForeignKey('cevap_turleri.id'), nullable=False)
    soru_metni = db.Column(db.Text, nullable=False)
    soru_sirasi = db.Column(db.Integer, nullable=False, default=1)
    cevap_secenekleri = db.Column(db.Text, nullable=True)  # JSON formatında saklanacak seçenekler (gerekirse)
    zorunlu = db.Column(db.Boolean, default=True)
    ters_puanlama = db.Column(db.Boolean, default=False)  # Psikolojik testler için ters puanlama
    
    # İlişkiler
    anket = relationship("Anket", back_populates="sorular")
    cevap_turu = relationship("CevapTuru", back_populates="sorular")
    cevaplar = relationship("AnketCevap", back_populates="soru", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AnketSoru {self.soru_metni[:30]}...>"
    
    @property
    def secenekler_listesi(self):
        """Cevap seçeneklerini liste olarak döndür (JSON formatından)"""
        import json
        if not self.cevap_secenekleri:
            return []
        try:
            return json.loads(self.cevap_secenekleri)
        except:
            return []

class OgrenciAnket(db.Model):
    """Öğrencilere atanan anketleri tanımlayan model"""
    __tablename__ = 'ogrenci_anketleri'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenciler.id'), nullable=False)
    anket_id = db.Column(db.Integer, db.ForeignKey('anketler.id'), nullable=False)
    atanma_tarihi = db.Column(db.DateTime, default=datetime.now)
    son_guncelleme = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    tamamlandi = db.Column(db.Boolean, default=False)
    tamamlanma_tarihi = db.Column(db.DateTime, nullable=True)
    
    # İlişkiler
    ogrenci = relationship("Ogrenci", back_populates="anketleri")
    anket = relationship("Anket", back_populates="ogrenci_anketleri")
    cevaplar = relationship("AnketCevap", back_populates="ogrenci_anket", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<OgrenciAnket {self.ogrenci_id}-{self.anket_id}>"

class AnketCevap(db.Model):
    """Öğrencilerin anket sorularına verdikleri cevapları tanımlayan model"""
    __tablename__ = 'anket_cevaplari'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    ogrenci_anket_id = db.Column(db.Integer, db.ForeignKey('ogrenci_anketleri.id'), nullable=False)
    soru_id = db.Column(db.Integer, db.ForeignKey('anket_sorulari.id'), nullable=False)
    cevap = db.Column(db.Text, nullable=True)  # Metin, sayı veya çoktan seçmeli değerler
    
    # İlişkiler
    ogrenci_anket = relationship("OgrenciAnket", back_populates="cevaplar")
    soru = relationship("AnketSoru", back_populates="cevaplar")
    
    def __repr__(self):
        return f"<AnketCevap {self.ogrenci_anket_id}-{self.soru_id}>"

class SinifAnketSonuc(db.Model):
    """Sınıf bazında toplu anket sonuçları için model (raporlama amaçlı)"""
    __tablename__ = 'sinif_anket_sonuclari'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    anket_id = db.Column(db.Integer, db.ForeignKey('anketler.id'), nullable=False)
    sinif = db.Column(db.String(20), nullable=False)  # "9A", "10B" gibi
    cevaplayan_sayisi = db.Column(db.Integer, default=0)
    sonuc_ozeti = db.Column(db.Text, nullable=True)  # JSON formatında özet bilgiler
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    
    # İlişkiler
    anket = relationship("Anket")
    
    def __repr__(self):
        return f"<SinifAnketSonuc {self.anket_id}-{self.sinif}>"