"""
Anket Yönetimi blueprint'i için route tanımlamaları.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from app.blueprints.anket_yonetimi import anket_yonetimi_bp
from app.blueprints.anket_yonetimi.services import AnketService
from app.blueprints.anket_yonetimi.models import Anket, AnketSoru, AnketTuru, CevapTuru
from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from app.utils.auth import admin_required
import json
import io
import csv

@anket_yonetimi_bp.route('/')
@admin_required
def index():
    """Anket Yönetimi ana sayfası"""
    anketler = AnketService.get_anketler()
    return render_template('anket_yonetimi/index.html', anketler=anketler)

@anket_yonetimi_bp.route('/anket-turleri', methods=['GET', 'POST'])
@admin_required
def anket_turleri():
    """Anket türleri listesi ve yeni tür ekleme"""
    if request.method == 'POST':
        tur_adi = request.form.get('tur_adi', '').strip()
        aciklama = request.form.get('aciklama', '').strip()
        
        if not tur_adi:
            flash('Tür adı zorunludur!', 'danger')
            return redirect(url_for('anket_yonetimi.anket_turleri'))
        
        sonuc = AnketService.kaydet_anket_turu(tur_adi, aciklama)
        
        if sonuc['success']:
            flash(sonuc['message'], 'success')
        else:
            flash(sonuc['message'], 'danger')
            
        return redirect(url_for('anket_yonetimi.anket_turleri'))
    
    anket_turleri = AnketService.get_anket_turleri()
    return render_template('anket_yonetimi/anket_turleri.html', anket_turleri=anket_turleri)

@anket_yonetimi_bp.route('/cevap-turleri', methods=['GET', 'POST'])
@admin_required
def cevap_turleri():
    """Cevap türleri listesi ve yeni tür ekleme"""
    if request.method == 'POST':
        tur_adi = request.form.get('tur_adi', '').strip()
        aciklama = request.form.get('aciklama', '').strip()
        
        if not tur_adi:
            flash('Tür adı zorunludur!', 'danger')
            return redirect(url_for('anket_yonetimi.cevap_turleri'))
        
        sonuc = AnketService.kaydet_cevap_turu(tur_adi, aciklama)
        
        if sonuc['success']:
            flash(sonuc['message'], 'success')
        else:
            flash(sonuc['message'], 'danger')
            
        return redirect(url_for('anket_yonetimi.cevap_turleri'))
    
    cevap_turleri = AnketService.get_cevap_turleri()
    return render_template('anket_yonetimi/cevap_turleri.html', cevap_turleri=cevap_turleri)

@anket_yonetimi_bp.route('/yeni-anket', methods=['GET', 'POST'])
@admin_required
def yeni_anket():
    """Yeni anket oluşturma formu ve işlemi"""
    if request.method == 'POST':
        baslik = request.form.get('baslik', '').strip()
        anket_turu_id = request.form.get('anket_turu_id')
        aciklama = request.form.get('aciklama', '').strip()
        
        if not baslik or not anket_turu_id:
            flash('Başlık ve anket türü zorunludur!', 'danger')
            return redirect(url_for('anket_yonetimi.yeni_anket'))
        
        sonuc = AnketService.kaydet_anket(baslik, anket_turu_id, aciklama)
        
        if sonuc['success']:
            flash(sonuc['message'], 'success')
            # Yeni oluşturulan anketin düzenleme sayfasına yönlendir
            return redirect(url_for('anket_yonetimi.duzenle_anket', anket_id=sonuc['id']))
        else:
            flash(sonuc['message'], 'danger')
            return redirect(url_for('anket_yonetimi.yeni_anket'))
    
    anket_turleri = AnketService.get_anket_turleri()
    return render_template('anket_yonetimi/yeni_anket.html', anket_turleri=anket_turleri)

@anket_yonetimi_bp.route('/anket/<int:anket_id>', methods=['GET'])
@admin_required
def anket_detay(anket_id):
    """Anket detayları sayfası"""
    anket = AnketService.get_anket(anket_id)
    
    if not anket:
        flash('Anket bulunamadı!', 'danger')
        return redirect(url_for('anket_yonetimi.index'))
    
    # Anket sorularını sıralı şekilde al
    sorular = AnketSoru.query.filter_by(anket_id=anket_id).order_by(AnketSoru.soru_sirasi).all()
    
    return render_template('anket_yonetimi/anket_detay.html', anket=anket, sorular=sorular)

@anket_yonetimi_bp.route('/anket/<int:anket_id>/duzenle', methods=['GET', 'POST'])
@admin_required
def duzenle_anket(anket_id):
    """Anket düzenleme formu ve işlemi"""
    anket = AnketService.get_anket(anket_id)
    
    if not anket:
        flash('Anket bulunamadı!', 'danger')
        return redirect(url_for('anket_yonetimi.index'))
    
    if request.method == 'POST':
        baslik = request.form.get('baslik', '').strip()
        anket_turu_id = request.form.get('anket_turu_id')
        aciklama = request.form.get('aciklama', '').strip()
        
        if not baslik or not anket_turu_id:
            flash('Başlık ve anket türü zorunludur!', 'danger')
            return redirect(url_for('anket_yonetimi.duzenle_anket', anket_id=anket_id))
        
        sonuc = AnketService.kaydet_anket(baslik, anket_turu_id, aciklama, anket_id)
        
        if sonuc['success']:
            flash(sonuc['message'], 'success')
        else:
            flash(sonuc['message'], 'danger')
            
        return redirect(url_for('anket_yonetimi.duzenle_anket', anket_id=anket_id))
    
    anket_turleri = AnketService.get_anket_turleri()
    # Anket sorularını sıralı şekilde al
    sorular = AnketSoru.query.filter_by(anket_id=anket_id).order_by(AnketSoru.soru_sirasi).all()
    cevap_turleri = AnketService.get_cevap_turleri()
    
    return render_template('anket_yonetimi/duzenle_anket.html', 
                         anket=anket, 
                         anket_turleri=anket_turleri,
                         sorular=sorular,
                         cevap_turleri=cevap_turleri)

@anket_yonetimi_bp.route('/anket/<int:anket_id>/soru-ekle', methods=['POST'])
@admin_required
def soru_ekle(anket_id):
    """Ankete yeni soru ekleme"""
    anket = AnketService.get_anket(anket_id)
    
    if not anket:
        return jsonify({"success": False, "message": "Anket bulunamadı!"})
    
    soru_metni = request.form.get('soru_metni', '').strip()
    cevap_turu_id = request.form.get('cevap_turu_id')
    soru_sirasi = request.form.get('soru_sirasi')
    cevap_secenekleri = request.form.get('cevap_secenekleri', '').strip()
    zorunlu = request.form.get('zorunlu') == 'on'
    ters_puanlama = request.form.get('ters_puanlama') == 'on'
    
    if not soru_metni or not cevap_turu_id:
        return jsonify({"success": False, "message": "Soru metni ve cevap türü zorunludur!"})
    
    # Sıra numarası belirtilmişse kullan
    if soru_sirasi:
        try:
            soru_sirasi = int(soru_sirasi)
        except:
            soru_sirasi = None
    else:
        soru_sirasi = None
    
    sonuc = AnketService.kaydet_anket_soru(
        anket_id, soru_metni, cevap_turu_id, 
        soru_sirasi, cevap_secenekleri, 
        zorunlu, ters_puanlama
    )
    
    return jsonify(sonuc)

@anket_yonetimi_bp.route('/anket/<int:anket_id>/toplu-soru-ekle', methods=['POST'])
@admin_required
def toplu_soru_ekle(anket_id):
    """Ankete toplu şekilde soru ekleme"""
    anket = AnketService.get_anket(anket_id)
    
    if not anket:
        return jsonify({"success": False, "message": "Anket bulunamadı!"})
    
    data = request.json
    
    if not data:
        return jsonify({"success": False, "message": "Geçersiz veri formatı!"})
    
    cevap_turu_id = data.get('cevap_turu_id')
    cevap_secenekleri = data.get('cevap_secenekleri', '')
    zorunlu = data.get('zorunlu', True)
    ters_puanlama = data.get('ters_puanlama', False)
    sorular = data.get('sorular', [])
    
    if not cevap_turu_id:
        return jsonify({"success": False, "message": "Cevap türü zorunludur!"})
    
    if not sorular or len(sorular) == 0:
        return jsonify({"success": False, "message": "En az bir soru girmelisiniz!"})
    
    # Son soru sırasını bul
    son_soru = AnketSoru.query.filter_by(anket_id=anket_id).order_by(AnketSoru.soru_sirasi.desc()).first()
    baslangic_sirasi = 1 if not son_soru else son_soru.soru_sirasi + 1
    
    basarili_sayisi = 0
    hatalar = []
    
    # Her bir soru için kayıt işlemi yap
    for i, soru_metni in enumerate(sorular):
        if not soru_metni.strip():
            continue  # Boş satırları atla
            
        sonuc = AnketService.kaydet_anket_soru(
            anket_id, soru_metni.strip(), cevap_turu_id, 
            baslangic_sirasi + i, cevap_secenekleri, 
            zorunlu, ters_puanlama
        )
        
        if sonuc['success']:
            basarili_sayisi += 1
        else:
            hatalar.append(f"Soru {i+1}: {sonuc['message']}")
    
    if basarili_sayisi > 0:
        message = f"{basarili_sayisi} soru başarıyla eklendi."
        if hatalar:
            message += f" {len(hatalar)} soru eklenirken hata oluştu."
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "message": "Hiçbir soru eklenemedi. " + "; ".join(hatalar)})

@anket_yonetimi_bp.route('/anket/soru/<int:soru_id>/duzenle', methods=['POST'])
@admin_required
def soru_duzenle(soru_id):
    """Anket sorusunu düzenleme"""
    soru = AnketSoru.query.get(soru_id)
    
    if not soru:
        return jsonify({"success": False, "message": "Soru bulunamadı!"})
    
    soru_metni = request.form.get('soru_metni', '').strip()
    cevap_turu_id = request.form.get('cevap_turu_id')
    soru_sirasi = request.form.get('soru_sirasi')
    cevap_secenekleri = request.form.get('cevap_secenekleri', '').strip()
    zorunlu = request.form.get('zorunlu') == 'on'
    ters_puanlama = request.form.get('ters_puanlama') == 'on'
    
    if not soru_metni or not cevap_turu_id:
        return jsonify({"success": False, "message": "Soru metni ve cevap türü zorunludur!"})
    
    # Sıra numarası belirtilmişse kullan
    if soru_sirasi:
        try:
            soru_sirasi = int(soru_sirasi)
        except:
            soru_sirasi = None
    else:
        soru_sirasi = None
    
    sonuc = AnketService.kaydet_anket_soru(
        soru.anket_id, soru_metni, cevap_turu_id, 
        soru_sirasi, cevap_secenekleri, 
        zorunlu, ters_puanlama, soru_id
    )
    
    return jsonify(sonuc)

@anket_yonetimi_bp.route('/anket/soru/<int:soru_id>/sil', methods=['POST'])
@admin_required
def soru_sil(soru_id):
    """Anket sorusunu silme"""
    sonuc = AnketService.sil_anket_soru(soru_id)
    return jsonify(sonuc)

@anket_yonetimi_bp.route('/anket/<int:anket_id>/sil', methods=['POST'])
@admin_required
def anket_sil(anket_id):
    """Anketi silme"""
    sonuc = AnketService.sil_anket(anket_id)
    
    if sonuc['success']:
        flash(sonuc['message'], 'success')
    else:
        flash(sonuc['message'], 'danger')
        
    return redirect(url_for('anket_yonetimi.index'))

@anket_yonetimi_bp.route('/anket/<int:anket_id>/durum-degistir', methods=['POST'])
@admin_required
def anket_durum_degistir(anket_id):
    """Anket durumunu değiştirme (aktif/pasif)"""
    aktif_mi = request.form.get('durum') == 'aktif'
    
    sonuc = AnketService.anket_durum_degistir(anket_id, aktif_mi)
    
    if sonuc['success']:
        flash(sonuc['message'], 'success')
    else:
        flash(sonuc['message'], 'danger')
        
    return redirect(url_for('anket_yonetimi.index'))

@anket_yonetimi_bp.route('/anket/<int:anket_id>/ogrencilere-ata', methods=['GET', 'POST'])
@admin_required
def ogrencilere_ata(anket_id):
    """Anketi öğrencilere atama formu ve işlemi"""
    anket = AnketService.get_anket(anket_id)
    
    if not anket:
        flash('Anket bulunamadı!', 'danger')
        return redirect(url_for('anket_yonetimi.index'))
    
    if not anket.aktif:
        flash('Pasif bir anket öğrencilere atanamaz!', 'warning')
        return redirect(url_for('anket_yonetimi.anket_detay', anket_id=anket_id))
    
    if request.method == 'POST':
        ogrenci_listesi = request.form.getlist('ogrenci_id')
        
        if not ogrenci_listesi:
            flash('En az bir öğrenci seçmelisiniz!', 'danger')
            return redirect(url_for('anket_yonetimi.ogrencilere_ata', anket_id=anket_id))
        
        sonuc = AnketService.ogrencilere_anket_ata(anket_id, ogrenci_listesi)
        
        if sonuc['success']:
            flash(sonuc['message'], 'success')
            return redirect(url_for('anket_yonetimi.anket_detay', anket_id=anket_id))
        else:
            flash(sonuc['message'], 'danger')
            return redirect(url_for('anket_yonetimi.ogrencilere_ata', anket_id=anket_id))
    
    # Tüm öğrencileri sinif ve şubeye göre gruplayıp getir
    ogrenciler = Ogrenci.query.order_by(Ogrenci.sinif, Ogrenci.sube, Ogrenci.ad, Ogrenci.soyad).all()
    
    # Sınıf-şube gruplarını belirle
    siniflar = {}
    for ogrenci in ogrenciler:
        sinif_key = f"{ogrenci.sinif}-{ogrenci.sube}"
        if sinif_key not in siniflar:
            siniflar[sinif_key] = {
                "ad": f"{ogrenci.sinif}-{ogrenci.sube}",
                "ogrenciler": []
            }
        siniflar[sinif_key]["ogrenciler"].append(ogrenci)
    
    return render_template('anket_yonetimi/ogrencilere_ata.html', 
                         anket=anket, 
                         siniflar=siniflar)

@anket_yonetimi_bp.route('/anket/<int:anket_id>/toplu-cevap-yukle', methods=['GET', 'POST'])
@admin_required
def toplu_cevap_yukle(anket_id):
    """Anket için toplu cevap yükleme formu ve işlemi"""
    anket = AnketService.get_anket(anket_id)
    
    if not anket:
        flash('Anket bulunamadı!', 'danger')
        return redirect(url_for('anket_yonetimi.index'))
    
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('Dosya yüklemelisiniz!', 'danger')
            return redirect(url_for('anket_yonetimi.toplu_cevap_yukle', anket_id=anket_id))
        
        file = request.files['csv_file']
        
        if file.filename == '':
            flash('Dosya seçilmedi!', 'danger')
            return redirect(url_for('anket_yonetimi.toplu_cevap_yukle', anket_id=anket_id))
        
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in ['csv', 'xlsx', 'xls']:
            flash('Yalnızca Excel (.xlsx, .xls) veya CSV (.csv) dosyaları kabul edilir!', 'danger')
            return redirect(url_for('anket_yonetimi.toplu_cevap_yukle', anket_id=anket_id))
        
        sinif = request.form.get('sinif', '').strip()
        
        try:
            if file_ext == 'csv':
                # CSV dosyası için
                csv_content = file.read().decode('utf-8')
                sonuc = AnketService.toplu_cevap_yukle(anket_id, csv_content, sinif, dosya_turu='csv')
            else:
                # Excel dosyası için
                excel_data = file.read()
                sonuc = AnketService.toplu_cevap_yukle(anket_id, excel_data, sinif, dosya_turu='excel')
            
            if sonuc['success']:
                flash(sonuc['message'], 'success')
                return redirect(url_for('anket_yonetimi.anket_detay', anket_id=anket_id))
            else:
                flash(sonuc['message'], 'danger')
        except Exception as e:
            flash(f'Dosya işlenirken bir hata oluştu: {str(e)}', 'danger')
        
        return redirect(url_for('anket_yonetimi.toplu_cevap_yukle', anket_id=anket_id))
    
    # Anket sorularını al
    sorular = AnketSoru.query.filter_by(anket_id=anket_id).order_by(AnketSoru.soru_sirasi).all()
    
    return render_template('anket_yonetimi/toplu_cevap_yukle.html', 
                         anket=anket,
                         sorular=sorular)

@anket_yonetimi_bp.route('/anket/<int:anket_id>/sablon-indir', methods=['GET'])
@admin_required
def sablon_indir(anket_id):
    """Anket cevap şablonu (CSV veya Excel) indirme"""
    anket = AnketService.get_anket(anket_id)
    
    if not anket:
        flash('Anket bulunamadı!', 'danger')
        return redirect(url_for('anket_yonetimi.index'))
    
    # Anket sorularını al
    sorular = AnketSoru.query.filter_by(anket_id=anket_id).order_by(AnketSoru.soru_sirasi).all()
    
    # Dosya formatını al (varsayılan excel)
    dosya_format = request.args.get('format', 'excel').lower()
    
    # Excel formatı isteniyorsa
    if dosya_format == 'excel':
        import openpyxl
        from io import BytesIO
        
        # Yeni workbook oluştur
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Anket {anket_id} Şablonu"
        
        # Başlık satırı
        headers = ['ogrenci_no']
        for i, soru in enumerate(sorular, 1):
            headers.append(f"soru{i}")
        
        ws.append(headers)
        
        # Örnek satır
        example_row = ['123456']
        for _ in sorular:
            example_row.append('')  # Boş bırak
        
        ws.append(example_row)
        
        # Excel dosyasını kullanıcıya gönder
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Benzersiz bir dosya adı oluştur
        from datetime import datetime
        tarih_str = datetime.now().strftime('%Y%m%d_%H%M')
        anket_adi = anket.baslik.replace(' ', '_').lower()[:30]  # Başlığın ilk 30 karakteri
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"{anket_adi}_{tarih_str}.xlsx"
        )
    
    # Varsayılan olarak CSV formatı
    else:
        # CSV oluştur
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Başlık satırı
        headers = ['ogrenci_no']
        for i, soru in enumerate(sorular, 1):
            headers.append(f"soru{i}")
        
        writer.writerow(headers)
        
        # Örnek satır
        example_row = ['123456']
        for _ in sorular:
            example_row.append('')  # Boş bırak
        
        writer.writerow(example_row)
        
        # CSV dosyasını kullanıcıya gönder
        output.seek(0)
        
        # Benzersiz bir dosya adı oluştur
        from datetime import datetime
        tarih_str = datetime.now().strftime('%Y%m%d_%H%M')
        anket_adi = anket.baslik.replace(' ', '_').lower()[:30]  # Başlığın ilk 30 karakteri
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"{anket_adi}_{tarih_str}.csv"
        )

@anket_yonetimi_bp.route('/anket/<int:anket_id>/sonuclar', methods=['GET'])
@admin_required
def anket_sonuclari(anket_id):
    """Anket sonuçları sayfası"""
    anket = AnketService.get_anket(anket_id)
    
    if not anket:
        flash('Anket bulunamadı!', 'danger')
        return redirect(url_for('anket_yonetimi.index'))
    
    sonuclar = AnketService.get_anket_sonuclari(anket_id)
    
    if not sonuclar['success']:
        flash(sonuclar['message'], 'danger')
        return redirect(url_for('anket_yonetimi.anket_detay', anket_id=anket_id))
    
    return render_template('anket_yonetimi/anket_sonuclari.html', 
                         anket=anket,
                         sonuclar=sonuclar)