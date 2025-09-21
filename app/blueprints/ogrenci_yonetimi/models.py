from datetime import datetime
from app.extensions import db
from sqlalchemy.orm import relationship

class Ogrenci(db.Model):
    __tablename__ = 'ogrenciler'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    numara = db.Column(db.String(20), unique=True, nullable=False)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    sinif = db.Column(db.String(20), nullable=False)
    cinsiyet = db.Column(db.String(10), nullable=False)
    telefon = db.Column(db.String(20), nullable=True)
    eposta = db.Column(db.String(100), nullable=True)
    
    # Relationships - öğrencinin ilişkili kayıtlarını tanımlıyoruz
    ders_programlari = relationship("DersProgrami", back_populates="ogrenci", cascade="all, delete-orphan")
    ders_ilerlemeleri = relationship("DersIlerleme", back_populates="ogrenci", cascade="all, delete-orphan")
    konu_takipleri = relationship("KonuTakip", back_populates="ogrenci", cascade="all, delete-orphan")
    deneme_sonuclari = relationship("DenemeSonuc", back_populates="ogrenci", cascade="all, delete-orphan")
    anketleri = relationship("OgrenciAnket", back_populates="ogrenci", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ogrenci {self.numara} - {self.ad} {self.soyad}>"
    
    @property
    def tam_ad(self):
        return f"{self.ad} {self.soyad}"
    
    def ders_tamamlama_yuzdesi(self, ders_id):
        """Belirli bir dersin tamamlanma yüzdesini hesapla"""
        # İlişki tanımladığımız için direkt self.ders_ilerlemeleri üzerinden filtreleyebiliriz
        ilerleme = next((di for di in self.ders_ilerlemeleri if di.ders_id == ders_id), None)
        if ilerleme:
            return ilerleme.tamamlama_yuzdesi
        return 0
    
    def genel_ilerleme(self):
        """Tüm dersler üzerinden genel ilerleme yüzdesini hesapla"""
        # İlişki tanımladığımız için direkt self.ders_ilerlemeleri kullanabiliriz
        if not self.ders_ilerlemeleri:
            return 0
        
        return sum(di.tamamlama_yuzdesi for di in self.ders_ilerlemeleri) / len(self.ders_ilerlemeleri)
        
# GorusmeKaydi ilişkisini Ogrenci sınıfının sonunda tanımla - döngüsel import problemini önlemek için
from app.blueprints.gorusme_defteri.models import GorusmeKaydi
Ogrenci.gorusme_kayitlari = relationship("GorusmeKaydi", back_populates="ogrenci", cascade="all, delete-orphan")
GorusmeKaydi.ogrenci = relationship("Ogrenci", back_populates="gorusme_kayitlari")