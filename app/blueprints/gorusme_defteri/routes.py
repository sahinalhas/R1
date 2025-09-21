"""
Görüşme Defteri blueprint'i için route tanımlamaları.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from app.blueprints.gorusme_defteri import gorusme_defteri_bp
from app.blueprints.gorusme_defteri.services import GorusmeService
from app.blueprints.gorusme_defteri.helpers import get_categories
from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from app.blueprints.parametre_yonetimi.models import GorusmeKonusu
from app.utils.auth import admin_required

@gorusme_defteri_bp.route('/')
def index():
    """Görüşme Defteri ana sayfası"""
    from app.blueprints.parametre_yonetimi.services import SabitlerService
    
    # Okul bilgisini al
    okul_bilgisi = SabitlerService.get_okul_bilgisi()
    okul_adi = okul_bilgisi.okul_adi if okul_bilgisi else "YKS Çalışma Takip Sistemi"
    
    return render_template('gorusme_defteri/gorusme_defteri.html', okul_adi=okul_adi)

@gorusme_defteri_bp.route('/api/meeting-diary')
def get_gorusme_kayitlari():
    """Görüşme kayıtlarını getir - API endpointi"""
    ay = request.args.get('ay')
    if ay:
        try:
            ay = int(ay)
        except ValueError:
            return jsonify({"error": "Geçersiz ay değeri"}), 400
    
    kayitlar = GorusmeService.get_all_gorusme_kayitlari(ay=ay)
    
    # API yanıtı için görüşme verilerini serialize et
    kayitlar_json = []
    for kayit in kayitlar:
        ogrenci = kayit.ogrenci
        kayitlar_json.append({
            "id": kayit.id,
            "studentNumber": ogrenci.numara if ogrenci else "",
            "studentName": ogrenci.tam_ad if ogrenci else "",
            "studentClass": ogrenci.sinif if ogrenci else "",
            "studentGender": ogrenci.cinsiyet if ogrenci else "",
            "date": kayit.tarih.isoformat(),
            "startTime": kayit.baslangic_saati.strftime('%H:%M') if kayit.baslangic_saati else "",
            "endTime": kayit.bitis_saati.strftime('%H:%M') if kayit.bitis_saati else "",
            "sessionCount": kayit.gorusme_sayisi,
            "personMet": kayit.gorusulen_kisi,
            "personRole": kayit.kisi_rolu,
            "relationship": kayit.yakinlik_derecesi,
            "topic": kayit.gorusme_konusu,
            "workArea": kayit.calisma_alani,
            "workCategory": kayit.calisma_kategorisi,
            "serviceType": kayit.hizmet_turu,
            "institutionalCooperation": kayit.kurum_isbirligi,
            "meetingPlace": kayit.gorusme_yeri,
            "isDisciplinary": kayit.disiplin_gorusmesi,
            "isLegalReferral": kayit.adli_sevk,
            "workMethod": kayit.calisma_yontemi,
            "summary": kayit.ozet,
            "mebbisStatus": "Aktarıldı" if kayit.mebbis_aktarildi else "Bekliyor"
        })
    
    return jsonify(kayitlar_json)

@gorusme_defteri_bp.route('/api/sync-mebbis', methods=['POST'])
def sync_mebbis():
    """MEBBİS senkronizasyon endpoint'i"""
    result = GorusmeService.sync_mebbis()
    return jsonify(result)

@gorusme_defteri_bp.route('/api/delete/<int:kayit_id>', methods=['DELETE'])
def delete_gorusme(kayit_id):
    """Görüşme kaydı silme API endpoint'i"""
    result = GorusmeService.delete_gorusme_kaydi(kayit_id)
    return jsonify(result)

