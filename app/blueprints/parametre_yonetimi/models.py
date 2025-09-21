"""
Sabitler modülü için veritabanı modelleri.
Bu modül, sistem genelinde kullanılan sabit verilerin saklanmasını sağlar.
"""

from datetime import datetime
from app.extensions import db
from sqlalchemy.orm import relationship

class OkulBilgi(db.Model):
    """Okul bilgilerini saklayan model"""
    __tablename__ = 'okul_bilgileri'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    okul_adi = db.Column(db.String(200), nullable=False)
    il = db.Column(db.String(50), nullable=False)
    ilce = db.Column(db.String(50), nullable=False)
    danisman_adi = db.Column(db.String(100), nullable=False)
    aktif = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"<OkulBilgi {self.okul_adi}>"

class DersSaati(db.Model):
    """Ders saatlerini (giriş-çıkış) saklayan model"""
    __tablename__ = 'ders_saatleri'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    ders_numarasi = db.Column(db.Integer, nullable=False)  # 1. ders, 2. ders vb.
    baslangic_saati = db.Column(db.Time, nullable=False)
    bitis_saati = db.Column(db.Time, nullable=False)
    ogle_arasi = db.Column(db.Boolean, default=False)  # Öğle arası olup olmadığı
    
    def __repr__(self):
        return f"<DersSaati {self.ders_numarasi}. Ders: {self.baslangic_saati.strftime('%H:%M')}-{self.bitis_saati.strftime('%H:%M')}>"

class OgleArasi(db.Model):
    """Öğle arası bilgilerini saklayan model"""
    __tablename__ = 'ogle_arasi'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    baslangic_saati = db.Column(db.Time, nullable=False)
    bitis_saati = db.Column(db.Time, nullable=False)
    aktif = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"<OgleArasi {self.baslangic_saati.strftime('%H:%M')}-{self.bitis_saati.strftime('%H:%M')}>"

class GorusmeKonusu(db.Model):
    """Danışman görüşmesi için konu başlıklarını saklayan model"""
    __tablename__ = 'gorusme_konulari'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(255), nullable=False, unique=True)
    
    def __repr__(self):
        return f"<GorusmeKonusu {self.baslik}>"