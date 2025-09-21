from flask import render_template, request, redirect, url_for, flash, jsonify
from app.blueprints.ilk_kayit_formu import ilk_kayit_formu_bp
from app.blueprints.ilk_kayit_formu.services import GorusmeFormuService
from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from app.blueprints.parametre_yonetimi.models import GorusmeKonusu
from app.blueprints.parametre_yonetimi.services import SabitlerService
from app.extensions import db

@ilk_kayit_formu_bp.route('/kayit-formu')
def kayit_formu():
    """Rehberlik Servisi Öğrenci Görüşme Fişi sayfası"""
    gorusme_konulari = SabitlerService.get_gorusme_konulari()
    ders_saatleri = SabitlerService.get_ders_saatleri()
    return render_template('ilk_kayit_formu/kayit_formu.html', 
                           gorusme_konulari=gorusme_konulari,
                           ders_saatleri=ders_saatleri)

@ilk_kayit_formu_bp.route('/kayit-formu/ogrenci-ara', methods=['GET'])
def ogrenci_ara():
    """Öğrenci arama API'si"""
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify([])
    
    # Öğrencileri numara, ad, soyad veya sınıfa göre ara
    ogrenciler = Ogrenci.query.filter(
        (Ogrenci.numara.ilike(f'%{query}%')) |
        (Ogrenci.ad.ilike(f'%{query}%')) |
        (Ogrenci.soyad.ilike(f'%{query}%')) |
        (Ogrenci.sinif.ilike(f'%{query}%'))
    ).limit(10).all()
    
    # Ayrıca sınıfı query ile tam eşleşen öğrencileri önceliklendir
    # Bu şekilde sınıfa göre arama daha etkili olacak
    ogrenciler.sort(key=lambda o: 0 if o.sinif.lower() == query.lower() else 1)
    
    sonuclar = []
    for ogrenci in ogrenciler:
        sonuclar.append({
            'id': ogrenci.id,
            'numara': ogrenci.numara,
            'ad': ogrenci.ad,
            'soyad': ogrenci.soyad,
            'tam_ad': f"{ogrenci.ad} {ogrenci.soyad}",
            'sinif': ogrenci.sinif,
            'cinsiyet': ogrenci.cinsiyet
        })
    
    return jsonify(sonuclar)

@ilk_kayit_formu_bp.route('/kayit-formu/ogrenci-detay/<numara>', methods=['GET'])
def ogrenci_detay(numara):
    """Öğrenci numarasına göre detay bilgilerini getir"""
    ogrenci = Ogrenci.query.filter_by(numara=numara).first()
    
    if not ogrenci:
        return jsonify({'error': 'Öğrenci bulunamadı'}), 404
    
    return jsonify({
        'id': ogrenci.id,
        'numara': ogrenci.numara,
        'ad': ogrenci.ad,
        'soyad': ogrenci.soyad,
        'tam_ad': f"{ogrenci.ad} {ogrenci.soyad}",
        'sinif': ogrenci.sinif,
        'cinsiyet': ogrenci.cinsiyet
    })

@ilk_kayit_formu_bp.route('/kayit-formu/gorusme-konulari', methods=['GET'])
def gorusme_konulari():
    """Görüşme konularını getir - API endpointi"""
    query = request.args.get('q', '')
    konular = SabitlerService.get_gorusme_konulari()
    
    # Arama sorgusu varsa, konuları filtrele
    if query and len(query) >= 2:
        filtered_konular = [k for k in konular if query.lower() in k.baslik.lower()]
        konular = filtered_konular
    
    sonuclar = []
    for konu in konular:
        sonuclar.append({
            'id': konu.id,
            'baslik': konu.baslik
        })
    
    return jsonify(sonuclar)

@ilk_kayit_formu_bp.route('/kayit-formu/ders-saatleri', methods=['GET'])
def ders_saatleri_api():
    """Ders saatlerini getir - API endpointi"""
    saatler = SabitlerService.get_ders_saatleri()
    
    sonuclar = []
    for ders_saati in saatler:
        sonuclar.append({
            'id': ders_saati.id,
            'ders_numarasi': ders_saati.ders_numarasi,
            'baslangic_saati': ders_saati.baslangic_saati.strftime('%H:%M'),
            'bitis_saati': ders_saati.bitis_saati.strftime('%H:%M'),
            'ogle_arasi': ders_saati.ogle_arasi
        })
    
    return jsonify(sonuclar)

@ilk_kayit_formu_bp.route('/kayit-formu/gorusme-fisi', methods=['POST'])
def gorusme_fisi_olustur():
    """Görüşme fişi PDF belgesi oluştur"""
    # Form verilerini al
    form_data = request.json
    
    if not form_data:
        return jsonify({'success': False, 'message': 'Form verileri geçersiz.'}), 400
    
    # PDF oluştur
    sonuc = GorusmeFormuService.generate_gorusme_fisi_pdf(form_data)
    
    if not sonuc['success']:
        return jsonify({'success': False, 'message': sonuc['message']}), 400
    
    return jsonify({
        'success': True,
        'message': sonuc['message'],
        'pdf_url': sonuc['pdf_url']
    })

@ilk_kayit_formu_bp.route('/kayit-formu/cagri-fisi', methods=['POST'])
def cagri_fisi_olustur():
    """Çağrı fişi PDF belgesi oluştur"""
    # Form verilerini al
    form_data = request.json
    
    if not form_data:
        return jsonify({'success': False, 'message': 'Form verileri geçersiz.'}), 400
    
    # PDF oluştur
    sonuc = GorusmeFormuService.generate_cagri_fisi_pdf(form_data)
    
    if not sonuc['success']:
        return jsonify({'success': False, 'message': sonuc['message']}), 400
    
    return jsonify({
        'success': True,
        'message': sonuc['message'],
        'pdf_url': sonuc['pdf_url']
    })