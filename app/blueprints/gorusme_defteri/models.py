"""
Görüşme Defteri için veri modelleri.
"""

from datetime import datetime
from app.extensions import db
from sqlalchemy.orm import relationship

class GorusmeKaydi(db.Model):
    """Rehberlik görüşme kayıtları."""
    __tablename__ = 'gorusme_kayitlari'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenciler.id'), nullable=True)
    
    # Görüşme bilgileri
    tarih = db.Column(db.Date, nullable=False, default=datetime.now().date)
    baslangic_saati = db.Column(db.Time, nullable=False)
    bitis_saati = db.Column(db.Time, nullable=False)
    gorusme_sayisi = db.Column(db.Integer, default=1)
    
    # Görüşülen kişi bilgileri
    gorusulen_kisi = db.Column(db.String(100), nullable=False)
    kisi_rolu = db.Column(db.String(50))
    yakinlik_derecesi = db.Column(db.String(50))
    
    # Görüşme içeriği
    gorusme_konusu = db.Column(db.String(200), nullable=False)
    calisma_alani = db.Column(db.String(100))
    calisma_kategorisi = db.Column(db.String(100))
    hizmet_turu = db.Column(db.String(100))
    kurum_isbirligi = db.Column(db.String(100))
    gorusme_yeri = db.Column(db.String(100))
    
    # Özel durumlar
    disiplin_gorusmesi = db.Column(db.Boolean, default=False)
    adli_sevk = db.Column(db.Boolean, default=False)
    calisma_yontemi = db.Column(db.String(100))
    
    # Özet ve notlar
    ozet = db.Column(db.Text)
    
    # MEBBİS aktarım durumu
    mebbis_aktarildi = db.Column(db.Boolean, default=False)
    mebbis_aktarim_tarihi = db.Column(db.DateTime)
    
    # İlişkiler - Öğrenci model ilişkisini burada tanımlayacağız
    
    def __repr__(self):
        return f"<GorusmeKaydi id={self.id} tarih={self.tarih} ogrenci_id={self.ogrenci_id}>"