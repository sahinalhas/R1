from app.extensions import db
from sqlalchemy.orm import relationship

class DenemeSonuc(db.Model):
    __tablename__ = 'deneme_sonuclari'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenciler.id'), nullable=False)
    deneme_adi = db.Column(db.String(100), nullable=False)
    tarih = db.Column(db.Date, nullable=False)
    net_tyt_turkce = db.Column(db.Float, default=0)
    net_tyt_sosyal = db.Column(db.Float, default=0)
    net_tyt_matematik = db.Column(db.Float, default=0)
    net_tyt_fen = db.Column(db.Float, default=0)
    net_ayt_matematik = db.Column(db.Float, default=0)
    net_ayt_fizik = db.Column(db.Float, default=0)
    net_ayt_kimya = db.Column(db.Float, default=0)
    net_ayt_biyoloji = db.Column(db.Float, default=0)
    net_ayt_edebiyat = db.Column(db.Float, default=0)
    net_ayt_tarih = db.Column(db.Float, default=0)
    net_ayt_cografya = db.Column(db.Float, default=0)
    net_ayt_felsefe = db.Column(db.Float, default=0)
    puan_tyt = db.Column(db.Float, default=0)
    puan_say = db.Column(db.Float, default=0)
    puan_ea = db.Column(db.Float, default=0)
    puan_soz = db.Column(db.Float, default=0)
    
    # Relationships - Öğrenci ile ilişki kuruyoruz
    ogrenci = relationship("Ogrenci", back_populates="deneme_sonuclari")
    
    def __repr__(self):
        return f"<DenemeSonuc {self.ogrenci_id} - {self.deneme_adi} {self.tarih}>"
    
    def tyt_toplam_net(self):
        """TYT toplam netini hesapla"""
        return self.net_tyt_turkce + self.net_tyt_sosyal + self.net_tyt_matematik + self.net_tyt_fen
    
    def ayt_toplam_net(self):
        """AYT toplam netini hesapla"""
        return (self.net_ayt_matematik + self.net_ayt_fizik + self.net_ayt_kimya + self.net_ayt_biyoloji +
                self.net_ayt_edebiyat + self.net_ayt_tarih + self.net_ayt_cografya + self.net_ayt_felsefe)