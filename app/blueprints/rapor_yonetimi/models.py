"""
Rapor Yönetimi modülü için veritabanı modelleri.
"""

from datetime import datetime
import json
from app.extensions import db
from sqlalchemy.orm import relationship

# SQLite ve PostgreSQL uyumluluğu için JSON alanı tanımları
# İki veritabanı sisteminde de metin olarak JSON saklayacağız
from sqlalchemy import Text

class FaaliyetRaporu(db.Model):
    """
    Rehberlik faaliyetlerinin dönemsel raporları
    MEB E-Rehberlik sistemi formatına uyumlu
    """
    __tablename__ = 'faaliyet_raporlari'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(200), nullable=False)
    donem = db.Column(db.String(50), nullable=False) # '2023-2024 Güz', '2023-2024 Bahar' gibi
    
    # Rapor tipi: 'dönemsel', 'yıllık', 'aylık', 'haftalık'
    rapor_tipi = db.Column(db.String(50), nullable=False, default='dönemsel')
    
    # Rapor durumu: 'taslak', 'tamamlandı', 'onaylandı', 'mebbis_aktarıldı'
    durum = db.Column(db.String(50), nullable=False, default='taslak')
    
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Raporu oluşturan kullanıcı bilgisi (ileride eklenebilir)
    # olusturan_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=True)
    
    # Rapor içeriği (JSON formatında)
    """
    rapor_verileri içeriği örneği:
    {
        "okul_bilgileri": {
            "okul_adi": "Örnek Anadolu Lisesi",
            "okul_turu": "Anadolu Lisesi",
            "il": "İstanbul",
            "ilce": "Kadıköy"
        },
        "rehberlik_kadrosu": {
            "rehber_ogretmen_sayisi": 2,
            "psikolojik_danismanlari": ["Ayşe Kaya", "Mehmet Yılmaz"]
        },
        "ozet_veriler": {
            "toplam_gorusme": 230,
            "bireysel_gorusme": 150,
            "grup_gorusmesi": 40,
            "veli_gorusmesi": 40
        },
        "aylik_istatistikler": [
            {"ay": "Eylül", "bireysel": 20, "grup": 5, "veli": 10},
            {"ay": "Ekim", "bireysel": 35, "grup": 8, "veli": 12}
        ],
        "sinif_dagilimi": [
            {"sinif": "9", "gorusme_sayisi": 50, "ogrenci_sayisi": 120},
            {"sinif": "10", "gorusme_sayisi": 45, "ogrenci_sayisi": 110}
        ],
        "calisma_alanlari": [
            {"alan": "Akademik Başarı", "gorusme_sayisi": 80},
            {"alan": "Kariyer Planlama", "gorusme_sayisi": 60}
        ]
    }
    """
    # Use Text column to store JSON data as string for PostgreSQL compatibility
    rapor_verileri = db.Column(db.Text, nullable=False, default='{}')
    
    @property
    def rapor_verileri_dict(self):
        """JSON'dan dict'e dönüştür"""
        return json.loads(self.rapor_verileri) if self.rapor_verileri else {}
        
    @rapor_verileri_dict.setter
    def rapor_verileri_dict(self, value):
        """Dict'i JSON'a dönüştür"""
        self.rapor_verileri = json.dumps(value) if value is not None else '{}'
    
    # Raporu oluşturan rehber öğretmen yorumu
    yorum = db.Column(db.Text, nullable=True)
    
    # MEBBİS entegrasyonu için ek bilgiler
    mebbis_aktarim_tarihi = db.Column(db.DateTime, nullable=True)
    mebbis_referans_no = db.Column(db.String(50), nullable=True)
    
    def __repr__(self):
        return f"<FaaliyetRaporu {self.baslik} - {self.donem}>"

class RaporSablonu(db.Model):
    """
    Özelleştirilebilir rapor şablonları
    Farklı rapor tiplerine göre önceden tanımlanmış şablonlar
    """
    __tablename__ = 'rapor_sablonlari'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(100), nullable=False)
    aciklama = db.Column(db.Text, nullable=True)
    
    # Şablon tipi: 'faaliyet', 'öğrenci_gelişim', 'sınıf_analiz', 'yönetim_özet', 'rehberlik_planı'
    sablon_tipi = db.Column(db.String(50), nullable=False)
    
    # Şablon yapısı (JSON formatında)
    """
    sablon_yapisi içeriği örneği:
    {
        "bölümler": [
            {
                "baslik": "Okul Bilgileri",
                "alanlar": ["okul_adi", "okul_turu", "il", "ilce"]
            },
            {
                "baslik": "Rehberlik Kadrosu",
                "alanlar": ["rehber_ogretmen_sayisi", "psikolojik_danismanlari"]
            }
        ],
        "grafikler": [
            {
                "ad": "Aylık Görüşme Sayıları",
                "tip": "bar",
                "veri_kaynagi": "aylik_istatistikler",
                "x_ekseni": "ay",
                "y_ekseni": ["bireysel", "grup", "veli"],
                "renkler": ["#4e73df", "#1cc88a", "#f6c23e"]
            }
        ]
    }
    """
    sablon_yapisi = db.Column(db.Text, nullable=False)
    
    @property
    def sablon_yapisi_dict(self):
        """JSON'dan dict'e dönüştür"""
        return json.loads(self.sablon_yapisi) if self.sablon_yapisi else {}
        
    @sablon_yapisi_dict.setter
    def sablon_yapisi_dict(self, value):
        """Dict'i JSON'a dönüştür"""
        self.sablon_yapisi = json.dumps(value) if value is not None else '{}'
    
    # Şablon HTML içeriği (Rapor şablonu HTML formatında)
    html_icerik = db.Column(db.Text, nullable=True)
    
    # MEB standartlarına uygunluk durumu
    meb_uyumlu = db.Column(db.Boolean, default=False)
    
    # Şablon oluşturma/güncelleme tarihleri
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<RaporSablonu {self.baslik} ({self.sablon_tipi})>"

