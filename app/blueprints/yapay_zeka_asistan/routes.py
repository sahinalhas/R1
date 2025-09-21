"""
Yapay Zeka Destekli Danışmanlık Asistanı blueprint'i için route tanımlamaları.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask import current_app as app

from app.utils.auth import session_required, ogrenci_required, admin_required
from app.blueprints.yapay_zeka_asistan import yapay_zeka_asistan_bp
from app.blueprints.yapay_zeka_asistan.services import YapayZekaService
from app.blueprints.ogrenci_yonetimi.services import OgrenciService

@yapay_zeka_asistan_bp.route('/')
@session_required
def index(ogrenci_id=None):
    """Yapay Zeka Asistanı ana sayfası"""
    modeller = YapayZekaService.get_modeller()
    return render_template('yapay_zeka_asistan/index.html', modeller=modeller)

@yapay_zeka_asistan_bp.route('/modeller')
@session_required
def modeller(ogrenci_id=None):
    """Yapay zeka modelleri listesi"""
    modeller = YapayZekaService.get_modeller()
    return render_template('yapay_zeka_asistan/modeller.html', modeller=modeller)

@yapay_zeka_asistan_bp.route('/model/<int:model_id>')
@session_required
def model_detay(model_id, ogrenci_id=None):
    """Model detay sayfası"""
    model = YapayZekaService.get_model(model_id)
    if not model:
        flash('Model bulunamadı.', 'danger')
        return redirect(url_for('yapay_zeka_asistan.modeller'))

    return render_template('yapay_zeka_asistan/model_detay.html', model=model)

@yapay_zeka_asistan_bp.route('/akademik-risk-modeli-olustur', methods=['GET', 'POST'])
@admin_required
def akademik_risk_modeli_olustur():
    """Akademik risk modeli oluşturma formu ve işlemi"""
    if request.method == 'POST':
        sinif = request.form.get('sinif')
        model_tipi = request.form.get('model_tipi', 'gelismis')

        # 'all' seçeneği için None değeri kullan
        if sinif == 'all':
            sinif = None

        sonuc = YapayZekaService.olustur_akademik_risk_modeli(sinif, model_tipi)

        if sonuc['success']:
            flash(sonuc['message'], 'success')
            return redirect(url_for('yapay_zeka_asistan.model_detay', model_id=sonuc['model_id']))
        else:
            flash(sonuc['message'], 'danger')

    return render_template('yapay_zeka_asistan/akademik_risk_modeli_olustur.html')

@yapay_zeka_asistan_bp.route('/ogrenci/<int:ogrenci_id>/analizler')
@ogrenci_required
def ogrenci_analizler(ogrenci_id, ogrenci=None):
    """Öğrenci analizleri sayfası"""
    # ogrenci parametresi ogrenci_required dekoratöründen gelir
    if not ogrenci:
        ogrenci = OgrenciService.get_ogrenci_by_id(ogrenci_id)
        if not ogrenci:
            flash('Öğrenci bulunamadı.', 'danger')
            return redirect(url_for('ogrenci_yonetimi.liste'))

    analizler = YapayZekaService.get_ogrenci_analiz_sonuclari(ogrenci_id)
    duygu_analizleri = YapayZekaService.get_duygu_analizleri(ogrenci_id)

    # Şablon için gerekli tüm URL'leri buradan gönderelim
    urls = {
        'ogrenci_profil': url_for('ogrenci_yonetimi.profil', ogrenci_id=ogrenci_id),
        'yeni_analiz': url_for('yapay_zeka_asistan.ogrenci_analiz_yap', ogrenci_id=ogrenci_id),
        'duygu_analizi': url_for('yapay_zeka_asistan.duygu_analizi_yap', ogrenci_id=ogrenci_id),
    }

    return render_template('yapay_zeka_asistan/ogrenci_analizler.html', 
                          ogrenci=ogrenci, 
                          analizler=analizler,
                          duygu_analizleri=duygu_analizleri,
                          urls=urls)

@yapay_zeka_asistan_bp.route('/ogrenci/<int:ogrenci_id>/analiz-yap', methods=['GET', 'POST'])
@ogrenci_required
def ogrenci_analiz_yap(ogrenci_id, ogrenci=None):
    """Öğrenci için yapay zeka analizi yapma"""
    # ogrenci parametresi ogrenci_required dekoratöründen gelir
    if not ogrenci:
        ogrenci = OgrenciService.get_ogrenci_by_id(ogrenci_id)
        if not ogrenci:
            flash('Öğrenci bulunamadı.', 'danger')
            return redirect(url_for('ogrenci_yonetimi.liste'))

    modeller = YapayZekaService.get_modeller(aktif_mi=True)

    if request.method == 'POST':
        model_id = request.form.get('model_id')

        sonuc = YapayZekaService.ogrenci_analiz_yap(ogrenci_id, model_id)

        if sonuc['success']:
            flash(sonuc['message'], 'success')
            return redirect(url_for('yapay_zeka_asistan.ogrenci_analizler', ogrenci_id=ogrenci_id))
        else:
            flash(sonuc['message'], 'danger')

    # Şablon için gerekli tüm URL'leri buradan gönderelim
    urls = {
        'ogrenci_profil': url_for('ogrenci_yonetimi.profil', ogrenci_id=ogrenci_id),
        'ogrenci_analizler': url_for('yapay_zeka_asistan.ogrenci_analizler', ogrenci_id=ogrenci_id),
    }

    return render_template('yapay_zeka_asistan/ogrenci_analiz_yap.html', 
                          ogrenci=ogrenci, 
                          modeller=modeller,
                          urls=urls)

@yapay_zeka_asistan_bp.route('/analiz/<int:analiz_id>/oneriler')
@session_required
def analiz_oneriler(analiz_id, ogrenci_id=None):
    """Analiz önerileri sayfası"""
    oneriler = YapayZekaService.get_analiz_onerileri(analiz_id)

    return render_template('yapay_zeka_asistan/analiz_oneriler.html', 
                          oneriler=oneriler,
                          analiz_id=analiz_id)

@yapay_zeka_asistan_bp.route('/oneri/<int:oneri_id>/guncelle', methods=['POST'])
@session_required
def oneri_guncelle(oneri_id, ogrenci_id=None):
    """Öneri uygulama durumunu güncelleme"""
    uygulamaya_alindi = request.form.get('uygulamaya_alindi') == 'true'
    uygulama_sonucu = request.form.get('uygulama_sonucu')

    sonuc = YapayZekaService.oneri_uygulama_durumu_guncelle(oneri_id, uygulamaya_alindi, uygulama_sonucu)

    return jsonify(sonuc)

@yapay_zeka_asistan_bp.route('/ogrenci/<int:ogrenci_id>/duygu-analizi', methods=['GET', 'POST'])
@ogrenci_required
def duygu_analizi_yap(ogrenci_id, ogrenci=None):
    """Öğrenci için duygu analizi yapma - Geliştirilmiş versiyon"""
    # ogrenci parametresi ogrenci_required dekoratöründen gelir
    if not ogrenci:
        ogrenci = OgrenciService.get_ogrenci_by_id(ogrenci_id)
        if not ogrenci:
            flash('Öğrenci bulunamadı.', 'danger')
            return redirect(url_for('ogrenci_yonetimi.liste'))

    if request.method == 'POST':
        metin = request.form.get('metin')
        metin_kaynagi = request.form.get('metin_kaynagi')
        analiz_tipi = request.form.get('analiz_tipi', 'gelismis')  # Varsayılan olarak gelişmiş analiz kullan

        if not metin or not metin_kaynagi:
            flash('Lütfen tüm alanları doldurun.', 'warning')
            return redirect(url_for('yapay_zeka_asistan.duygu_analizi_yap', ogrenci_id=ogrenci_id))

        sonuc = YapayZekaService.metin_duygu_analizi_yap(ogrenci_id, metin, metin_kaynagi, analiz_tipi)

        if sonuc['success']:
            flash(sonuc['message'], 'success')
            
            # Sonuç detay sayfasına yönlendir
            return redirect(url_for('yapay_zeka_asistan.duygu_analizi_sonuc', 
                                   ogrenci_id=ogrenci_id, 
                                   analiz_id=sonuc['analiz_id']))
        else:
            flash(sonuc['message'], 'danger')

    # Şablon için gerekli tüm URL'leri buradan gönderelim
    urls = {
        'ogrenci_profil': url_for('ogrenci_yonetimi.profil', ogrenci_id=ogrenci_id),
        'ogrenci_analizler': url_for('yapay_zeka_asistan.ogrenci_analizler', ogrenci_id=ogrenci_id),
    }

    return render_template('yapay_zeka_asistan/duygu_analizi_yap.html', 
                          ogrenci=ogrenci,
                          urls=urls)

@yapay_zeka_asistan_bp.route('/ogrenci/<int:ogrenci_id>/duygu-analizi/<int:analiz_id>')
@ogrenci_required
def duygu_analizi_sonuc(ogrenci_id, analiz_id, ogrenci=None):
    """Duygu analizi sonuçlarını görüntüleme sayfası"""
    import json
    # ogrenci parametresi ogrenci_required dekoratöründen gelir
    if not ogrenci:
        ogrenci = OgrenciService.get_ogrenci_by_id(ogrenci_id)
        if not ogrenci:
            flash('Öğrenci bulunamadı.', 'danger')
            return redirect(url_for('ogrenci_yonetimi.liste'))
    
    # Duygu analizi sonucunu getir
    duygu_analizi = YapayZekaService.get_duygu_analizi(analiz_id)
    if not duygu_analizi:
        flash('Duygu analizi bulunamadı.', 'danger')
        return redirect(url_for('yapay_zeka_asistan.ogrenci_analizler', ogrenci_id=ogrenci_id))
    
    # Analiz sonuçlarını hazırla
    analiz = {
        'id': duygu_analizi.id,
        'tarih': duygu_analizi.tarih,
        'metin': duygu_analizi.metin,
        'metin_kaynagi': duygu_analizi.metin_kaynagi.replace('_', ' ').capitalize(),
        'baskin_duygu': duygu_analizi.baskın_duygu,
        'olumlu_skor': duygu_analizi.olumlu_skor,
        'olumsuz_skor': duygu_analizi.olumsuz_skor,
        'notr_skor': duygu_analizi.notr_skor,
        'analiz_tipi': 'gelismis' # Varsayılan değer
    }
    
    # Baskın duyguya göre renk ve ikonlar ekle
    if analiz['baskin_duygu'] == 'olumlu':
        analiz['baskin_duygu_renk'] = 'success'
        analiz['baskin_duygu_ikon'] = 'smile'
    elif analiz['baskin_duygu'] == 'olumsuz':
        analiz['baskin_duygu_renk'] = 'danger'
        analiz['baskin_duygu_ikon'] = 'frown'
    else:
        analiz['baskin_duygu_renk'] = 'info'
        analiz['baskin_duygu_ikon'] = 'meh'
    
    # Gerekli tüm URL'leri hazırla
    urls = {
        'ogrenci_profil': url_for('ogrenci_yonetimi.profil', ogrenci_id=ogrenci_id),
        'ogrenci_analizler': url_for('yapay_zeka_asistan.ogrenci_analizler', ogrenci_id=ogrenci_id),
    }
    
    # Analiz ekstra özellikleri (varsa)
    try:
        # Sonuç detayları JSON içinde saklanıyor olabilir
        if hasattr(duygu_analizi, 'sonuc_detay') and duygu_analizi.sonuc_detay:
            detaylar = json.loads(duygu_analizi.sonuc_detay)
            
            # Önemli kelimeler
            if 'onemli_kelimeler' in detaylar:
                analiz['onemli_kelimeler'] = detaylar['onemli_kelimeler']
            
            # Analiz tipi
            if 'analiz_tipi' in detaylar:
                analiz['analiz_tipi'] = detaylar['analiz_tipi']
            
            # Duygu yogunluğu
            analiz['duygu_yogunlugu'] = max(analiz['olumlu_skor'], analiz['olumsuz_skor'])
            
            # Kapsamlı analiz için ek bilgiler
            if analiz['analiz_tipi'] == 'kapsamli':
                if 'duygu_kategorileri' in detaylar:
                    analiz['duygu_kategorileri'] = detaylar['duygu_kategorileri']
                if 'motivasyon_kaygi_dengesi' in detaylar:
                    analiz['motivasyon_kaygi_dengesi'] = detaylar['motivasyon_kaygi_dengesi']
                if 'cumle_analizleri' in detaylar:
                    # Cümle analizleri için renk ve ikon ekle
                    analiz['cumle_analizleri'] = []
                    for cumle in detaylar['cumle_analizleri']:
                        c = cumle.copy()
                        if c['duygu'] == 'olumlu':
                            c['duygu_renk'] = 'success'
                            c['duygu_ikon'] = 'smile'
                        elif c['duygu'] == 'olumsuz':
                            c['duygu_renk'] = 'danger'
                            c['duygu_ikon'] = 'frown'
                        else:
                            c['duygu_renk'] = 'info'
                            c['duygu_ikon'] = 'meh'
                        analiz['cumle_analizleri'].append(c)
    except:
        # JSON ayrıştırma hatası durumunda ek detayları ekleme
        pass
    
    return render_template('yapay_zeka_asistan/duygu_analizi_sonuc.html',
                          ogrenci=ogrenci,
                          analiz=analiz,
                          urls=urls)

@yapay_zeka_asistan_bp.route('/gelismis-veri-analizi')
@admin_required
def gelismis_veri_analizi():
    """Gelişmiş veri analizi sayfası"""
    # Sınıflar arası karşılaştırmalı analiz
    sinif_verileri = YapayZekaService.get_comparative_class_analysis()

    # Zaman serisi analizi
    zaman_serisi = YapayZekaService.get_time_series_analysis()

    # Tahminleme modelleri
    tahminler = YapayZekaService.get_predictive_models()

    return render_template('yapay_zeka_asistan/gelismis_veri_analizi.html', 
                          sinif_verileri=sinif_verileri,
                          zaman_serisi=zaman_serisi,
                          tahminler=tahminler)

@yapay_zeka_asistan_bp.route('/dashboard')
@admin_required
def dashboard():
    """Yapay zeka dashboard sayfası"""
    # Tüm öğrenciler için yapılan analizlerin özeti
    ogrenci_sayisi = OgrenciService.get_ogrenci_sayisi()
    analiz_sayisi = len(YapayZekaService.get_modeller())

    return render_template('yapay_zeka_asistan/dashboard.html', 
                          ogrenci_sayisi=ogrenci_sayisi,
                          analiz_sayisi=analiz_sayisi)