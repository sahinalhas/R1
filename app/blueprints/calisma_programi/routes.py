from flask import render_template, redirect, url_for, request, flash, jsonify
from datetime import datetime, time, timedelta
from sqlalchemy import or_, func

from app.extensions import db
from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from app.blueprints.ders_konu_yonetimi.models import Ders, Konu
from app.blueprints.calisma_programi.models import DersProgrami, DersIlerleme, KonuTakip
from app.utils.program import generate_weekly_schedule, calculate_topic_schedule
from app.blueprints.calisma_programi.services import ProgramService
from app.utils.session import set_aktif_ogrenci, get_aktif_ogrenci
from app.utils.auth import session_required, log_activity
from app.blueprints.calisma_programi import calisma_programi_bp


@calisma_programi_bp.route('/ogrenci/<int:ogrenci_id>/haftalik-plan', methods=['GET', 'POST'])
@session_required
@log_activity('haftalik_plan_goruntule', 'Öğrencinin haftalık ders planı görüntülendi')
def haftalik_plan(ogrenci_id):
    """Öğrencinin haftalık ders planını görüntüleme ve düzenleme"""
    ogrenci = Ogrenci.query.get_or_404(ogrenci_id)
    
    # Mevcut aktif öğrenciyi oturumda ayarla
    set_aktif_ogrenci(ogrenci_id)
    
    dersler = Ders.query.order_by(Ders.ad).all()
    
    if request.method == 'POST':
        # Program temizleme butonu tıklandığında
        if 'temizle' in request.form:
            # Servis katmanını kullanarak programı temizle
            result = ProgramService.clear_program(ogrenci_id)
            
            if result['status'] == 'success':
                flash('Ders programı başarıyla temizlendi.', 'success')
            else:
                flash(f'Programı temizlerken bir hata oluştu: {result.get("message")}', 'danger')
            return redirect(url_for('calisma_programi.haftalik_plan', ogrenci_id=ogrenci_id))
        
        # Normal kaydetme işlemi için önce mevcut programı temizle
        clear_result = ProgramService.clear_program(ogrenci_id)
        if clear_result['status'] != 'success':
            flash(f'Programı güncellerken bir hata oluştu: {clear_result.get("message")}', 'danger')
            return redirect(url_for('calisma_programi.haftalik_plan', ogrenci_id=ogrenci_id))
        
        # Formdan gelen verileri işle ve yeni programı ekle
        for key, value in request.form.items():
            if key.startswith('ders_') and value:
                try:
                    # Format: ders_gun_saat (ders_0_7 = Pazartesi 7:00-7:30)
                    parts = key.split('_')
                    if len(parts) != 3:
                        continue
                    
                    gun = int(parts[1])
                    saat_baslangic = int(parts[2])
                    ders_id = int(value)
                    
                    # Saat nesnelerini oluştur (indeks 0 = saat 8:00'dan başlıyor)
                    saat_baslangic_saat = 8 + (saat_baslangic // 2)
                    saat_baslangic_dakika = 0 if saat_baslangic % 2 == 0 else 30
                    saat_bitis_saat = saat_baslangic_saat
                    saat_bitis_dakika = 30 if saat_baslangic % 2 == 0 else 0
                    if saat_bitis_dakika == 0:
                        saat_bitis_saat += 1
                    
                    # Saat formatları
                    start = f"{saat_baslangic_saat:02d}:{saat_baslangic_dakika:02d}"
                    end = f"{saat_bitis_saat:02d}:{saat_bitis_dakika:02d}"
                    
                    # Servis katmanını kullanarak yeni program kaydı ekle
                    ProgramService.add_program_event(ogrenci_id, ders_id, gun, start, end)
                except (ValueError, TypeError) as e:
                    flash(f'Ders programı kaydedilirken bir hata oluştu: {str(e)}', 'danger')
                    return redirect(url_for('calisma_programi.haftalik_plan', ogrenci_id=ogrenci_id))
        
        # Komşu aynı ders saatlerini birleştir
        ProgramService.merge_adjacent_lessons(ogrenci_id)
        
        # Öğrencinin konu ilerlemelerini güncelle
        ProgramService.update_topic_progress(ogrenci_id)
        
        flash('Ders programı başarıyla kaydedildi.', 'success')
        return redirect(url_for('calisma_programi.haftalik_plan', ogrenci_id=ogrenci_id))
    
    # Programı görüntüle - Birleştirilmiş bloklar halinde
    program_verisi = generate_weekly_schedule(ogrenci_id)
    
    # Ders bloklarını hazırla (tam blok görünümü için)
    ders_bloklari = []
    
    # Tüm dersleri al
    tum_dersler = {d.id: d.ad for d in Ders.query.all()}
    
    # Veritabanından program verilerini çek (birleştirilmiş bloklar)
    program_dersleri = DersProgrami.query.filter_by(ogrenci_id=ogrenci_id).order_by(
        DersProgrami.gun, DersProgrami.baslangic_saat
    ).all()
    
    # Ders bloklarını uygun formatta hazırla
    for ders in program_dersleri:
        # Başlangıç ve bitiş saatlerini dakika cinsinden hesapla (00:00'dan itibaren)
        baslangic_dakika = ders.baslangic_saat.hour * 60 + ders.baslangic_saat.minute
        bitis_dakika = ders.bitis_saat.hour * 60 + ders.bitis_saat.minute
        
        # 8:00'dan başladığımız için çıkarma yap (480 dakika = 8 saat)
        baslangic_index = (baslangic_dakika - 480) // 30
        bitis_index = (bitis_dakika - 480) // 30 - 1  # bitiş dahil edilmediği için -1
        
        # Ders adını al
        ders_adi = tum_dersler.get(ders.ders_id, "Bilinmeyen Ders")
        
        # Renk indeksi - sabit renk indeksi için ders id'si kullanıyoruz
        # Aynı ders hep aynı renkte olmalı (haftalik_plan.html'de de ders_id % 10 kullanıyoruz)
        renk_index = ders.ders_id % 10 if ders.ders_id else 0
        
        ders_bloklari.append({
            'gun': ders.gun,
            'baslangic_index': baslangic_index,
            'bitis_index': bitis_index,
            'ders_id': ders.ders_id,
            'ders_adi': ders_adi,
            'baslangic_saat': ders.baslangic_saat.strftime('%H:%M'),
            'bitis_saat': ders.bitis_saat.strftime('%H:%M'),
            'sure_dakika': (bitis_dakika - baslangic_dakika),
            'renk_index': renk_index
        })
    
    # Haftanın günleri
    gunler = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
    
    # Saat aralıkları (8:00'dan 24:00'e kadar, yarım saatlik dilimlerle)
    saat_araliklari = []
    for saat in range(8, 24):  # 8:00'dan 24:00'e kadar
        saat_araliklari.append((saat, 0))  # XX:00
        saat_araliklari.append((saat, 30))  # XX:30
    
    # Yeni modern tasarımla takvimi göster
    return render_template('calisma_programi/haftalik_plan_new.html', 
                          ogrenci=ogrenci,
                          dersler=dersler,
                          ders_bloklari=ders_bloklari,
                          gunler=gunler,
                          saat_araliklari=saat_araliklari)


@calisma_programi_bp.route('/ogrenci/<int:ogrenci_id>/konu-plani')
@session_required
@log_activity('konu_plani_goruntule', 'Öğrencinin konu bazlı çalışma planı görüntülendi')
def konu_plani(ogrenci_id):
    """Öğrencinin konu bazlı çalışma planını görüntüleme"""
    ogrenci = Ogrenci.query.get_or_404(ogrenci_id)
    
    # Mevcut aktif öğrenciyi oturumda ayarla
    set_aktif_ogrenci(ogrenci_id)
    
    # Konu planını hesapla
    konu_plani_string = calculate_topic_schedule(ogrenci_id)
    
    # Dersleri al
    dersler = Ders.query.order_by(Ders.ad).all()
    
    # Gün adları listesi
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    
    # String günleri int indexlere dönüştür (düzeltme)
    konu_plani = {}
    for gun_str, gunluk_plan in konu_plani_string.items():
        gun_index = int(gun_str)
        konu_plani[gun_index] = gunluk_plan
    
    return render_template('calisma_programi/konu_plani.html', 
                          ogrenci=ogrenci, 
                          konu_plani=konu_plani,
                          dersler=dersler,
                          gunler=gunler)


@calisma_programi_bp.route('/ogrenci/<int:ogrenci_id>/konu-takip', methods=['GET', 'POST'])
@session_required
@log_activity('konu_takip', 'Öğrencinin konu takibi görüntülendi veya güncellendi')
def konu_takip(ogrenci_id):
    """Öğrencinin konu takiplerini görüntüleme ve güncelleme"""
    ogrenci = Ogrenci.query.get_or_404(ogrenci_id)
    
    # POST işlemi: Konu takip güncelleme
    if request.method == 'POST':
        print("DEBUG: Konu takip formu POST edildi")
        
        # Form verilerini yazdır
        print("DEBUG: Form verileri:", request.form)
        
        konu_takipleri = {}
        
        # Önce tüm konu ID'lerini al - her bir konu için en az bir alan formdadır
        unique_konu_ids = set()
        for key in request.form.keys():
            if key.startswith('konu_'):
                parts = key.split('_')
                if len(parts) == 3:
                    unique_konu_ids.add(int(parts[1]))

        print(f"DEBUG: Benzersiz konu ID'leri: {unique_konu_ids}")
        
        # Her konu için girdileri işle
        for konu_id in unique_konu_ids:
            konu_takipleri[konu_id] = {
                'tamamlandi': False,  # Varsayılan değer
                'cozulen_soru': 0,    # Varsayılan değer
                'dogru_soru': 0       # Varsayılan değer
            }
            
            # Tamamlandı durumu
            tamamlandi_key = f'konu_{konu_id}_tamamlandi'
            if tamamlandi_key in request.form:
                konu_takipleri[konu_id]['tamamlandi'] = True
            
            # Çözülen soru sayısı
            cozulen_key = f'konu_{konu_id}_cozulen_soru'
            if cozulen_key in request.form and request.form[cozulen_key]:
                try:
                    cozulen_soru = int(request.form[cozulen_key])
                    konu_takipleri[konu_id]['cozulen_soru'] = cozulen_soru
                except ValueError:
                    pass  # Dönüşüm başarısız olursa varsayılan değer kullan
            
            # Doğru soru sayısı
            dogru_key = f'konu_{konu_id}_dogru_soru'
            if dogru_key in request.form and request.form[dogru_key]:
                try:
                    dogru_soru = int(request.form[dogru_key])
                    # Doğru sayısı çözülen sayıdan fazla olmamalı
                    max_dogru = konu_takipleri[konu_id]['cozulen_soru']
                    konu_takipleri[konu_id]['dogru_soru'] = min(dogru_soru, max_dogru)
                except ValueError:
                    pass  # Dönüşüm başarısız olursa varsayılan değer kullan
        
        print(f"DEBUG: İşlenmiş konu takipleri: {konu_takipleri}")
        
        # Değerleri görelim
        for konu_id, data in konu_takipleri.items():
            print(f"DEBUG: Konu {konu_id}: tamamlandi={data['tamamlandi']}, "
                  f"cozulen={data['cozulen_soru']}, dogru={data['dogru_soru']}")
        
        try:
            # Servis katmanını kullanarak konu takiplerini güncelle
            update_result = ProgramService.update_topic_tracking(ogrenci_id, konu_takipleri)
            
            # Ders ilerleme yüzdelerini güncelle
            progress_result = ProgramService.calculate_lesson_progress(ogrenci_id)
            
            if update_result['status'] == 'success' and progress_result['status'] == 'success':
                flash('Konu takip bilgileri güncellenmiştir.', 'success')
            else:
                # Hata durumunda kullanıcıya bilgi ver
                error_message = update_result.get('message') if update_result['status'] == 'error' else progress_result.get('message')
                flash(f'Konu takibi güncellenirken bir hata oluştu: {error_message}', 'danger')
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f'Konu takibi güncellenirken beklenmeyen bir hata oluştu: {str(e)}', 'danger')
            
        return redirect(url_for('calisma_programi.konu_takip', ogrenci_id=ogrenci_id))
    
    # GET işlemi: Konu takip sayfasını görüntüle
    
    # Filtreleme parametrelerini al
    ders_id = request.args.get('ders_id', type=int)
    # Varsayılan filtre olarak "tüm" konuları göster
    durum = request.args.get('durum', None)
    
    # Öğrenciye atanan dersleri ve tüm dersleri almak için
    # 1. Öğrencinin programındaki dersleri al
    ogrenci_ders_ids = db.session.query(DersProgrami.ders_id)\
        .filter(DersProgrami.ogrenci_id == ogrenci_id)\
        .distinct().all()
    ogrenci_ders_ids = [ders_id for (ders_id,) in ogrenci_ders_ids]  # Tuple içinden ders_id'leri çıkar
    
    # 2. Öğrencinin derslerini al
    dersler = Ders.query.filter(Ders.id.in_(ogrenci_ders_ids)).order_by(Ders.ad).all()
    
    # Temel konu sorgusu - sadece öğrencinin derslerindeki konuları göster
    konu_query = Konu.query.join(Ders).filter(Konu.ders_id.in_(ogrenci_ders_ids))
    
    # Ders filtresi
    if ders_id:
        # Seçilen ders öğrencinin derslerinde var mı kontrol et
        if ders_id in ogrenci_ders_ids:
            konu_query = konu_query.filter(Konu.ders_id == ders_id)
        else:
            # Eğer seçilen ders öğrenciye atanmamışsa, uyarı göster
            flash(f"Seçilen ders öğrencinin programında bulunmuyor.", "warning")
            return redirect(url_for('calisma_programi.konu_takip', ogrenci_id=ogrenci_id))
    
    # Konuları al
    konular = konu_query.order_by(Ders.ad, Konu.sira).all()
    
    # Öğrencinin konu takiplerini al
    takipler = {kt.konu_id: kt for kt in KonuTakip.query.filter_by(ogrenci_id=ogrenci_id).all()}
    
    # Durum filtresini uygula (takip kayıtlarını filtrele)
    filtered_konular = []
    for konu in konular:
        takip = takipler.get(konu.id)
        
        if durum == 'tamamlanan' and (not takip or not takip.tamamlandi):
            continue
        elif durum == 'tamamlanmayan' and takip and takip.tamamlandi:
            continue
        
        filtered_konular.append(konu)
    
    # Sadece öğrenciye atanan dersleri al
    tum_dersler = {d.id: d for d in dersler}
    
    # İstatistikleri hesapla - sadece öğrencinin derslerindeki konular için
    toplam_konular = len(konular)
    tamamlanan_konular = 0
    cozulen_sorular = 0
    dogru_sorular = 0
    
    # Öğrencinin tüm konu takipleri üzerinde döngü
    for konu_id, takip in takipler.items():
        # Sadece öğrencinin ders programındaki derslere ait konuları say
        konu = db.session.query(Konu).get(konu_id)
        if konu and konu.ders_id in ogrenci_ders_ids:
            if takip.tamamlandi:
                tamamlanan_konular += 1
            cozulen_sorular += takip.cozulen_soru or 0
            dogru_sorular += takip.dogru_soru or 0
            
    # Debug için yazdıralım
    print(f"DEBUG: İstatistikler - Toplam: {toplam_konular}, Tamamlanan: {tamamlanan_konular}, "
          f"Çözülen sorular: {cozulen_sorular}, Doğru sorular: {dogru_sorular}")
    
    # Konuları derslere göre grupla
    ders_konulari = {}
    for konu in filtered_konular:
        if konu.ders_id not in ders_konulari:
            ders_konulari[konu.ders_id] = {
                'ders': tum_dersler.get(konu.ders_id),
                'konular': []
            }
        
        # Her konu için takip bilgisini de ekle
        takip = takipler.get(konu.id, KonuTakip(ogrenci_id=ogrenci_id, konu_id=konu.id))
        ders_konulari[konu.ders_id]['konular'].append({
            'konu': konu,
            'takip': takip
        })
    
    return render_template('calisma_programi/konu_takip_fixed.html', 
                          ogrenci=ogrenci, 
                          ders_konulari=ders_konulari,
                          dersler=dersler,
                          secili_ders_id=ders_id,
                          secili_durum=durum,
                          # Ek olarak hesaplanan istatistikleri gönder
                          toplam_konular=toplam_konular,
                          tamamlanan_konular=tamamlanan_konular,
                          cozulen_sorular=cozulen_sorular,
                          dogru_sorular=dogru_sorular)


# API endpointleri program/routes_api.py dosyasına taşınmıştır