class IstatistikRaporu(db.Model):
    """
    İstatistiksel veri analizi ve performans raporları için model
    """
    __tablename__ = 'istatistik_raporlari'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(200), nullable=False)
    
    # Rapor tipi: 'analiz', 'karşılaştırma', 'performans', 'yönetim_özeti'
    rapor_tipi = db.Column(db.String(50), nullable=False)
    
    # Tarih aralığı
    baslangic_tarihi = db.Column(db.Date, nullable=False)
    bitis_tarihi = db.Column(db.Date, nullable=False)
    
    # Filtreleme parametreleri (JSON formatında)
    filtreler = db.Column(db.Text, nullable=True)
    
    # Rapor içeriği (JSON formatında)
    rapor_verileri = db.Column(db.Text, nullable=False)
    
    # Rapor grafikleri (JSON formatında)
    grafikler = db.Column(db.Text, nullable=True)
    
    @property
    def filtreler_dict(self):
        """JSON'dan dict'e dönüştür"""
        return json.loads(self.filtreler) if self.filtreler else None
        
    @filtreler_dict.setter 
    def filtreler_dict(self, value):
        """Dict'i JSON'a dönüştür"""
        self.filtreler = json.dumps(value) if value is not None else None
        
    @property
    def rapor_verileri_dict(self):
        """JSON'dan dict'e dönüştür"""
        return json.loads(self.rapor_verileri) if self.rapor_verileri else {}
        
    @rapor_verileri_dict.setter
    def rapor_verileri_dict(self, value):
        """Dict'i JSON'a dönüştür"""
        self.rapor_verileri = json.dumps(value) if value is not None else '{}'
        
    @property
    def grafikler_dict(self):
        """JSON'dan dict'e dönüştür"""
        return json.loads(self.grafikler) if self.grafikler else None
        
    @grafikler_dict.setter
    def grafikler_dict(self, value):
        """Dict'i JSON'a dönüştür"""
        self.grafikler = json.dumps(value) if value is not None else None
    
    # Rapor oluşturma/güncelleme tarihleri
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Rapor yorumu
    yorum = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f"<IstatistikRaporu {self.baslik} ({self.rapor_tipi})>"

class RaporlananOlay(db.Model):
    """
    Önemli olaylar ve müdahaleler için raporlama modeli
    """
    __tablename__ = 'raporlanan_olaylar'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(200), nullable=False)
    
    # Olay tipi: 'kriz', 'disiplin', 'özel_durum', 'acil_müdahale'
    olay_tipi = db.Column(db.String(50), nullable=False)
    
    # Olay tarihi ve saati
    olay_tarihi = db.Column(db.DateTime, nullable=False)
    
    # İlgili öğrenciler (virgülle ayrılmış liste)
    ilgili_ogrenciler = db.Column(db.String(500), nullable=True)
    
    # İlgili personel (virgülle ayrılmış liste)
    ilgili_personel = db.Column(db.String(500), nullable=True)
    
    # Olay detayları
    olay_detaylari = db.Column(db.Text, nullable=False)
    
    # Yapılan müdahale ve işlemler
    yapilan_mudahale = db.Column(db.Text, nullable=True)
    
    # Sonuç ve takip bilgileri
    sonuc = db.Column(db.Text, nullable=True)
    
    # Olay durumu: 'devam_ediyor', 'tamamlandı', 'takipte'
    durum = db.Column(db.String(50), nullable=False, default='devam_ediyor')
    
    # Ekler ve referanslar (JSON formatında)
    ekler = db.Column(db.Text, nullable=True)
    
    @property
    def ekler_dict(self):
        """JSON'dan dict'e dönüştür"""
        return json.loads(self.ekler) if self.ekler else {}
        
    @ekler_dict.setter
    def ekler_dict(self, value):
        """Dict'i JSON'a dönüştür"""
        self.ekler = json.dumps(value) if value is not None else '{}'
    
    # Oluşturma/güncelleme tarihleri
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # MEBBİS raporlaması gerekli mi?
    mebbis_rapor_gerekli = db.Column(db.Boolean, default=False)
    mebbis_rapor_tarihi = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f"<RaporlananOlay {self.baslik} ({self.olay_tipi})>"