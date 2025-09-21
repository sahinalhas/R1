"""
Görüşme formu işlemleri için servis modülü
Bu modül, rehberlik görüşme formu ile ilgili iş mantığı işlemlerini gerçekleştirir.
"""

import os
from datetime import datetime
from flask import render_template, url_for
from app.extensions import db
from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from app.blueprints.parametre_yonetimi.models import GorusmeKonusu, OkulBilgi
from app.blueprints.parametre_yonetimi.services import SabitlerService
import weasyprint

class GorusmeFormuService:
    """Görüşme formu işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def generate_cagri_fisi_pdf(form_data):
        """
        Çağrı fişi PDF raporu oluştur
        
        Args:
            form_data: Çağrı bilgilerini içeren form verisi
            
        Returns:
            Dict: İşlem sonucunu ve PDF dosya yolunu içeren sözlük
        """
        # Öğrenci bilgilerini kontrol et
        if not form_data.get('ogrenci_ids') and not form_data.get('ogrenci_id'):
            return {
                'success': False, 
                'message': 'En az bir öğrenci seçmelisiniz.'
            }
            
        # Zaman bilgilerini kontrol et
        if not form_data.get('gelis_saat') or not form_data.get('gelis_saat').strip():
            return {
                'success': False,
                'message': 'Çağrı saati belirtmelisiniz.'
            }
        
        if not form_data.get('gelis_ders') or not form_data.get('gelis_ders').strip():
            return {
                'success': False,
                'message': 'Çağrının yapıldığı dersi belirtmelisiniz.'
            }
        
        try:
            # Öğrenci bilgilerini al
            ogrenci_bilgileri_listesi = []
            
            # Tek öğrenci ID'si gönderilmiş olabilir
            if form_data.get('ogrenci_id'):
                ogrenci_id = form_data.get('ogrenci_id')
                ogrenci = Ogrenci.query.get(ogrenci_id)
                
                if ogrenci:
                    ogrenci_bilgileri_listesi.append({
                        'id': ogrenci.id,
                        'numara': ogrenci.numara,
                        'ad': ogrenci.ad,
                        'soyad': ogrenci.soyad,
                        'sinif': ogrenci.sinif,
                        'tam_ad': f"{ogrenci.ad} {ogrenci.soyad}"
                    })
            
            # Çoklu öğrenci ID'leri gönderilmiş olabilir
            elif form_data.get('ogrenci_ids'):
                for ogrenci_id in form_data.get('ogrenci_ids'):
                    ogrenci = Ogrenci.query.get(ogrenci_id)
                    
                    if ogrenci:
                        ogrenci_bilgileri_listesi.append({
                            'id': ogrenci.id,
                            'numara': ogrenci.numara,
                            'ad': ogrenci.ad,
                            'soyad': ogrenci.soyad,
                            'sinif': ogrenci.sinif,
                            'tam_ad': f"{ogrenci.ad} {ogrenci.soyad}"
                        })
            
            # Hiç öğrenci bulunamadıysa hata döndür
            if not ogrenci_bilgileri_listesi:
                return {
                    'success': False,
                    'message': 'Öğrenci bulunamadı.'
                }
                
            # Okul bilgilerini al
            okul_bilgisi = SabitlerService.get_okul_bilgisi()
            
            # Form verilerini hazırla
            # Gün adını Türkçe olarak al
            gun_adlari = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
            bugun = datetime.now()
            gun_index = bugun.weekday()  # 0: Pazartesi, 1: Salı, ..., 6: Pazar
            
            form_verileri = {
                'gelis_saat': form_data.get('gelis_saat', ''),
                'gelis_ders': form_data.get('gelis_ders', ''),
                'gun_adi': gun_adlari[gun_index]
            }
            
            # Tarih bilgisini daha okunabilir şekilde oluştur (gün ay yıl)
            ay_isimleri = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
                          "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
            gun = bugun.day
            ay = bugun.month
            yil = bugun.year
            tarih_bilgisi = f"{gun} {ay_isimleri[ay-1]} {yil}"
            
            # Fiş numarası için saat bilgisi oluştur (sadece saat, dakika ve saniye)
            fis_no = f"CF-{datetime.now().strftime('%H%M%S')}"
            
            # HTML şablonunu render et
            html_content = render_template(
                'ilk_kayit_formu/pdf/cagri_fisi_pdf.html',
                ogrenciler=ogrenci_bilgileri_listesi,
                form_verileri=form_verileri,
                tarih=tarih_bilgisi,
                fis_no=fis_no,
                okul_bilgisi=okul_bilgisi,
                base_url=url_for('static', filename='', _external=True)
            )
            
            # Geçici PDF dosya yolu
            pdf_filename = f"cagri_fisi_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            pdf_path = os.path.join('app', 'static', 'temp', pdf_filename)
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            # PDF oluştur
            weasyprint.HTML(string=html_content).write_pdf(pdf_path)
            
            # Dosya URL'i
            pdf_url = url_for('static', filename=f"temp/{pdf_filename}")
            
            return {
                'success': True,
                'message': 'Çağrı fişi başarıyla oluşturuldu.',
                'pdf_path': pdf_path,
                'pdf_url': pdf_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"PDF oluşturulurken hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def generate_gorusme_fisi_pdf(form_data):
        """
        Görüşme fişi PDF raporu oluştur
        
        Args:
            form_data: Görüşme bilgilerini içeren form verisi
            
        Returns:
            Dict: İşlem sonucunu ve PDF dosya yolunu içeren sözlük
        """
        # Öğrenci bilgilerini kontrol et
        if not form_data.get('ogrenciler') or len(form_data.get('ogrenciler', [])) == 0:
            return {
                'success': False, 
                'message': 'En az bir öğrenci seçmelisiniz.'
            }
            
        # Zaman bilgilerini kontrol et
        if not form_data.get('gelis_saat') or not form_data.get('gelis_saat').strip():
            return {
                'success': False,
                'message': 'Geliş saati belirtmelisiniz.'
            }
        
        if not form_data.get('gelis_ders') or not form_data.get('gelis_ders').strip():
            return {
                'success': False,
                'message': 'Geliş dersi belirtmelisiniz.'
            }
        
        if not form_data.get('gidis_saat') or not form_data.get('gidis_saat').strip():
            return {
                'success': False,
                'message': 'Gidiş saati belirtmelisiniz.'
            }
        
        if not form_data.get('gidis_ders') or not form_data.get('gidis_ders').strip():
            return {
                'success': False,
                'message': 'Gidiş dersi belirtmelisiniz.'
            }
        
        # Görüşme konusunu al (zorunlu değil)
        gorusme_konusu_id = form_data.get('gorusme_konusu')
        
        try:
            # Öğrenci bilgilerini al
            ogrenci_bilgileri = []
            for ogrenci_id in form_data.get('ogrenciler', []):
                ogrenci = Ogrenci.query.get(ogrenci_id)
                if ogrenci:
                    ogrenci_bilgileri.append({
                        'id': ogrenci.id,
                        'numara': ogrenci.numara,
                        'ad': ogrenci.ad,
                        'soyad': ogrenci.soyad,
                        'sinif': ogrenci.sinif,
                        'tam_ad': f"{ogrenci.ad} {ogrenci.soyad}"
                    })
            
            # Görüşme konusu bilgisini al
            gorusme_konusu = GorusmeKonusu.query.get(gorusme_konusu_id)
            konu_basligi = gorusme_konusu.baslik if gorusme_konusu else "Belirlenmemiş"
            
            # Okul bilgilerini al
            okul_bilgisi = SabitlerService.get_okul_bilgisi()
            
            # Form verilerini hazırla
            form_verileri = {
                'gorusme_konusu': konu_basligi,
                'gorusme_yeri': form_data.get('gorusme_yeri', 'Rehberlik Servisi'),
                'gorusme_sekli': form_data.get('gorusme_sekli', 'Yüzyüze'),
                'aciklama': form_data.get('aciklama', ''),
                'disiplin_durum': form_data.get('disiplin_durum', ''),
                'gorusme_kisi': form_data.get('gorusme_kisi', ''),
                'yakinlik_derecesi': form_data.get('yakinlik_derecesi', ''),
                'kurum_isbirligi': form_data.get('kurum_isbirligi', ''),
                'gelis_saat': form_data.get('gelis_saat', ''),
                'gelis_ders': form_data.get('gelis_ders', ''),
                'gidis_saat': form_data.get('gidis_saat', ''),
                'gidis_ders': form_data.get('gidis_ders', '')
            }
            
            # Tarih bilgisini daha okunabilir şekilde oluştur (gün ay yıl)
            ay_isimleri = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
                          "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
            bugun = datetime.now()
            gun = bugun.day
            ay = bugun.month
            yil = bugun.year
            tarih_bilgisi = f"{gun} {ay_isimleri[ay-1]} {yil}"
            
            # Fiş numarası için saat bilgisi oluştur (sadece saat, dakika ve saniye)
            fis_no = f"GF-{datetime.now().strftime('%H%M%S')}"
            
            # HTML şablonunu render et
            html_content = render_template(
                'ilk_kayit_formu/pdf/gorusme_fisi_pdf.html',
                ogrenci_bilgileri=ogrenci_bilgileri,
                form_verileri=form_verileri,
                tarih=tarih_bilgisi,
                fis_no=fis_no,
                okul_bilgisi=okul_bilgisi,
                base_url=url_for('static', filename='', _external=True)
            )
            
            # Geçici PDF dosya yolu
            pdf_filename = f"gorusme_fisi_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            pdf_path = os.path.join('app', 'static', 'temp', pdf_filename)
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            # PDF oluştur
            weasyprint.HTML(string=html_content).write_pdf(pdf_path)
            
            # Dosya URL'i
            pdf_url = url_for('static', filename=f"temp/{pdf_filename}")
            
            return {
                'success': True,
                'message': 'Görüşme fişi başarıyla oluşturuldu.',
                'pdf_path': pdf_path,
                'pdf_url': pdf_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"PDF oluşturulurken hata oluştu: {str(e)}"
            }