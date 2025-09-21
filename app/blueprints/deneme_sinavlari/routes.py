from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from app.extensions import db
from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from app.blueprints.deneme_sinavlari.models import DenemeSonuc
from app.blueprints.deneme_sinavlari import deneme_sinavlari_bp

@deneme_sinavlari_bp.route('/ogrenci/<int:ogrenci_id>/sonuclar', methods=['GET', 'POST'])
def sonuclar(ogrenci_id):
    """Öğrencinin deneme sınavı sonuçlarını görüntüleme ve ekleme"""
    ogrenci = Ogrenci.query.get_or_404(ogrenci_id)
    
    # POST isteği: Yeni deneme sonucu ekle
    if request.method == 'POST':
        # Form verilerini al
        deneme_adi = request.form.get('deneme_adi')
        tarih_str = request.form.get('tarih')
        
        # TYT netleri
        net_tyt_turkce = float(request.form.get('net_tyt_turkce') or 0)
        net_tyt_sosyal = float(request.form.get('net_tyt_sosyal') or 0)
        net_tyt_matematik = float(request.form.get('net_tyt_matematik') or 0)
        net_tyt_fen = float(request.form.get('net_tyt_fen') or 0)
        
        # AYT netleri
        net_ayt_matematik = float(request.form.get('net_ayt_matematik') or 0)
        net_ayt_fizik = float(request.form.get('net_ayt_fizik') or 0)
        net_ayt_kimya = float(request.form.get('net_ayt_kimya') or 0)
        net_ayt_biyoloji = float(request.form.get('net_ayt_biyoloji') or 0)
        net_ayt_edebiyat = float(request.form.get('net_ayt_edebiyat') or 0)
        net_ayt_tarih = float(request.form.get('net_ayt_tarih') or 0)
        net_ayt_cografya = float(request.form.get('net_ayt_cografya') or 0)
        net_ayt_felsefe = float(request.form.get('net_ayt_felsefe') or 0)
        
        # Puanlar (Kullanıcı tarafından girilecek)
        puan_tyt = float(request.form.get('puan_tyt') or 0)
        puan_say = float(request.form.get('puan_say') or 0)
        puan_ea = float(request.form.get('puan_ea') or 0)
        puan_soz = float(request.form.get('puan_soz') or 0)
        
        # Validasyon
        if not deneme_adi or not tarih_str:
            flash('Lütfen deneme adı ve tarih alanlarını doldurun!', 'danger')
            return redirect(url_for('deneme_sinavlari.sonuclar', ogrenci_id=ogrenci_id))
        
        try:
            tarih = datetime.strptime(tarih_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Lütfen geçerli bir tarih girin!', 'danger')
            return redirect(url_for('deneme_sinavlari.sonuclar', ogrenci_id=ogrenci_id))
        
        # Yeni deneme sonucu oluştur
        yeni_sonuc = DenemeSonuc(
            ogrenci_id=ogrenci_id,
            deneme_adi=deneme_adi,
            tarih=tarih,
            net_tyt_turkce=net_tyt_turkce,
            net_tyt_sosyal=net_tyt_sosyal,
            net_tyt_matematik=net_tyt_matematik,
            net_tyt_fen=net_tyt_fen,
            net_ayt_matematik=net_ayt_matematik,
            net_ayt_fizik=net_ayt_fizik,
            net_ayt_kimya=net_ayt_kimya,
            net_ayt_biyoloji=net_ayt_biyoloji,
            net_ayt_edebiyat=net_ayt_edebiyat,
            net_ayt_tarih=net_ayt_tarih,
            net_ayt_cografya=net_ayt_cografya,
            net_ayt_felsefe=net_ayt_felsefe,
            puan_tyt=puan_tyt,
            puan_say=puan_say,
            puan_ea=puan_ea,
            puan_soz=puan_soz
        )
        
        # Veritabanına kaydet
        db.session.add(yeni_sonuc)
        db.session.commit()
        
        flash(f'"{deneme_adi}" deneme sonuçları başarıyla kaydedildi!', 'success')
        return redirect(url_for('deneme_sinavlari.sonuclar', ogrenci_id=ogrenci_id))
    
    # GET isteği: Sonuçları görüntüle
    sonuclar = DenemeSonuc.query.filter_by(ogrenci_id=ogrenci_id).order_by(DenemeSonuc.tarih.desc()).all()
    
    # Grafik verileri
    puanlar_tyt = []
    puanlar_say = []
    puanlar_ea = []
    puanlar_soz = []
    tarihler = []
    
    # TYT netleri grafiği
    netler_tyt_turkce = []
    netler_tyt_matematik = []
    netler_tyt_sosyal = []
    netler_tyt_fen = []
    
    # Sonuçları tarihe göre sırala (eski->yeni)
    sonuclar_ordered = sorted(sonuclar, key=lambda x: x.tarih)
    
    for sonuc in sonuclar_ordered:
        puanlar_tyt.append(sonuc.puan_tyt)
        puanlar_say.append(sonuc.puan_say)
        puanlar_ea.append(sonuc.puan_ea)
        puanlar_soz.append(sonuc.puan_soz)
        tarihler.append(sonuc.tarih.strftime('%d.%m.%y'))
        
        netler_tyt_turkce.append(sonuc.net_tyt_turkce)
        netler_tyt_matematik.append(sonuc.net_tyt_matematik)
        netler_tyt_sosyal.append(sonuc.net_tyt_sosyal)
        netler_tyt_fen.append(sonuc.net_tyt_fen)
    
    return render_template('deneme_sinavlari/deneme_sonuclari.html',
                          ogrenci=ogrenci,
                          sonuclar=sonuclar,
                          puanlar_tyt=puanlar_tyt,
                          puanlar_say=puanlar_say,
                          puanlar_ea=puanlar_ea,
                          puanlar_soz=puanlar_soz,
                          tarihler=tarihler,
                          netler_tyt_turkce=netler_tyt_turkce,
                          netler_tyt_matematik=netler_tyt_matematik,
                          netler_tyt_sosyal=netler_tyt_sosyal,
                          netler_tyt_fen=netler_tyt_fen)

@deneme_sinavlari_bp.route('/ogrenci/<int:ogrenci_id>/deneme/<int:deneme_id>/sil', methods=['POST'])
def sil(ogrenci_id, deneme_id):
    """Deneme sınavı sonucunu silme işlemi"""
    deneme = DenemeSonuc.query.get_or_404(deneme_id)
    
    # Yetki kontrolü
    if deneme.ogrenci_id != ogrenci_id:
        flash('Bu sonucu silme yetkiniz yok!', 'danger')
        return redirect(url_for('deneme_sinavlari.sonuclar', ogrenci_id=ogrenci_id))
    
    # Sınav adını saklayalım
    deneme_adi = deneme.deneme_adi
    
    # Deneme sonucunu sil
    db.session.delete(deneme)
    db.session.commit()
    
    flash(f'"{deneme_adi}" deneme sonucu başarıyla silindi!', 'success')
    return redirect(url_for('deneme_sinavlari.sonuclar', ogrenci_id=ogrenci_id))