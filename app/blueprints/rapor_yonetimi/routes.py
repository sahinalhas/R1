from flask import render_template, send_file, make_response, flash, redirect, url_for, request, jsonify, abort, current_app
from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from app.utils.program import generate_weekly_schedule, calculate_topic_schedule
from app.blueprints.rapor_yonetimi import rapor_yonetimi_bp
from app.utils.auth import ogrenci_required, admin_required
import io
from datetime import datetime, timedelta, date
import weasyprint
from app.blueprints.rapor_yonetimi.models import FaaliyetRaporu, RaporSablonu, IstatistikRaporu, RaporlananOlay
from app.extensions import db

def generate_pdf(template_name, title, **context):
    """PDF rapor oluştur - Blueprint şablonlarını kullanır"""
    # PDF oluşturma tarihini ekle
    context['now'] = datetime.now()
    
    # Türkçe gün adlarını ekle
    context['gunler'] = [
        'Pazartesi', 'Salı', 'Çarşamba', 
        'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'
    ]
    
    # Title'ı context'e ekle
    context['title'] = title
    
    # Blueprint'in şablon yolunu kullanarak HTML içeriği oluştur
    template_path = f'pdf/{template_name}'
    html_content = render_template(template_path, **context)
    
    # HTML'i PDF'e dönüştür
    pdf = weasyprint.HTML(string=html_content).write_pdf()
    
    # PDF içeriğini HTTP cevabı olarak hazırla
    response = make_response(pdf)
    
    # Content-Type ve Content-Disposition başlıklarını ayarla
    # Türkçe karakterleri ASCII'ye dönüştür
    import unicodedata
    import re
    
    def slugify(value):
        """Converts to ASCII and removes special characters, spaces, etc."""
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value.lower())
        return re.sub(r'[-\s]+', '_', value).strip('_')
    
    file_name = slugify(title) + '.pdf'
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{file_name}"'
    
    return response

@rapor_yonetimi_bp.route('/haftalik-plan-pdf/<int:ogrenci_id>')
@ogrenci_required
def haftalik_plan_pdf(ogrenci_id, ogrenci=None):
    """Öğrencinin haftalık ders planını PDF olarak oluştur"""
    try:
        # Haftalık programı hesapla
        program_data = generate_weekly_schedule(ogrenci_id)
        
        # Günlerin int olarak erişilebileceği bir program nesnesine dönüştür
        # Şablonda program[j] şeklinde erişilebilmesi için
        int_program = {}
        for gun_str, dersler in program_data.items():
            int_program[int(gun_str)] = dersler
            
        # PDF oluştur
        title = f'{ogrenci.ad} {ogrenci.soyad} - Haftalık Ders Programı'
        return generate_pdf(
            template_name='haftalik_plan_pdf.html',
            title=title,
            ogrenci=ogrenci,
            program=int_program
        )
    except Exception as e:
        flash(f'PDF oluşturulurken bir hata oluştu: {str(e)}', 'danger')
        return redirect(url_for('ogrenci_yonetimi.profil', ogrenci_id=ogrenci_id))

@rapor_yonetimi_bp.route('/konu-plani-pdf/<int:ogrenci_id>')
@ogrenci_required
def konu_plani_pdf(ogrenci_id, ogrenci=None):
    """Öğrencinin konu bazlı çalışma planını PDF olarak oluştur"""
    try:
        # Konu planını hesapla
        konu_plani = calculate_topic_schedule(ogrenci_id)
        
        # Günlerin int olarak erişilebileceği bir konu planı nesnesine dönüştür
        # Şablonda konu_plani[gun_index] şeklinde erişilebilmesi için
        int_konu_plani = {}
        for gun_str, konular in konu_plani.items():
            int_konu_plani[int(gun_str)] = konular
            
        # PDF oluştur
        title = f'{ogrenci.ad} {ogrenci.soyad} - Konu Çalışma Planı'
        return generate_pdf(
            template_name='konu_plani_pdf.html',
            title=title,
            ogrenci=ogrenci,
            konu_plani=int_konu_plani
        )
    except Exception as e:
        flash(f'PDF oluşturulurken bir hata oluştu: {str(e)}', 'danger')
        return redirect(url_for('ogrenci_yonetimi.profil', ogrenci_id=ogrenci_id))