@gorusme_defteri_bp.route('/api/update/<int:kayit_id>', methods=['PUT'])
def update_gorusme(kayit_id):
    """Görüşme kaydı güncelleme API endpoint'i"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'Güncelleme verileri geçersiz'}), 400
            
        # Tarih ve saat bilgilerini işle
        tarih = None
        baslangic_saati = None
        bitis_saati = None
        
        if 'date' in data:
            try:
                tarih = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': 'Geçersiz tarih formatı'}), 400
                
        if 'startTime' in data:
            try:
                baslangic_saati = datetime.strptime(data['startTime'], '%H:%M').time()
            except ValueError:
                return jsonify({'success': False, 'message': 'Geçersiz başlangıç saati formatı'}), 400
                
        if 'endTime' in data:
            try:
                bitis_saati = datetime.strptime(data['endTime'], '%H:%M').time()
            except ValueError:
                return jsonify({'success': False, 'message': 'Geçersiz bitiş saati formatı'}), 400
        
        # Doğrudan güncellenecek tarih ve saat değerleri
        update_kwargs = {}
        if tarih:
            update_kwargs['tarih'] = tarih
        if baslangic_saati:
            update_kwargs['baslangic_saati'] = baslangic_saati
        if bitis_saati:
            update_kwargs['bitis_saati'] = bitis_saati
            
        # API model anahtarlarını veritabanı model alanlarına dönüştür
        field_mapping = {
            'studentNumber': None,  # Bu alanları doğrudan güncellemeyi desteklemiyoruz
            'studentName': None,    # Bu alanları doğrudan güncellemeyi desteklemiyoruz
            'studentClass': None,   # Bu alanları doğrudan güncellemeyi desteklemiyoruz
            'studentGender': None,  # Bu alanları doğrudan güncellemeyi desteklemiyoruz
            'date': None,           # Yukarıda update_kwargs içine ekledik
            'startTime': None,      # Yukarıda update_kwargs içine ekledik
            'endTime': None,        # Yukarıda update_kwargs içine ekledik
            'sessionCount': 'gorusme_sayisi',
            'personMet': 'gorusulen_kisi',
            'personRole': 'kisi_rolu',
            'relationship': 'yakinlik_derecesi',
            'topic': 'gorusme_konusu',
            'workArea': 'calisma_alani',
            'workCategory': 'calisma_kategorisi',
            'serviceType': 'hizmet_turu',
            'institutionalCooperation': 'kurum_isbirligi',
            'meetingPlace': 'gorusme_yeri',
            'isDisciplinary': 'disiplin_gorusmesi',
            'isLegalReferral': 'adli_sevk',
            'workMethod': 'calisma_yontemi',
            'summary': 'ozet',
            'mebbisStatus': None,  # Bu alanı doğrudan güncellemeyi desteklemiyoruz
        }
        
        # API'dan gelen verileri model için uygun formata dönüştür
        update_data = {}
        for api_field, value in data.items():
            if api_field in field_mapping and field_mapping[api_field] is not None:
                db_field = field_mapping[api_field]
                # String olmayan anahtar hatasını önlemek için db_field'in string olduğundan emin olalım
                update_data[str(db_field)] = value
        
        # Tarih ve saat değerlerini ekleyelim
        update_data.update(update_kwargs)
        
        # Güncelleme işlemini gerçekleştir
        result = GorusmeService.update_gorusme_kaydi(kayit_id, **update_data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Görüşme kaydı güncellenirken bir hata oluştu: {str(e)}'
        }), 500

@gorusme_defteri_bp.route('/api/kaydet', methods=['POST'])
def kaydet_gorusme():
    """Görüşme kaydı oluşturma API endpoint'i"""
    try:
        # Form verilerini al
        form_data = request.json
        
        if not form_data:
            return jsonify({'success': False, 'message': 'Form verileri geçersiz'}), 400
            
        # Görüşme konusu
        gorusme_konusu_id = form_data.get('gorusme_konusu')
        gorusme_konusu_baslik = ""
        
        if gorusme_konusu_id:
            # Görüşme konusu kayıttan adını al
            gorusme_konusu = GorusmeKonusu.query.get(gorusme_konusu_id)
            if gorusme_konusu:
                gorusme_konusu_baslik = gorusme_konusu.baslik
        
        # Zaman bilgilerini düzenle
        try:
            baslangic_saati = datetime.strptime(form_data.get('gelis_zamani', '00:00'), '%H:%M').time()
            bitis_saati = datetime.strptime(form_data.get('gidis_zamani', '00:00'), '%H:%M').time()
        except ValueError:
            return jsonify({'success': False, 'message': 'Geçersiz saat formatı'}), 400
        
        # Görüşme şekli bilgisini al
        gorusme_sekli = form_data.get('gorusme_sekli', 'Yüzyüze')
        
        # Görüşme konusuna ve görüşme şekline göre kategorileri otomatik belirle
        categories = get_categories(gorusme_konusu_baslik, gorusme_sekli)
        
        # Ortak form bilgileri
        common_data = {
            'tarih': datetime.now().date(),
            'baslangic_saati': baslangic_saati,
            'bitis_saati': bitis_saati,
            'gorusme_sayisi': 1,  # Varsayılan 1
            'gorusulen_kisi': form_data.get('gorusulen_kisi', ''),
            'kisi_rolu': categories['kisi_rolu'],  # Görüşme konusuna göre belirlenen rol
            'yakinlik_derecesi': form_data.get('yakinlik_derecesi', ''),
            'gorusme_konusu': gorusme_konusu_baslik,
            'calisma_alani': categories['calisma_alani'],
            'calisma_kategorisi': categories['calisma_kategorisi'],
            'hizmet_turu': categories['hizmet_turu'],
            'kurum_isbirligi': form_data.get('kurum_isbirligi', ''),
            'gorusme_yeri': form_data.get('gorusme_yeri', 'Rehberlik Servisi'),
            'disiplin_gorusmesi': form_data.get('disiplin_durumu') == 'kurulaSevk',
            'adli_sevk': False,  # Form'da karşılığı yok
            'calisma_yontemi': categories['calisma_yontemi'],  # Görüşme şekli
            'ozet': form_data.get('aciklama', '')
        }
        
        # Birden fazla öğrenci varsa her biri için ayrı kayıt oluştur
        results = []
        success_count = 0
        error_messages = []
        
        if form_data.get('ogrenciler') and len(form_data.get('ogrenciler')) > 0:
            for ogrenci in form_data.get('ogrenciler'):
                try:
                    # Her öğrenci için kayıt oluştur
                    result = GorusmeService.create_gorusme_kaydi(
                        ogrenci_id=ogrenci['id'],
                        **common_data
                    )
                    results.append(result)
                    
                    if result['success']:
                        success_count += 1
                    else:
                        error_messages.append(f"{ogrenci.get('ad_soyad', 'Öğrenci')} için: {result['message']}")
                        
                except Exception as e:
                    error_messages.append(f"{ogrenci.get('ad_soyad', 'Öğrenci')} için hata: {str(e)}")
        else:
            # Öğrenci olmadan kayıt oluştur (veli görüşmesi vb. durumlar için)
            result = GorusmeService.create_gorusme_kaydi(
                ogrenci_id=None,
                **common_data
            )
            results.append(result)
            
            if result['success']:
                success_count += 1
            else:
                error_messages.append(result['message'])
        
        # Sonuçları değerlendir
        total_count = len(results)
        
        if success_count == total_count:
            return jsonify({
                'success': True,
                'message': f"{success_count} görüşme kaydı başarıyla oluşturuldu."
            })
        elif success_count > 0:
            return jsonify({
                'success': True,
                'message': f"{success_count}/{total_count} görüşme kaydı oluşturuldu. Bazı kayıtlar hatalı: {'; '.join(error_messages)}"
            })
        else:
            return jsonify({
                'success': False,
                'message': f"Görüşme kayıtları oluşturulamadı: {'; '.join(error_messages)}"
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Görüşme kaydı oluşturulurken bir hata oluştu: {str(e)}'
        }), 500