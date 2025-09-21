from datetime import datetime
from app.extensions import db
from sqlalchemy.orm import relationship

class DersProgrami(db.Model):
    __tablename__ = 'ders_programlari'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenciler.id'), nullable=False)
    ders_id = db.Column(db.Integer, db.ForeignKey('dersler.id'), nullable=False)
    gun = db.Column(db.Integer, nullable=False)  # 0: Pazartesi, 1: Salı, ..., 6: Pazar
    baslangic_saat = db.Column(db.Time, nullable=False)
    bitis_saat = db.Column(db.Time, nullable=False)
    
    # Relationships
    ogrenci = relationship("Ogrenci", back_populates="ders_programlari")
    ders = relationship("Ders", back_populates="ders_programlari")
    
    def __repr__(self):
        return f"<DersProgrami {self.ogrenci_id} - {self.ders_id} {self.gun_adi()} {self.baslangic_saat}-{self.bitis_saat}>"
    
    def gun_adi(self):
        """Gün index'ine göre gün adını döndür"""
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        return gunler[self.gun]
    
    def sure_dakika(self):
        """Ders süresini dakika olarak hesapla"""
        baslangic = datetime.combine(datetime.today(), self.baslangic_saat)
        bitis = datetime.combine(datetime.today(), self.bitis_saat)
        delta = bitis - baslangic
        return delta.seconds // 60

class DersIlerleme(db.Model):
    __tablename__ = 'ders_ilerlemeleri'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenciler.id'), nullable=False)
    ders_id = db.Column(db.Integer, db.ForeignKey('dersler.id'), nullable=False)
    tamamlama_yuzdesi = db.Column(db.Float, default=0)
    tahmini_bitis_tarihi = db.Column(db.Date, nullable=True)
    son_guncelleme = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    ogrenci = relationship("Ogrenci", back_populates="ders_ilerlemeleri")
    ders = relationship("Ders", back_populates="ders_ilerlemeleri")
    
    def __repr__(self):
        return f"<DersIlerleme {self.ogrenci_id} - {self.ders_id} %{self.tamamlama_yuzdesi:.1f}>"

class KonuTakip(db.Model):
    __tablename__ = 'konu_takipleri'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenciler.id'), nullable=False)
    konu_id = db.Column(db.Integer, db.ForeignKey('konular.id'), nullable=False)
    tamamlandi = db.Column(db.Boolean, default=False)
    calisilan_sure = db.Column(db.Integer, default=0)  # Dakika cinsinden
    cozulen_soru = db.Column(db.Integer, default=0)  # Çözülen soru sayısı
    dogru_soru = db.Column(db.Integer, default=0)   # Doğru çözülen soru sayısı
    son_calisma_tarihi = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    ogrenci = relationship("Ogrenci", back_populates="konu_takipleri")
    konu = relationship("Konu", back_populates="konu_takipleri")
    
    def __repr__(self):
        return f"<KonuTakip {self.ogrenci_id} - {self.konu_id} {'Tamamlandı' if self.tamamlandi else 'Devam ediyor'}>"
    
    def dogru_orani(self):
        """Çözülen sorular içinde doğru oranını hesapla"""
        if self.cozulen_soru == 0:
            return 0
        return (self.dogru_soru / self.cozulen_soru) * 100