@rapor_yonetimi_bp.route('/ilerleme-raporu-pdf/<int:ogrenci_id>')
@ogrenci_required
def ilerleme_raporu_pdf(ogrenci_id, ogrenci=None):
    """Öğrencinin ilerleme raporunu PDF olarak oluştur"""
    try:
        # İlerleme verilerini almak için yeni servis fonksiyonumuzu kullanalım
        from app.blueprints.rapor_yonetimi.services import RaporService
        sonuc = RaporService.generate_ilerleme_raporu_pdf(ogrenci_id)
        
        if not sonuc['success']:
            flash(sonuc['message'], 'danger')
            return redirect(url_for('ogrenci_yonetimi.profil', ogrenci_id=ogrenci_id))
        
        # PDF dosyasını döndür
        from flask import current_app
        import os
        abs_path = os.path.join(current_app.root_path, sonuc['pdf_path'])
        return send_file(abs_path, as_attachment=True)
    except Exception as e:
        flash(f'PDF oluşturulurken bir hata oluştu: {str(e)}', 'danger')
        return redirect(url_for('ogrenci_yonetimi.profil', ogrenci_id=ogrenci_id))

# ========== MEB ve Dönemsel Raporlar ==========

@rapor_yonetimi_bp.route('/rapor-yonetimi')
def rapor_yonetimi_index():
    """Rapor yönetimi ana sayfası"""
    # Mevcut raporları al
    faaliyet_raporlari = FaaliyetRaporu.query.order_by(FaaliyetRaporu.olusturma_tarihi.desc()).all()
    istatistik_raporlari = IstatistikRaporu.query.order_by(IstatistikRaporu.olusturma_tarihi.desc()).all()
    
    # Rapor şablonlarını al
    sablonlar = RaporSablonu.query.all()
    
    return render_template(
        'rapor_yonetimi/index.html',
        faaliyet_raporlari=faaliyet_raporlari,
        istatistik_raporlari=istatistik_raporlari,
        sablonlar=sablonlar
    )

@rapor_yonetimi_bp.route('/donemsel-rapor', methods=['GET', 'POST'])
def donemsel_rapor():
    """Dönemsel faaliyet raporu oluşturma sayfası"""
    from app.blueprints.rapor_yonetimi.services import RaporService
    
    if request.method == 'POST':
        baslik = request.form.get('baslik', '').strip()
        donem = request.form.get('donem', '').strip()
        rapor_tipi = request.form.get('rapor_tipi', 'dönemsel')
        baslangic_tarihi = datetime.strptime(request.form.get('baslangic_tarihi'), '%Y-%m-%d').date()
        bitis_tarihi = datetime.strptime(request.form.get('bitis_tarihi'), '%Y-%m-%d').date()
        yorum = request.form.get('yorum', '').strip() or None
        
        # Validasyon
        if not baslik or not donem or not baslangic_tarihi or not bitis_tarihi:
            flash('Lütfen tüm zorunlu alanları doldurun.', 'danger')
            return redirect(url_for('rapor_yonetimi.donemsel_rapor'))
        
        # Rapor verilerini oluştur
        rapor_verileri = RaporService.generate_donemsel_rapor_verileri(baslangic_tarihi, bitis_tarihi)
        
        # Raporu oluştur
        sonuc = RaporService.create_faaliyet_raporu(baslik, donem, rapor_tipi, rapor_verileri, yorum)
        
        if sonuc['success']:
            flash(sonuc['message'], 'success')
            return redirect(url_for('rapor_yonetimi.rapor_detay', rapor_id=sonuc['rapor_id']))
        else:
            flash(sonuc['message'], 'danger')
            return redirect(url_for('rapor_yonetimi.donemsel_rapor'))
    
    # Varsayılan tarih aralığı (Mevcut dönem)
    bugun = date.today()
    # Dönem belirleme (Eylül-Ocak veya Şubat-Haziran)
    if bugun.month >= 9 or bugun.month <= 1:  # Güz dönemi
        baslangic_tarihi = date(bugun.year if bugun.month >= 9 else bugun.year - 1, 9, 1)
        bitis_tarihi = date(bugun.year + 1 if bugun.month >= 9 else bugun.year, 1, 31)
        donem = f"{baslangic_tarihi.year}-{bitis_tarihi.year} Güz"
    else:  # Bahar dönemi
        baslangic_tarihi = date(bugun.year, 2, 1)
        bitis_tarihi = date(bugun.year, 6, 30)
        donem = f"{baslangic_tarihi.year}-{bitis_tarihi.year} Bahar"
    
    return render_template(
        'rapor_yonetimi/donemsel_rapor.html',
        baslangic_tarihi=baslangic_tarihi,
        bitis_tarihi=bitis_tarihi,
        donem=donem
    )

