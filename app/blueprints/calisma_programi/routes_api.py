"""
API endpoint'leri için routes modülü
Haftalık ders programı ve konu takibi için API endpoint'leri burada tanımlanır
"""

from flask import request, jsonify
from datetime import datetime
from app.extensions import db

from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from app.blueprints.ders_konu_yonetimi.models import Ders, Konu
from app.blueprints.calisma_programi.models import KonuTakip
from app.blueprints.calisma_programi.services import ProgramService
from app.blueprints.calisma_programi import calisma_programi_bp


@calisma_programi_bp.route('/<int:ogrenci_id>/api/haftalik-plan', methods=['GET'])
def api_get_haftalik_plan(ogrenci_id):
    """Öğrenci haftalık ders planını FullCalendar formatında getir (GET)"""
    # Öğrenci kontrolü
    ogrenci = Ogrenci.query.get_or_404(ogrenci_id)
    
    # Servis katmanını kullanarak takvim etkinliklerini al
    events = ProgramService.get_calendar_events(ogrenci_id)
    
    return jsonify(events)


@calisma_programi_bp.route('/<int:ogrenci_id>/api/haftalik-plan', methods=['POST'])
def api_guncelle_haftalik_plan(ogrenci_id):
    """Öğrencinin haftalık ders planını güncelle (POST)"""
    # Yetkisiz erişimi kontrol et
    ogrenci = Ogrenci.query.get_or_404(ogrenci_id)
    
    # JSON verisini al
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'Geçersiz veri formatı'}), 400
    
    try:
        action = data.get('action')
        
        # Yeni etkinlik ekleme
        if action == 'add':
            ders_id = data.get('ders_id')
            gun = data.get('gun')
            start = data.get('start')
            end = data.get('end')
            
            # Servis katmanını kullanarak etkinlik ekle
            result = ProgramService.add_program_event(ogrenci_id, ders_id, gun, start, end)
            
            # Standart yanıt formatı
            if result.get('status') == 'error':
                return jsonify(result), 400
            return jsonify(result)
        
        # Etkinlik güncelleme
        elif action == 'update':
            program_id = data.get('id')
            gun = data.get('gun')
            start = data.get('start')
            end = data.get('end')
            
            # Servis katmanını kullanarak etkinlik güncelle
            result = ProgramService.update_program_event(ogrenci_id, program_id, gun, start, end)
            
            # Standart yanıt formatı
            if result.get('status') == 'error':
                return jsonify(result), 400
            return jsonify(result)
        
        # Etkinlik silme
        elif action == 'delete':
            program_id = data.get('id')
            
            # Servis katmanını kullanarak etkinlik sil
            result = ProgramService.delete_program_event(ogrenci_id, program_id)
            
            # Standart yanıt formatı
            if result.get('status') == 'error':
                return jsonify(result), 400
            return jsonify(result)
        
        # Tüm programı temizle
        elif action == 'clear':
            # Servis katmanını kullanarak programı temizle
            result = ProgramService.clear_program(ogrenci_id)
            
            # Standart yanıt formatı
            if result.get('status') == 'error':
                return jsonify(result), 400
            return jsonify(result)
        
        # Otomatik program oluştur
        elif action == 'auto_schedule':
            gunler = data.get('gunler', [])
            baslangic_saat = data.get('baslangic_saat')
            bitis_saat = data.get('bitis_saat')
            ders_suresi = data.get('ders_suresi', 45)
            mola_suresi = data.get('mola_suresi', 15)
            
            # Servis katmanını kullanarak otomatik program oluştur
            result = ProgramService.auto_create_schedule(
                ogrenci_id, gunler, baslangic_saat, bitis_saat, ders_suresi, mola_suresi
            )
            
            # Standart yanıt formatı
            if result.get('status') == 'error':
                return jsonify(result), 400
            return jsonify(result)
        
        # Tanımlanmamış işlem
        else:
            return jsonify({'status': 'error', 'message': 'Tanımlanmamış işlem'}), 400
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
        
        
@calisma_programi_bp.route('/ogrenci/<int:ogrenci_id>/calisma-tamamla', methods=['POST'])
def calisma_tamamla(ogrenci_id):
    """Konu planında gösterilen çalışmaları tamamlandı olarak işaretle
    
    Bu endpoint, öğrencinin konu planındaki konuları tamamlandı olarak işaretler.
    Konu takip tablosundaki çalışılan süreleri günceller ve gerekirse konuyu tamamlandı olarak işaretler.
    """
    # Öğrenci kontrolü
    ogrenci = Ogrenci.query.get_or_404(ogrenci_id)
    
    # JSON verisini al
    data = request.json
    if not data or 'konu_plani' not in data:
        return jsonify({'success': False, 'message': 'Geçersiz veri formatı'}), 400
        
    konu_plani = data.get('konu_plani', [])
    if not konu_plani:
        return jsonify({'success': False, 'message': 'Konu planı boş'}), 400
        
    try:
        # Güncellenecek konuları topla
        guncellenen_konular = 0
        tamamlanan_konular = 0
        
        for plan_item in konu_plani:
            konu_id = plan_item.get('konu_id')
            sure = plan_item.get('sure', 0)
            
            if not konu_id or sure <= 0:
                continue
                
            # Konuyu ve mevcut takip kaydını al
            konu = Konu.query.get(konu_id)
            if not konu:
                continue
                
            # Mevcut takip kaydını al veya oluştur
            takip = KonuTakip.query.filter_by(ogrenci_id=ogrenci_id, konu_id=konu_id).first()
            if not takip:
                # Yeni takip kaydı oluştur
                takip = KonuTakip(
                    ogrenci_id=ogrenci_id,
                    konu_id=konu_id,
                    calisilan_sure=0,
                    tamamlandi=False,
                    son_calisma_tarihi=datetime.now()
                )
                db.session.add(takip)
            
            # Çalışılan süreyi güncelle
            takip.calisilan_sure += sure
            takip.son_calisma_tarihi = datetime.now()
            
            # Konu tamamlandı mı kontrol et
            if takip.calisilan_sure >= konu.tahmini_sure:
                takip.tamamlandi = True
                tamamlanan_konular += 1
                
            guncellenen_konular += 1
        
        if guncellenen_konular > 0:
            db.session.commit()
            
            # Ders ilerleme yüzdelerini güncelle
            for plan_item in konu_plani:
                konu_id = plan_item.get('konu_id')
                if konu_id:
                    konu = Konu.query.get(konu_id)
                    if konu:
                        # İlgili dersin ilerleme bilgisini güncelle
                        ProgramService.update_ders_ilerleme(ogrenci_id, konu.ders_id)
            
            # Başarılı yanıt
            return jsonify({
                'success': True, 
                'message': f'Çalışma tamamlandı! {guncellenen_konular} konu güncellendi, {tamamlanan_konular} konu tamamlandı.'
            })
        else:
            return jsonify({'success': False, 'message': 'Güncellenecek konu bulunamadı'}), 404
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'İşlem sırasında hata oluştu: {str(e)}'}), 500