from flask import render_template, redirect, url_for
from flask_login import current_user
from app.blueprints.ana_sayfa import ana_sayfa_bp
from app.blueprints.auth.forms import LoginForm
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
    """Ana sayfa - giriş yapmamış kullanıcıları login'e yönlendir, giriş yapmışları dashboard'a"""
    if not current_user.is_authenticated:
        # Giriş yapmamış kullanıcıları direkt login sayfasına yönlendir
        return redirect(url_for('auth.login'))
    
    # Giriş yapmış kullanıcıları dashboard'a yönlendir
    return redirect(url_for('ana_sayfa.dashboard'))


@ana_sayfa_bp.route('/dashboard')
@session_required
def dashboard(aktif_ogrenci_id):
    """Dashboard - Ana kontrol paneli"""
    from app.blueprints.ogrenci_yonetimi.models import Ogrenci
    from app.blueprints.ders_konu_yonetimi.models import Ders, Konu
    from app.blueprints.calisma_programi.models import DersIlerleme
    from app.blueprints.gorusme_defteri.models import GorusmeKaydi
    from app.blueprints.etkinlik_kayit.models import Etkinlik
    from sqlalchemy import and_, or_
    
    # Temel istatistikler
    ogrenci_sayisi = Ogrenci.query.count()
    ders_sayisi = Ders.query.count()
    konu_sayisi = Konu.query.count()
    
    # Ortalama ilerleme
    ortalama_ilerleme = 0
    ders_ilerlemeleri = DersIlerleme.query.all()
    if ders_ilerlemeleri:
        ortalama_ilerleme = sum(di.tamamlama_yuzdesi for di in ders_ilerlemeleri) / len(ders_ilerlemeleri)
    
    # Bugünün tarihi
    bugun = datetime.now().date()
    bu_hafta_basi = bugun - timedelta(days=bugun.weekday())
    bu_hafta_sonu = bu_hafta_basi + timedelta(days=6)
    
    # Yaklaşan görüşmeler (bu hafta)
    yaklasan_gorusmeler = GorusmeKaydi.query.filter(
        and_(
            GorusmeKaydi.tarih >= bu_hafta_basi,
            GorusmeKaydi.tarih <= bu_hafta_sonu
        )
    ).order_by(GorusmeKaydi.tarih.asc()).limit(5).all()
    
    # Bu hafta yapılacak etkinlikler
    bu_hafta_etkinlikler = Etkinlik.query.filter(
        and_(
            Etkinlik.etkinlik_tarihi >= bu_hafta_basi,
            Etkinlik.etkinlik_tarihi <= bu_hafta_sonu
        )
    ).order_by(Etkinlik.etkinlik_tarihi.asc()).limit(5).all()
    
    # Risk altındaki öğrenciler (düşük ilerleme oranına sahip)
    risk_altindaki_ogrenciler = []
    for ogrenci in Ogrenci.query.all():
        ogrenci_ilerlemeleri = DersIlerleme.query.filter_by(ogrenci_id=ogrenci.id).all()
        if ogrenci_ilerlemeleri:
            ortalama = sum(di.tamamlama_yuzdesi for di in ogrenci_ilerlemeleri) / len(ogrenci_ilerlemeleri)
            if ortalama < 50:  # %50'nin altındakiler risk altında
                risk_altindaki_ogrenciler.append({
                    'ogrenci': ogrenci,
                    'ilerleme': ortalama
                })
    
    # En son 5 öğrenci
    son_ogrenciler = Ogrenci.query.order_by(Ogrenci.id.desc()).limit(5).all()
    
    # Başarılı öğrenciler (yüksek ilerleme oranına sahip)
    basarili_ogrenciler = []
    for ogrenci in Ogrenci.query.all():
        ogrenci_ilerlemeleri = DersIlerleme.query.filter_by(ogrenci_id=ogrenci.id).all()
        if ogrenci_ilerlemeleri:
            ortalama = sum(di.tamamlama_yuzdesi for di in ogrenci_ilerlemeleri) / len(ogrenci_ilerlemeleri)
            if ortalama >= 80:  # %80'nin üstündekiler başarılı
                basarili_ogrenciler.append({
                    'ogrenci': ogrenci,
                    'ilerleme': ortalama
                })
    
    # Bu ay yapılan toplam görüşme sayısı
    bu_ay_basi = bugun.replace(day=1)
    bu_ay_gorusme_sayisi = GorusmeKaydi.query.filter(
        GorusmeKaydi.tarih >= bu_ay_basi
    ).count()
    
    # Bu ay yapılan toplam etkinlik sayısı
    bu_ay_etkinlik_sayisi = Etkinlik.query.filter(
        Etkinlik.etkinlik_tarihi >= bu_ay_basi
    ).count()
    
    # Okul bilgisi
    from app.blueprints.parametre_yonetimi.models import OkulBilgi
    okul_bilgisi = OkulBilgi.query.filter_by(aktif=True).first()
    
    return render_template('ana_sayfa/dashboard.html',
                          # Temel istatistikler
                          ogrenci_sayisi=ogrenci_sayisi,
                          ders_sayisi=ders_sayisi,
                          konu_sayisi=konu_sayisi,
                          ortalama_ilerleme=ortalama_ilerleme,
                          # Hatırlatıcılar ve aktiviteler
                          yaklasan_gorusmeler=yaklasan_gorusmeler,
                          bu_hafta_etkinlikler=bu_hafta_etkinlikler,
                          # Öğrenci durumları
                          risk_altindaki_ogrenciler=risk_altindaki_ogrenciler[:5],
                          basarili_ogrenciler=basarili_ogrenciler[:5],
                          son_ogrenciler=son_ogrenciler,
                          # Aylık aktivite istatistikleri
                          bu_ay_gorusme_sayisi=bu_ay_gorusme_sayisi,
                          bu_ay_etkinlik_sayisi=bu_ay_etkinlik_sayisi,
                          # Diğer
                          okul_bilgisi=okul_bilgisi,
                          hide_sidebar=True)
