from flask import render_template, redirect, url_for
from app.blueprints.ana_sayfa import ana_sayfa_bp
from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from app.blueprints.ders_konu_yonetimi.models import Ders, Konu
from app.blueprints.calisma_programi.models import DersIlerleme
from app.blueprints.parametre_yonetimi.models import OkulBilgi
from app.blueprints.ogrenci_yonetimi.services import OgrenciService
from app.blueprints.gorusme_defteri.services import GorusmeService
from app.blueprints.etkinlik_kayit.services import EtkinlikService
from app.blueprints.calisma_programi.services import CalismaService
from app.blueprints.rapor_yonetimi.services import RaporService
from app.utils.auth import session_required
from app.utils.session import get_aktif_ogrenci
from datetime import datetime, timedelta

# Basit ana sayfa fonksiyonu - ileride kullanılabilir
def simple_index():
    """Ana sayfa - basit özet bilgiler gösterilir"""
    ogrenci_sayisi = Ogrenci.query.count()
    ders_sayisi = Ders.query.count()
    konu_sayisi = Konu.query.count()
    
    # Son eklenen 5 öğrenci (ID'ye göre sıralama yapılır)
    son_ogrenciler = Ogrenci.query.order_by(Ogrenci.id.desc()).limit(5).all()
    
    # Ortalama ilerleme
    ortalama_ilerleme = 0
    ders_ilerlemeleri = DersIlerleme.query.all()
    if ders_ilerlemeleri:
        ortalama_ilerleme = sum(di.tamamlama_yuzdesi for di in ders_ilerlemeleri) / len(ders_ilerlemeleri)
    
    # Okul bilgisi
    okul_bilgisi = OkulBilgi.query.filter_by(aktif=True).first()
    
    return render_template('ana_sayfa/index.html', 
                          ogrenci_sayisi=ogrenci_sayisi, 
                          ders_sayisi=ders_sayisi,
                          konu_sayisi=konu_sayisi,
                          son_ogrenciler=son_ogrenciler,
                          ortalama_ilerleme=ortalama_ilerleme,
                          okul_bilgisi=okul_bilgisi)

@ana_sayfa_bp.route('/')
def index():
    """Ana sayfa - tüm modüller için giriş noktası"""
    # İstatistik değerleri doğrudan burada oluşturalım
    from app.blueprints.ogrenci_yonetimi.models import Ogrenci
    from app.blueprints.ders_konu_yonetimi.models import Ders, Konu
    from app.blueprints.calisma_programi.models import DersIlerleme
    
    ogrenci_sayisi = Ogrenci.query.count()
    ders_sayisi = Ders.query.count()
    konu_sayisi = Konu.query.count()
    
    # Ortalama ilerleme
    ortalama_ilerleme = 0
    ders_ilerlemeleri = DersIlerleme.query.all()
    if ders_ilerlemeleri:
        ortalama_ilerleme = sum(di.tamamlama_yuzdesi for di in ders_ilerlemeleri) / len(ders_ilerlemeleri)
    
    # Basit template render edelim
    return render_template('ana_sayfa/index.html',
                          ogrenci_sayisi=ogrenci_sayisi,
                          ders_sayisi=ders_sayisi,
                          konu_sayisi=konu_sayisi,
                          ortalama_ilerleme=ortalama_ilerleme)
