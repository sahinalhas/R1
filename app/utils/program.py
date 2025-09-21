from datetime import time
# Gereken modelleri doğrudan app.extensions'dan import ediyoruz
from app.extensions import db

def generate_weekly_schedule(ogrenci_id):
    """Öğrenci için haftalık ders programı veri yapısı oluştur"""
    # Modelleri yükle - uygulamanın başlatılmış olması gerekiyor
    from app.blueprints.calisma_programi.models import DersProgrami
    from app.blueprints.ders_konu_yonetimi.models import Ders
    
    # Öğrencinin ders programını al
    ders_programi = DersProgrami.query.filter_by(ogrenci_id=ogrenci_id).order_by(
        DersProgrami.gun, DersProgrami.baslangic_saat).all()
    
    # Tüm dersleri al ve sözlüğe koy
    dersler = {d.id: d.ad for d in Ders.query.all()}
    
    # Programı günlere göre grupla
    program = {str(gun): [] for gun in range(7)}
    
    for dp in ders_programi:
        # Time nesnelerini string formatına dönüştür
        baslangic_str = dp.baslangic_saat.strftime('%H:%M')
        bitis_str = dp.bitis_saat.strftime('%H:%M')
        
        # Ders adını sözlükten al
        ders_adi = dersler.get(dp.ders_id, f"Ders-{dp.ders_id}")
        
        program[str(dp.gun)].append({
            'ders_id': dp.ders_id,
            'ders_adi': ders_adi,
            'baslangic': baslangic_str,
            'bitis': bitis_str,
            'sure': dp.sure_dakika()
        })
    
    return program

def calculate_topic_schedule(ogrenci_id):
    """Öğrenci için konu bazlı çalışma planı hesapla"""
    # Modelleri yükle - uygulamanın başlatılmış olması gerekiyor
    from app.blueprints.calisma_programi.models import DersProgrami, KonuTakip
    from app.blueprints.ders_konu_yonetimi.models import Ders, Konu
    
    # Öğrencinin haftalık ders programını al
    haftalik_program = generate_weekly_schedule(ogrenci_id)
    
    # Her ders için sıradaki konuları ve kalan süreleri takip et
    ders_konu_takip = {}
    
    # Tüm derslerin konularını al ve sıradaki konuyu belirle
    tum_dersler = set([dp.ders_id for dp in DersProgrami.query.filter_by(ogrenci_id=ogrenci_id).all()])
    
    for ders_id in tum_dersler:
        # Dersin tüm konularını sırayla al
        konular = Konu.query.filter_by(ders_id=ders_id).order_by(Konu.sira).all()
        
        if not konular:
            continue
        
        # Öğrencinin bu dersteki konu takiplerini al
        konu_takipleri = {kt.konu_id: kt for kt in KonuTakip.query.filter_by(
            ogrenci_id=ogrenci_id).filter(KonuTakip.konu_id.in_([k.id for k in konular])).all()}
        
        # İlk tamamlanmamış konuyu bul
        siradaki_konu_index = 0
        kalan_sure = 0
        
        for i, konu in enumerate(konular):
            kt = konu_takipleri.get(konu.id)
            
            # Eğer konu takibi yoksa veya tamamlanmadıysa
            if not kt or not kt.tamamlandi:
                siradaki_konu_index = i
                # Kalan süreyi hesapla
                if kt:
                    kalan_sure = max(0, konu.tahmini_sure - kt.calisilan_sure)
                else:
                    kalan_sure = konu.tahmini_sure
                break
        
        ders_konu_takip[ders_id] = {
            'konular': konular,
            'siradaki_index': siradaki_konu_index,
            'kalan_sure': kalan_sure
        }
    
    # Konu bazlı plan için veri yapısı
    konu_plani = {}
    
    # Her gün için
    for gun in range(7):
        gun_str = str(gun)
        konu_plani[gun_str] = []
        
        # Bu günün ders programı
        if gun_str not in haftalik_program:
            continue
            
        gun_programi = haftalik_program[gun_str]
        
        for ders_bilgi in gun_programi:
            ders_id = ders_bilgi['ders_id']
            ders = Ders.query.get(ders_id)
            
            # Saat string'lerini parçala
            baslangic_str = ders_bilgi['baslangic']
            baslangic_saat, baslangic_dakika = map(int, baslangic_str.split(':'))
            
            sure = ders_bilgi['sure']
            
            # Bu dersin konu takip bilgilerini al
            konu_takip = ders_konu_takip.get(ders_id)
            if not konu_takip:
                continue
            
            # Bu ders bloğunda çalışılacak konuları hesapla
            blok_konulari = []
            kalan_dakika = sure
            
            while kalan_dakika > 0 and konu_takip['siradaki_index'] < len(konu_takip['konular']):
                siradaki_konu = konu_takip['konular'][konu_takip['siradaki_index']]
                konu_kalan_sure = konu_takip['kalan_sure']
                
                # Bu ders bloğunda çalışılacak süre
                calisma_suresi = min(kalan_dakika, konu_kalan_sure)
                
                # Konuyu ekle
                blok_konulari.append({
                    'konu': siradaki_konu,
                    'sure': calisma_suresi
                })
                
                # Kalan süreleri güncelle
                kalan_dakika -= calisma_suresi
                konu_takip['kalan_sure'] -= calisma_suresi
                
                # Konu bittiyse bir sonraki konuya geç
                if konu_takip['kalan_sure'] <= 0:
                    konu_takip['siradaki_index'] += 1
                    if konu_takip['siradaki_index'] < len(konu_takip['konular']):
                        sonraki_konu = konu_takip['konular'][konu_takip['siradaki_index']]
                        konu_takip['kalan_sure'] = sonraki_konu.tahmini_sure
            
            # Ders bloğu için toplam dakika
            toplam_dakika = baslangic_saat * 60 + baslangic_dakika
            
            # Konuları, her biri için başlangıç ve bitiş saatleriyle birlikte ekle
            for i, blok_konu in enumerate(blok_konulari):
                baslangic_dakika_toplam = toplam_dakika
                bitis_dakika_toplam = toplam_dakika + blok_konu['sure']
                
                # Saat formatına dönüştür
                baslangic_str = f"{baslangic_dakika_toplam // 60:02d}:{baslangic_dakika_toplam % 60:02d}"
                bitis_str = f"{bitis_dakika_toplam // 60:02d}:{bitis_dakika_toplam % 60:02d}"
                
                konu_plani[gun_str].append({
                    'ders_id': ders.id,
                    'ders_adi': ders.ad,
                    'konu_id': blok_konu['konu'].id,
                    'konu_adi': blok_konu['konu'].ad,
                    'baslangic': baslangic_str,
                    'bitis': bitis_str,
                    'sure': blok_konu['sure']
                })
                
                # Bir sonraki konunun başlangıç dakikası
                toplam_dakika = bitis_dakika_toplam
    
    return konu_plani