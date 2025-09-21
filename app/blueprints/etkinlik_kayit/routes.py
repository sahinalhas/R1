"""
Etkinlik Kayıt Modülü blueprint'i için route tanımlamaları.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from app.blueprints.etkinlik_kayit import etkinlik_kayit_bp
from app.blueprints.etkinlik_kayit.services import EtkinlikService
from app.utils.auth import admin_required

@etkinlik_kayit_bp.route('/')
def index():
    """Etkinlik Kayıt ana sayfası - Etkinliklerin listelendiği sayfa"""
    etkinlikler = EtkinlikService.get_all_etkinlikler()
    return render_template('etkinlik_kayit/etkinlik_listesi.html', 
                          etkinlikler=etkinlikler, 
                          active_page="etkinlik_kayit")

@etkinlik_kayit_bp.route('/yeni', methods=['GET', 'POST'])
def yeni_etkinlik():
    """Yeni etkinlik ekleme sayfası"""
    if request.method == 'POST':
        # Form verilerini al
        form_data = {
            'etkinlik_tarihi': datetime.strptime(request.form['etkinlik_tarihi'], '%Y-%m-%d').date(),
            'calisma_yontemi': request.form['calisma_yontemi'],
            'aciklama': request.form['aciklama'],
            'hedef_turu': request.form['hedef_turu'],
            'faaliyet_turu': request.form['faaliyet_turu'],
            'ogretmen_sayisi': request.form.get('ogretmen_sayisi', 0),
            'veli_sayisi': request.form.get('veli_sayisi', 0),
            'diger_katilimci_sayisi': request.form.get('diger_katilimci_sayisi', 0),
            'erkek_ogrenci_sayisi': request.form.get('erkek_ogrenci_sayisi', 0),
            'kiz_ogrenci_sayisi': request.form.get('kiz_ogrenci_sayisi', 0),
            'sinif_bilgisi': request.form.get('sinif_bilgisi', ''),
            'resmi_yazi_sayisi': request.form.get('resmi_yazi_sayisi', '')
        }
        
        # Etkinlik oluştur
        EtkinlikService.create_etkinlik(form_data)
        flash('Etkinlik başarıyla kaydedildi.', 'success')
        return redirect(url_for('etkinlik_kayit.index'))
    
    # GET isteği - form sayfasını göster
    etkinlik_turleri = EtkinlikService.get_etkinlik_turleri()
    hedef_turleri = EtkinlikService.get_hedef_turleri()
    calisma_yontemleri = EtkinlikService.get_calisma_yontemleri()
    
    return render_template('etkinlik_kayit/etkinlik_formu.html',
                          etkinlik=None,
                          etkinlik_turleri=etkinlik_turleri,
                          hedef_turleri=hedef_turleri,
                          calisma_yontemleri=calisma_yontemleri,
                          form_action="yeni",
                          active_page="etkinlik_kayit")

@etkinlik_kayit_bp.route('/duzenle/<int:etkinlik_id>', methods=['GET', 'POST'])
def etkinlik_duzenle(etkinlik_id):
    """Etkinlik düzenleme sayfası"""
    etkinlik = EtkinlikService.get_etkinlik_by_id(etkinlik_id)
    if not etkinlik:
        flash('Etkinlik bulunamadı.', 'error')
        return redirect(url_for('etkinlik_kayit.index'))
    
    if request.method == 'POST':
        # Form verilerini al
        form_data = {
            'etkinlik_tarihi': datetime.strptime(request.form['etkinlik_tarihi'], '%Y-%m-%d').date(),
            'calisma_yontemi': request.form['calisma_yontemi'],
            'aciklama': request.form['aciklama'],
            'hedef_turu': request.form['hedef_turu'],
            'faaliyet_turu': request.form['faaliyet_turu'],
            'ogretmen_sayisi': request.form.get('ogretmen_sayisi', 0),
            'veli_sayisi': request.form.get('veli_sayisi', 0),
            'diger_katilimci_sayisi': request.form.get('diger_katilimci_sayisi', 0),
            'erkek_ogrenci_sayisi': request.form.get('erkek_ogrenci_sayisi', 0),
            'kiz_ogrenci_sayisi': request.form.get('kiz_ogrenci_sayisi', 0),
            'sinif_bilgisi': request.form.get('sinif_bilgisi', ''),
            'resmi_yazi_sayisi': request.form.get('resmi_yazi_sayisi', '')
        }
        
        # Etkinliği güncelle
        EtkinlikService.update_etkinlik(etkinlik_id, form_data)
        flash('Etkinlik başarıyla güncellendi.', 'success')
        return redirect(url_for('etkinlik_kayit.index'))
    
    # GET isteği - form sayfasını göster
    etkinlik_turleri = EtkinlikService.get_etkinlik_turleri()
    hedef_turleri = EtkinlikService.get_hedef_turleri()
    calisma_yontemleri = EtkinlikService.get_calisma_yontemleri()
    
    return render_template('etkinlik_kayit/etkinlik_formu.html',
                          etkinlik=etkinlik,
                          etkinlik_turleri=etkinlik_turleri,
                          hedef_turleri=hedef_turleri,
                          calisma_yontemleri=calisma_yontemleri,
                          form_action="duzenle",
                          active_page="etkinlik_kayit")

@etkinlik_kayit_bp.route('/sil/<int:etkinlik_id>', methods=['POST'])
def etkinlik_sil(etkinlik_id):
    """Etkinlik silme işlemi"""
    if EtkinlikService.delete_etkinlik(etkinlik_id):
        flash('Etkinlik başarıyla silindi.', 'success')
    else:
        flash('Etkinlik silinirken bir hata oluştu.', 'error')
    
    return redirect(url_for('etkinlik_kayit.index'))

@etkinlik_kayit_bp.route('/detay/<int:etkinlik_id>')
def etkinlik_detay(etkinlik_id):
    """Etkinlik detay sayfası"""
    etkinlik = EtkinlikService.get_etkinlik_by_id(etkinlik_id)
    if not etkinlik:
        flash('Etkinlik bulunamadı.', 'error')
        return redirect(url_for('etkinlik_kayit.index'))
    
    return render_template('etkinlik_kayit/etkinlik_detay.html',
                          etkinlik=etkinlik,
                          active_page="etkinlik_kayit")