@rapor_yonetimi_bp.route('/rapor-detay/<int:rapor_id>')
def rapor_detay(rapor_id):
    """Faaliyet raporu detay sayfası"""
    # Raporu veritabanından al
    rapor = FaaliyetRaporu.query.get_or_404(rapor_id)
    
    # Rapor verilerini dict olarak alalım
    rapor_verileri = rapor.rapor_verileri_dict
    
    return render_template(
        'rapor_yonetimi/rapor_detay.html',
        rapor=rapor,
        rapor_verileri=rapor_verileri
    )

@rapor_yonetimi_bp.route('/rapor-pdf/<int:rapor_id>')
def rapor_pdf(rapor_id):
    """Faaliyet raporu PDF indirme"""
    from app.blueprints.rapor_yonetimi.services import RaporService
    
    # Raporu veritabanından al
    rapor = FaaliyetRaporu.query.get_or_404(rapor_id)
    
    # PDF oluştur
    sonuc = RaporService.generate_meb_faaliyet_raporu_pdf(rapor_id)
    
    if not sonuc['success']:
        flash(sonuc['message'], 'danger')
        return redirect(url_for('rapor_yonetimi.rapor_detay', rapor_id=rapor_id))
    
    # PDF dosyasını döndür
    import os
    abs_path = os.path.join(current_app.root_path, sonuc['pdf_path'])
    return send_file(abs_path, as_attachment=True)

@rapor_yonetimi_bp.route('/rapor-excel/<int:rapor_id>')
def rapor_excel(rapor_id):
    """Faaliyet raporu Excel indirme"""
    from app.blueprints.rapor_yonetimi.services import RaporService
    
    # Raporu veritabanından al
    rapor = FaaliyetRaporu.query.get_or_404(rapor_id)
    
    # Excel oluştur
    excel_data = RaporService.export_faaliyet_raporu_excel(rapor_id)
    
    if not excel_data:
        flash('Excel dosyası oluşturulurken bir hata oluştu.', 'danger')
        return redirect(url_for('rapor_yonetimi.rapor_detay', rapor_id=rapor_id))
    
    # Excel dosyasını döndür
    return send_file(
        excel_data,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f"faaliyet_raporu_{rapor_id}.xlsx"
    )

@rapor_yonetimi_bp.route('/istatistik-raporu', methods=['GET', 'POST'])
def istatistik_raporu():
    """İstatistiksel analiz raporu oluşturma sayfası"""
    from app.blueprints.rapor_yonetimi.services import RaporService
    
    if request.method == 'POST':
        rapor_tipi = request.form.get('rapor_tipi')
        baslangic_tarihi = datetime.strptime(request.form.get('baslangic_tarihi'), '%Y-%m-%d').date()
        bitis_tarihi = datetime.strptime(request.form.get('bitis_tarihi'), '%Y-%m-%d').date()
        
        # Filtreleri al
        filtreler = {
            'sinif': request.form.getlist('sinif[]'),
            'calisma_alani': request.form.getlist('calisma_alani[]')
        }
        
        # Validasyon
        if not rapor_tipi or not baslangic_tarihi or not bitis_tarihi:
            flash('Lütfen tüm zorunlu alanları doldurun.', 'danger')
            return redirect(url_for('rapor_yonetimi.istatistik_raporu'))
        
        # Raporu oluştur
        sonuc = RaporService.generate_istatistik_raporu(rapor_tipi, baslangic_tarihi, bitis_tarihi, filtreler)
        
        if sonuc['success']:
            flash(sonuc['message'], 'success')
            return redirect(url_for('rapor_yonetimi.istatistik_rapor_detay', rapor_id=sonuc['rapor_id']))
        else:
            flash(sonuc['message'], 'danger')
            return redirect(url_for('rapor_yonetimi.istatistik_raporu'))
    
    # Varsayılan tarih aralığı (son 1 ay)
    bugun = date.today()
    bir_ay_once = bugun - timedelta(days=30)
    
    # Sınıf listesi
    siniflar = db.session.query(Ogrenci.sinif).distinct().all()
    siniflar = [s[0] for s in siniflar]
    
    return render_template(
        'rapor_yonetimi/istatistik_raporu.html',
        baslangic_tarihi=bir_ay_once,
        bitis_tarihi=bugun,
        siniflar=siniflar
    )

@rapor_yonetimi_bp.route('/istatistik-rapor-detay/<int:rapor_id>')
def istatistik_rapor_detay(rapor_id):
    """İstatistik raporu detay sayfası"""
    # Raporu veritabanından al
    rapor = IstatistikRaporu.query.get_or_404(rapor_id)
    
    return render_template(
        'rapor_yonetimi/istatistik_rapor_detay.html',
        rapor=rapor
    )