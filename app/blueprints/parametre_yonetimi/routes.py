
"""
Parametre Yönetimi blueprint'i için route tanımlamaları.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from app.blueprints.parametre_yonetimi import parametre_yonetimi_bp
from app.blueprints.parametre_yonetimi.services import SabitlerService
from app.utils.auth import admin_required

@parametre_yonetimi_bp.route('/')
@admin_required
def index():
    """Sabitler ana sayfası"""
    okul_bilgisi = SabitlerService.get_okul_bilgisi()
    ders_saatleri = SabitlerService.get_ders_saatleri()
    gorusme_konulari = SabitlerService.get_gorusme_konulari()
    ogle_arasi = SabitlerService.get_ogle_arasi()
    
    # Öğle arası varsayılan değerleri
    lunch_start = "12:00"
    lunch_end = "12:50"
    
    # Eğer öğle arası bilgisi varsa, değerleri al
    if ogle_arasi:
        lunch_start = ogle_arasi.baslangic_saati.strftime('%H:%M')
        lunch_end = ogle_arasi.bitis_saati.strftime('%H:%M')
    
    return render_template('parametre_yonetimi/index.html', 
                         okul_bilgisi=okul_bilgisi,
                         ders_saatleri=ders_saatleri,
                         gorusme_konulari=gorusme_konulari,
                         lunch_start=lunch_start,
                         lunch_end=lunch_end)

@parametre_yonetimi_bp.route('/okul-bilgileri', methods=['GET', 'POST'])
@admin_required
def okul_bilgileri():
    """Okul bilgileri formu ve işlemi"""
    try:
        if request.method == 'POST':
            okul_adi = request.form.get('okul_adi', '').strip()
            il = request.form.get('il', '').strip()
            ilce = request.form.get('ilce', '').strip()
            danisman_adi = request.form.get('danisman_adi', '').strip()
            
            if not all([okul_adi, il, ilce, danisman_adi]):
                flash('Tüm alanları doldurunuz!', 'danger')
                return redirect(url_for('parametre_yonetimi.okul_bilgileri'))
            
            sonuc = SabitlerService.kaydet_okul_bilgisi(okul_adi, il, ilce, danisman_adi)
            
            if sonuc['success']:
                flash(sonuc['message'], 'success')
                return redirect(url_for('parametre_yonetimi.index'))
            else:
                flash(sonuc['message'], 'danger')
        
        okul_bilgisi = SabitlerService.get_okul_bilgisi()
        return render_template('parametre_yonetimi/okul_bilgileri.html', okul_bilgisi=okul_bilgisi)
    
    except Exception as e:
        flash(f'Bir hata oluştu: {str(e)}', 'danger')
        return redirect(url_for('parametre_yonetimi.index'))

@parametre_yonetimi_bp.route('/ders-saatleri', methods=['GET', 'POST'])
@admin_required
def ders_saatleri():
    """Ders saatleri formu ve işlemi"""
    if request.method == 'POST':
        ders_saatleri_metin = request.form.get('ders_saatleri_metin', '').strip()
        lunch_start_time = request.form.get('lunch_start_time', '12:00')
        lunch_end_time = request.form.get('lunch_end_time', '12:50')
        
        # Artık ders_saatleri_metin boş olabilir - En az bir ders saati kontrolü JavaScript'te yapılıyor
        sonuc = SabitlerService.kaydet_ders_saatleri(ders_saatleri_metin, lunch_start_time, lunch_end_time)
        
        if sonuc['success']:
            flash(sonuc['message'], 'success')
            return redirect(url_for('parametre_yonetimi.index'))
        else:
            flash(sonuc['message'], 'danger')
    
    ders_saatleri = SabitlerService.get_ders_saatleri()
    
    # Ders saatlerini metin formatında hazırla
    ders_saatleri_metin = ""
    for ds in ders_saatleri:
        ders_saatleri_metin += f"{ds.ders_numarasi},{ds.baslangic_saati.strftime('%H:%M')},{ds.bitis_saati.strftime('%H:%M')},{1 if ds.ogle_arasi else 0}\n"
    
    return render_template('parametre_yonetimi/ders_saatleri.html', 
                         ders_saatleri=ders_saatleri,
                         ders_saatleri_metin=ders_saatleri_metin)

@parametre_yonetimi_bp.route('/gorusme-konulari', methods=['GET', 'POST'])
@admin_required
def gorusme_konulari():
    """Görüşme konuları formu ve işlemi"""
    if request.method == 'POST':
        konular_metni = request.form.get('konular_metni', '').strip()
        
        if not konular_metni:
            flash('Görüşme konuları giriniz!', 'danger')
            return redirect(url_for('parametre_yonetimi.gorusme_konulari'))
        
        sonuc = SabitlerService.kaydet_gorusme_konulari(konular_metni)
        
        if sonuc['success']:
            flash(sonuc['message'], 'success')
            return redirect(url_for('parametre_yonetimi.index'))
        else:
            flash(sonuc['message'], 'danger')
    
    gorusme_konulari = SabitlerService.get_gorusme_konulari()
    
    # Konuları metin formatında hazırla
    konular_metni = ""
    for konu in gorusme_konulari:
        konular_metni += f"{konu.baslik}\n"
    
    return render_template('parametre_yonetimi/gorusme_konulari.html', 
                         gorusme_konulari=gorusme_konulari,
                         konular_metni=konular_metni)

@parametre_yonetimi_bp.route('/gorusme-konulari/sil/<int:konu_id>', methods=['POST'])
@admin_required
def gorusme_konulari_sil(konu_id):
    """Görüşme konusu silme işlemi"""
    try:
        sonuc = SabitlerService.sil_gorusme_konusu(konu_id)
        
        if sonuc['success']:
            return jsonify({"success": True, "message": sonuc['message']})
        else:
            return jsonify({"success": False, "message": sonuc['message']})
    except Exception as e:
        return jsonify({"success": False, "message": f"Silme işlemi sırasında hata oluştu: {str(e)}"})
