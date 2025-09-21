from app.extensions import db
from sqlalchemy.orm import relationship

class Ders(db.Model):
    __tablename__ = 'dersler'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False, unique=True)
    aciklama = db.Column(db.Text, nullable=True)
    
    # Relationships
    konular = relationship("Konu", back_populates="ders", cascade="all, delete-orphan")
    ders_programlari = relationship("DersProgrami", back_populates="ders", cascade="all, delete-orphan")
    ders_ilerlemeleri = relationship("DersIlerleme", back_populates="ders", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ders {self.ad}>"
    
    def toplam_sure(self):
        """Dersin tüm konularının toplam tahmini süresini hesapla (dakika)"""
        # İlişki kurduğumuz için direkt konular ilişkisini kullanabiliriz
        return sum(konu.tahmini_sure for konu in self.konular)
    
    def konu_sayisi(self):
        """Dersin toplam konu sayısını döndür"""
        # İlişki kurduğumuz için direkt konular ilişkisini kullanabiliriz
        return len(self.konular)

class Konu(db.Model):
    __tablename__ = 'konular'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    ders_id = db.Column(db.Integer, db.ForeignKey('dersler.id'), nullable=False)
    ad = db.Column(db.String(200), nullable=False)
    tahmini_sure = db.Column(db.Integer, nullable=False)  # Dakika cinsinden
    sira = db.Column(db.Integer, nullable=False, default=0)
    
    # Relationships
    ders = relationship("Ders", back_populates="konular")
    konu_takipleri = relationship("KonuTakip", back_populates="konu", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Konu {self.ad}>"