"""
Program işlemleri için servis modülü
Bu modül, program işlemleri ile ilgili iş mantığı işlemlerini gerçekleştirir.
"""
from datetime import datetime, timedelta
from sqlalchemy import func

from app.extensions import db
from app.blueprints.calisma_programi.models import DersProgrami, DersIlerleme, KonuTakip
from app.blueprints.ders_konu_yonetimi.models import Ders, Konu
from app.blueprints.ogrenci_yonetimi.models import Ogrenci

class CalismaService:
    """Çalışma ve ilerleme işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def get_tamamlanan_konu_sayisi():
        """
        Tüm öğrencilerin tamamladığı toplam konu sayısını getir
        
        Returns:
            int: Toplam tamamlanan konu sayısı
        """
        return KonuTakip.query.filter_by(tamamlandi=True).count()
    
    @staticmethod
    def get_ogrenci_tamamlanan_konu_sayisi(ogrenci_id):
        """
        Belirli bir öğrencinin tamamladığı toplam konu sayısını getir
        
        Args:
            ogrenci_id: Öğrenci ID
            
        Returns:
            int: Öğrencinin tamamladığı konu sayısı
        """
        return KonuTakip.query.filter_by(ogrenci_id=ogrenci_id, tamamlandi=True).count()

class ProgramService:
    """Program işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def update_topic_tracking(ogrenci_id, konu_takipleri):
        """
        Öğrencinin konu takiplerini toplu olarak güncelle
        
        Args:
            ogrenci_id: Öğrenci ID
            konu_takipleri: Konu takip bilgilerini içeren sözlük {konu_id: {tamamlandi, cozulen_soru, dogru_soru}}
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # Güncelleme yapılacak konuların ID'lerini al
            konu_ids = list(konu_takipleri.keys())
            
            # Önce tüm mevcut kayıtları bir seferde al
            mevcut_takipler = {takip.konu_id: takip for takip in 
                              KonuTakip.query.filter_by(ogrenci_id=ogrenci_id)
                              .filter(KonuTakip.konu_id.in_(konu_ids)).all()}
            
            # Tüm konu takiplerini güncelle
            for konu_id, takip_bilgisi in konu_takipleri.items():
                konu_id = int(konu_id)  # Emin olmak için int'e çevir
                
                # Mevcut takip kaydını kontrol et
                takip = mevcut_takipler.get(konu_id)
                
                if not takip:
                    # Yeni takip kaydı oluştur
                    takip = KonuTakip(
                        ogrenci_id=ogrenci_id,
                        konu_id=konu_id,
                        tamamlandi=takip_bilgisi.get('tamamlandi', False),
                        cozulen_soru=takip_bilgisi.get('cozulen_soru', 0),
                        dogru_soru=takip_bilgisi.get('dogru_soru', 0),
                        son_calisma_tarihi=datetime.now() if takip_bilgisi.get('tamamlandi', False) else None
                    )
                    db.session.add(takip)
                else:
                    # Mevcut takip kaydını güncelle
                    takip.tamamlandi = takip_bilgisi.get('tamamlandi', False)  # Varsayılan False
                    
                    # Çözülen soru sayısını güncelle
                    cozulen_soru = takip_bilgisi.get('cozulen_soru')
                    if cozulen_soru is not None:
                        takip.cozulen_soru = int(cozulen_soru)
                    
                    # Doğru soru sayısını güncelle
                    dogru_soru = takip_bilgisi.get('dogru_soru')
                    if dogru_soru is not None:
                        takip.dogru_soru = int(dogru_soru)
                    
                    # Tamamlandı işaretlendiyse son çalışma tarihini güncelle
                    if takip_bilgisi.get('tamamlandi', False) and not takip.son_calisma_tarihi:
                        takip.son_calisma_tarihi = datetime.now()
            
            db.session.commit()
            return {"status": "success", "message": "Konu takipleri başarıyla güncellendi"}
        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def calculate_lesson_progress(ogrenci_id):
        """
        Öğrencinin ders ilerleme durumlarını konu takip bilgilerine göre hesapla
        
        Args:
            ogrenci_id: Öğrenci ID
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # Öğrencinin takip ettiği konuları al
            konu_takipler = KonuTakip.query.filter_by(ogrenci_id=ogrenci_id).all()
            
            # Konu ID'lerini al
            konu_ids = [kt.konu_id for kt in konu_takipler]
            
            # Konulara ait dersleri bul
            konular = Konu.query.filter(Konu.id.in_(konu_ids)).all()
            
            # Her konu için ders ID'sini al
            ders_konu_map = {}
            for konu in konular:
                if konu.ders_id not in ders_konu_map:
                    ders_konu_map[konu.ders_id] = []
                ders_konu_map[konu.ders_id].append(konu.id)
            
            # Her ders için ilerleme hesapla
            for ders_id, konu_ids in ders_konu_map.items():
                # Derse ait toplam konu sayısı
                total_konular = Konu.query.filter_by(ders_id=ders_id).count()
                
                if total_konular == 0:
                    continue
                
                # Tamamlanan konu sayısı
                tamamlanan_konular = KonuTakip.query.filter(
                    KonuTakip.ogrenci_id == ogrenci_id,
                    KonuTakip.konu_id.in_(konu_ids),
                    KonuTakip.tamamlandi == True
                ).count()
                
                # İlerleme yüzdesi
                tamamlama_yuzdesi = (tamamlanan_konular / total_konular) * 100 if total_konular > 0 else 0
                
                # Ders ilerleme kaydını güncelle veya oluştur
                ilerleme = DersIlerleme.query.filter_by(ogrenci_id=ogrenci_id, ders_id=ders_id).first()
                
                if not ilerleme:
                    # Yeni ilerleme kaydı oluştur
                    ilerleme = DersIlerleme(
                        ogrenci_id=ogrenci_id,
                        ders_id=ders_id,
                        tamamlama_yuzdesi=tamamlama_yuzdesi
                    )
                    db.session.add(ilerleme)
                else:
                    # Mevcut ilerleme kaydını güncelle
                    ilerleme.tamamlama_yuzdesi = tamamlama_yuzdesi
                    ilerleme.son_guncelleme = datetime.now()
            
            db.session.commit()
            return {"status": "success", "message": "Ders ilerleme durumları güncellendi"}
        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def get_calendar_events(ogrenci_id):
        """
        Öğrenci haftalık ders planını FullCalendar formatında getir
        
        Args:
            ogrenci_id: Öğrenci ID
            
        Returns:
            List: Takvim etkinlikleri listesi
        """
        from app.blueprints.calisma_programi.models import DersProgrami
        from app.blueprints.ders_konu_yonetimi.models import Ders
        
        # Öğrencinin ders programını al
        programlar = DersProgrami.query.filter_by(ogrenci_id=ogrenci_id).all()
        
        # Ders adlarını sözlüğe yükle
        ders_adlari = {d.id: d.ad for d in Ders.query.all()}
        
        # Gün isimlerini tanımla
        gunler = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        
        # Renk sınıflarını tanımla (CSS sınıfları)
        renk_siniflari = ['bg-primary', 'bg-success', 'bg-info', 'bg-warning', 'bg-danger', 
                        'bg-pink', 'bg-purple', 'bg-indigo', 'bg-teal']
        
        # Renk paletini tanımla (HEX renk kodları - FullCalendar için)
        renk_paleti = [
            '#6200ea', '#e91e63', '#2e7d32', '#8e24aa', '#37474f',
            '#c2185b', '#f57c00', '#00897b', '#1565c0', '#512da8'
        ]
        
        # FullCalendar formatında olaylar listesi oluştur
        events = []
        
        for program in programlar:
            # Ders rengini ders_id'ye göre belirle
            renk_index = program.ders_id % len(renk_siniflari)
            renk_sinifi = renk_siniflari[renk_index]
            renk_kodu = renk_paleti[program.ders_id % len(renk_paleti)]
            
            # Ders adını getir, bulunamazsa ID'sini kullan
            ders_adi = ders_adlari.get(program.ders_id, f"Ders-{program.ders_id}")
            
            # Referans tarih olarak bu haftanın Pazartesi gününü al
            # Böylece takvim her zaman içinde bulunduğumuz haftayı gösterir
            simdi = datetime.now()
            # Haftanın ilk günü (Pazartesi) için referans tarih bul
            haftanin_pazartesi = simdi - timedelta(days=simdi.weekday())
            
            # Hedef günün tarihini hesapla
            # program.gun: 0=Pazartesi, 1=Salı, ..., 6=Pazar
            # weekday(): 0=Pazartesi, 1=Salı, ..., 6=Pazar
            hedef_tarih = haftanin_pazartesi + timedelta(days=program.gun)
            
            # Takvim formatı için string'e çevir
            tarih_str = hedef_tarih.strftime('%Y-%m-%d')
            
            # Event oluştur - Takvim için gerekli minimum veri yapısı
            event = {
                'id': f"ders_{program.id}",  # ID başına "ders_" ekleyerek tutarlılık sağla
                'title': ders_adi,
                'start': f"{tarih_str}T{program.baslangic_saat.strftime('%H:%M')}:00",
                'end': f"{tarih_str}T{program.bitis_saat.strftime('%H:%M')}:00",
                'className': renk_sinifi,     # CSS sınıfı için - daha uyumlu
                'display': 'block',           # Görünüm tipi
                
                # ExtendedProps üzerinden veri taşı, UI özelliklerini burada tutma
                'extendedProps': {
                    'ders_id': program.ders_id,
                    'gun': program.gun,
                    'gun_adi': gunler[program.gun],
                    'baslangic_saat': program.baslangic_saat.strftime('%H:%M'),
                    'bitis_saat': program.bitis_saat.strftime('%H:%M'),
                    'renk_index': renk_index   # Tutarlı renk kullanımı için
                }
            }
            
            # CSS ile stil vermeyi tercih edelim, ama FullCalendar API'si için güvenli şekilde
            # doğrudan stil renk özelliklerini de ekleyelim (ilave, fazlalık bilgi olarak)
            try:
                # Renk özellikleri ayrı ekleme - hata olursa atlanacak
                event['backgroundColor'] = renk_kodu
                event['borderColor'] = renk_kodu
                # color özelliği sorun çıkarıyor, kullanmayalım
                # event['color'] = renk_kodu
            except Exception:
                # Hata durumunda CSS class ile renklendirme kullan
                pass
            
            events.append(event)
        
        return events
        
    @staticmethod
    def add_program_event(ogrenci_id, ders_id, gun, start, end):
        """
        Programa yeni bir ders etkinliği ekle
        
        Args:
            ogrenci_id: Öğrenci ID
            ders_id: Ders ID
            gun: Gün (0-6 arası)
            start: Başlangıç saati
            end: Bitiş saati
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # Parametreleri doğrula
            if not all([ogrenci_id, ders_id, gun is not None, start, end]):
                return {'status': 'error', 'message': 'Eksik parametreler'}
            
            # Saat formatını doğrula
            try:
                if isinstance(start, str):
                    start_time = datetime.strptime(start, '%H:%M').time()
                if isinstance(end, str):
                    end_time = datetime.strptime(end, '%H:%M').time()
            except ValueError:
                return {'status': 'error', 'message': 'Geçersiz saat formatı'}
            
            # Yeni program oluştur
            result = ProgramService.create_ders_programi(ogrenci_id, ders_id, gun, start, end)
            
            if result.get('success', False):
                # Başarılı ise FullCalendar formatında bir cevap döndür
                return {
                    'status': 'success',
                    'message': result.get('message', 'Program eklendi'),
                    'data': {
                        'id': result.get('id'),
                        'ogrenci_id': ogrenci_id,
                        'ders_id': ders_id,
                        'gun': gun,
                        'start': start,
                        'end': end
                    }
                }
            else:
                return {'status': 'error', 'message': result.get('message', 'Bilinmeyen hata')}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def update_program_event(ogrenci_id, program_id, gun=None, start=None, end=None):
        """
        Mevcut bir program etkinliğini güncelle
        
        Args:
            ogrenci_id: Öğrenci ID
            program_id: Program ID
            gun: Gün (0-6 arası, opsiyonel)
            start: Başlangıç saati (opsiyonel)
            end: Bitiş saati (opsiyonel)
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # Program kaydını kontrol et
            program = DersProgrami.query.get(program_id)
            if not program or program.ogrenci_id != ogrenci_id:
                return {'status': 'error', 'message': 'Program bulunamadı veya yetkisiz erişim'}
            
            # Güncelleme işlemini yap
            result = ProgramService.update_ders_programi(program_id, 
                                                         gun if gun is not None else program.gun, 
                                                         start if start else program.baslangic_saat,
                                                         end if end else program.bitis_saat)
            
            if result.get('success', False):
                return {
                    'status': 'success',
                    'message': result.get('message', 'Program güncellendi'),
                    'data': {
                        'id': program_id,
                        'ogrenci_id': ogrenci_id,
                        'ders_id': program.ders_id,
                        'gun': gun if gun is not None else program.gun,
                        'start': start if start else program.baslangic_saat.strftime('%H:%M'),
                        'end': end if end else program.bitis_saat.strftime('%H:%M')
                    }
                }
            else:
                return {'status': 'error', 'message': result.get('message', 'Bilinmeyen hata')}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def delete_program_event(ogrenci_id, program_id):
        """
        Bir program etkinliğini sil
        
        Args:
            ogrenci_id: Öğrenci ID
            program_id: Program ID
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # Program kaydını kontrol et
            program = DersProgrami.query.get(program_id)
            if not program or program.ogrenci_id != ogrenci_id:
                return {'status': 'error', 'message': 'Program bulunamadı veya yetkisiz erişim'}
            
            # Silme işlemini yap
            result = ProgramService.delete_ders_programi(program_id)
            
            if result.get('success', False):
                return {
                    'status': 'success',
                    'message': result.get('message', 'Program silindi'),
                    'data': {
                        'id': program_id
                    }
                }
            else:
                return {'status': 'error', 'message': result.get('message', 'Bilinmeyen hata')}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def clear_program(ogrenci_id):
        """
        Öğrencinin tüm programını temizle
        
        Args:
            ogrenci_id: Öğrenci ID
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # Öğrencinin programlarını bul
            programlar = DersProgrami.query.filter_by(ogrenci_id=ogrenci_id).all()
            
            # Programları sil
            silinen_sayi = 0
            for program in programlar:
                db.session.delete(program)
                silinen_sayi += 1
            
            db.session.commit()
            
            return {
                'status': 'success',
                'message': f'Toplam {silinen_sayi} program kaydı silindi',
                'data': {
                    'silinen_sayi': silinen_sayi
                }
            }
                
        except Exception as e:
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def auto_create_schedule(ogrenci_id, gunler, baslangic_saat, bitis_saat, ders_suresi=45, mola_suresi=15):
        """
        Otomatik ders programı oluştur
        
        Args:
            ogrenci_id: Öğrenci ID
            gunler: Seçilen günler listesi
            baslangic_saat: Başlangıç saati
            bitis_saat: Bitiş saati
            ders_suresi: Ders süresi (dakika)
            mola_suresi: Mola süresi (dakika)
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # Önce mevcut programı temizle
            clear_result = ProgramService.clear_program(ogrenci_id)
            if clear_result.get('status') != 'success':
                return clear_result
            
            # Parametreleri doğrula
            if not all([ogrenci_id, gunler, baslangic_saat, bitis_saat]):
                return {'status': 'error', 'message': 'Eksik parametreler'}
            
            # Saat formatını doğrula
            try:
                if isinstance(baslangic_saat, str):
                    baslangic_saat = datetime.strptime(baslangic_saat, '%H:%M').time()
                if isinstance(bitis_saat, str):
                    bitis_saat = datetime.strptime(bitis_saat, '%H:%M').time()
            except ValueError:
                return {'status': 'error', 'message': 'Geçersiz saat formatı'}
            
            # Başlangıç saati bitiş saatinden önce olmalı
            if baslangic_saat >= bitis_saat:
                return {'status': 'error', 'message': 'Başlangıç saati bitiş saatinden önce olmalıdır'}
            
            # Günleri doğrula
            try:
                gunler = [int(gun) for gun in gunler]
                for gun in gunler:
                    if gun < 0 or gun > 6:
                        return {'status': 'error', 'message': 'Geçersiz gün değerleri'}
            except:
                return {'status': 'error', 'message': 'Geçersiz gün formatı'}
                
            # Tüm dersleri getir
            dersler = Ders.query.all()
            if not dersler:
                return {'status': 'error', 'message': 'Hiç ders bulunamadı'}
            
            # Toplam dakikaları hesapla
            baslangic_dakika = baslangic_saat.hour * 60 + baslangic_saat.minute
            bitis_dakika = bitis_saat.hour * 60 + bitis_saat.minute
            toplam_dakika = bitis_dakika - baslangic_dakika
            
            # Ders ve mola toplam süresi
            ders_mola_suresi = ders_suresi + mola_suresi
            
            # Bir günde kaç blok olabilir
            blok_sayisi = toplam_dakika // ders_mola_suresi
            if blok_sayisi <= 0:
                return {'status': 'error', 'message': 'Seçilen saat aralığı çok kısa'}
            
            # Ders sayısı ve her dersin planlanma sayısı
            ders_sayisi = len(dersler)
            ders_planlama_sayisi = (blok_sayisi * len(gunler)) // ders_sayisi
            
            if ders_planlama_sayisi < 1:
                ders_planlama_sayisi = 1
            
            # Günler arası dengeli dağıtım için
            ders_indeks = 0
            eklenen_programlar = []
            
            # Her gün için
            for gun in gunler:
                # O günün blokları için
                for blok in range(blok_sayisi):
                    # Ders seç
                    ders = dersler[ders_indeks % ders_sayisi]
                    ders_indeks += 1
                    
                    # Zaman hesapla
                    blok_baslangic_dakika = baslangic_dakika + (blok * ders_mola_suresi)
                    blok_bitis_dakika = blok_baslangic_dakika + ders_suresi
                    
                    # Saat formatına dönüştür
                    blok_baslangic_saat = f"{blok_baslangic_dakika // 60:02d}:{blok_baslangic_dakika % 60:02d}"
                    blok_bitis_saat = f"{blok_bitis_dakika // 60:02d}:{blok_bitis_dakika % 60:02d}"
                    
                    # Program ekle
                    result = ProgramService.create_ders_programi(
                        ogrenci_id, ders.id, gun, blok_baslangic_saat, blok_bitis_saat
                    )
                    
                    if result.get('success', False):
                        eklenen_programlar.append({
                            'id': result.get('id'),
                            'gun': gun,
                            'ders_id': ders.id,
                            'ders_adi': ders.ad,
                            'baslangic': blok_baslangic_saat,
                            'bitis': blok_bitis_saat
                        })
            
            return {
                'status': 'success',
                'message': f'Toplam {len(eklenen_programlar)} program kaydı oluşturuldu',
                'data': {
                    'programlar': eklenen_programlar
                }
            }
                
        except Exception as e:
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def get_ders_programi_by_ogrenci_id(ogrenci_id):
        """
        Öğrenciye ait ders programını getir
        
        Args:
            ogrenci_id: Öğrenci ID
            
        Returns:
            Ders programı listesi
        """
        return DersProgrami.query.filter_by(ogrenci_id=ogrenci_id).order_by(
            DersProgrami.gun, DersProgrami.baslangic_saat
        ).all()
    
    @staticmethod
    def get_ders_programi_by_id(program_id):
        """
        ID'ye göre ders programı getir
        
        Args:
            program_id: Program ID
            
        Returns:
            Ders programı nesnesi veya None
        """
        return DersProgrami.query.get(program_id)
    
    @staticmethod
    def create_ders_programi(ogrenci_id, ders_id, gun, baslangic_saat, bitis_saat):
        """
        Yeni ders programı oluştur
        
        Args:
            ogrenci_id: Öğrenci ID
            ders_id: Ders ID
            gun: Gün (0: Pazartesi, 1: Salı, ..., 6: Pazar)
            baslangic_saat: Başlangıç saati (HH:MM formatında)
            bitis_saat: Bitiş saati (HH:MM formatında)
            
        Returns:
            Dict: İşlem sonucunu ve oluşturulan program ID'sini içeren sözlük
        """
        # Öğrenci kontrolü
        ogrenci = Ogrenci.query.get(ogrenci_id)
        if not ogrenci:
            return {
                'success': False, 
                'message': 'Öğrenci bulunamadı.'
            }
        
        # Ders kontrolü
        ders = Ders.query.get(ders_id)
        if not ders:
            return {
                'success': False, 
                'message': 'Ders bulunamadı.'
            }
        
        # Saat formatı kontrolü ve çevirme
        try:
            if isinstance(baslangic_saat, str):
                baslangic_saat = datetime.strptime(baslangic_saat, '%H:%M').time()
            if isinstance(bitis_saat, str):
                bitis_saat = datetime.strptime(bitis_saat, '%H:%M').time()
        except ValueError:
            return {
                'success': False,
                'message': 'Saat formatı hatalı, HH:MM formatında olmalıdır.'
            }
        
        # Başlangıç saati bitiş saatinden önce olmalı
        if baslangic_saat >= bitis_saat:
            return {
                'success': False,
                'message': 'Başlangıç saati bitiş saatinden önce olmalıdır.'
            }
        
        # Gün kontrolü
        if gun < 0 or gun > 6:
            return {
                'success': False,
                'message': 'Geçersiz gün değeri. 0 (Pazartesi) ile 6 (Pazar) arasında olmalıdır.'
            }
        
        # Çakışma kontrolü
        cakisma = DersProgrami.query.filter_by(
            ogrenci_id=ogrenci_id, 
            gun=gun
        ).filter(
            ((DersProgrami.baslangic_saat <= baslangic_saat) & (DersProgrami.bitis_saat > baslangic_saat)) |
            ((DersProgrami.baslangic_saat < bitis_saat) & (DersProgrami.bitis_saat >= bitis_saat)) |
            ((DersProgrami.baslangic_saat >= baslangic_saat) & (DersProgrami.bitis_saat <= bitis_saat))
        ).first()
        
        if cakisma:
            ders_adi = Ders.query.get(cakisma.ders_id).ad
            return {
                'success': False,
                'message': f'Bu zaman diliminde çakışan bir program mevcut: {ders_adi}, {cakisma.baslangic_saat.strftime("%H:%M")}-{cakisma.bitis_saat.strftime("%H:%M")}'
            }
        
        # Yeni program oluştur
        program = DersProgrami(
            ogrenci_id=ogrenci_id,
            ders_id=ders_id,
            gun=gun,
            baslangic_saat=baslangic_saat,
            bitis_saat=bitis_saat
        )
        
        try:
            db.session.add(program)
            db.session.commit()
            return {
                'success': True,
                'message': 'Ders programı başarıyla eklendi.',
                'id': program.id
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def update_ders_programi(program_id, gun, baslangic_saat, bitis_saat):
        """
        Ders programını güncelle
        
        Args:
            program_id: Program ID
            gun: Gün (0: Pazartesi, 1: Salı, ..., 6: Pazar)
            baslangic_saat: Başlangıç saati (HH:MM formatında)
            bitis_saat: Bitiş saati (HH:MM formatında)
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        program = DersProgrami.query.get(program_id)
        if not program:
            return {
                'success': False,
                'message': 'Ders programı bulunamadı.'
            }
        
        # Saat formatı kontrolü ve çevirme
        try:
            if isinstance(baslangic_saat, str):
                baslangic_saat = datetime.strptime(baslangic_saat, '%H:%M').time()
            if isinstance(bitis_saat, str):
                bitis_saat = datetime.strptime(bitis_saat, '%H:%M').time()
        except ValueError:
            return {
                'success': False,
                'message': 'Saat formatı hatalı, HH:MM formatında olmalıdır.'
            }
        
        # Başlangıç saati bitiş saatinden önce olmalı
        if baslangic_saat >= bitis_saat:
            return {
                'success': False,
                'message': 'Başlangıç saati bitiş saatinden önce olmalıdır.'
            }
        
        # Gün kontrolü
        if gun < 0 or gun > 6:
            return {
                'success': False,
                'message': 'Geçersiz gün değeri. 0 (Pazartesi) ile 6 (Pazar) arasında olmalıdır.'
            }
        
        # Çakışma kontrolü (kendi hariç)
        cakisma = DersProgrami.query.filter_by(
            ogrenci_id=program.ogrenci_id, 
            gun=gun
        ).filter(
            DersProgrami.id != program_id
        ).filter(
            ((DersProgrami.baslangic_saat <= baslangic_saat) & (DersProgrami.bitis_saat > baslangic_saat)) |
            ((DersProgrami.baslangic_saat < bitis_saat) & (DersProgrami.bitis_saat >= bitis_saat)) |
            ((DersProgrami.baslangic_saat >= baslangic_saat) & (DersProgrami.bitis_saat <= bitis_saat))
        ).first()
        
        if cakisma:
            ders_adi = Ders.query.get(cakisma.ders_id).ad
            return {
                'success': False,
                'message': f'Bu zaman diliminde çakışan bir program mevcut: {ders_adi}, {cakisma.baslangic_saat.strftime("%H:%M")}-{cakisma.bitis_saat.strftime("%H:%M")}'
            }
        
        # Bilgileri güncelle
        program.gun = gun
        program.baslangic_saat = baslangic_saat
        program.bitis_saat = bitis_saat
        
        try:
            db.session.commit()
            return {
                'success': True,
                'message': 'Ders programı başarıyla güncellendi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def delete_ders_programi(program_id):
        """
        Ders programını sil
        
        Args:
            program_id: Program ID
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        program = DersProgrami.query.get(program_id)
        if not program:
            return {
                'success': False,
                'message': 'Ders programı bulunamadı.'
            }
        
        try:
            db.session.delete(program)
            db.session.commit()
            return {
                'success': True,
                'message': 'Ders programı başarıyla silindi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def get_konu_takip_by_ogrenci_id(ogrenci_id, ders_id=None):
        """
        Öğrenciye ait konu takip listesini getir
        
        Args:
            ogrenci_id: Öğrenci ID
            ders_id: Ders ID (opsiyonel, belirli bir derse filtreler)
            
        Returns:
            Konu takip listesi
        """
        query = KonuTakip.query.filter_by(ogrenci_id=ogrenci_id)
        
        if ders_id:
            # Belirli derse ait konuları filtrele
            konu_ids = [konu.id for konu in Konu.query.filter_by(ders_id=ders_id).all()]
            query = query.filter(KonuTakip.konu_id.in_(konu_ids))
        
        return query.all()
    
    @staticmethod
    def get_konu_takip_by_id(takip_id):
        """
        ID'ye göre konu takip getir
        
        Args:
            takip_id: Takip ID
            
        Returns:
            Konu takip nesnesi veya None
        """
        return KonuTakip.query.get(takip_id)
    
    @staticmethod
    def create_konu_takip(ogrenci_id, konu_id, tamamlandi=False, calisilan_sure=0, cozulen_soru=0, dogru_soru=0):
        """
        Yeni konu takip oluştur
        
        Args:
            ogrenci_id: Öğrenci ID
            konu_id: Konu ID
            tamamlandi: Tamamlanma durumu
            calisilan_sure: Çalışılan süre (dakika)
            cozulen_soru: Çözülen soru sayısı
            dogru_soru: Doğru çözülen soru sayısı
            
        Returns:
            Dict: İşlem sonucunu ve oluşturulan takip ID'sini içeren sözlük
        """
        # Öğrenci kontrolü
        ogrenci = Ogrenci.query.get(ogrenci_id)
        if not ogrenci:
            return {
                'success': False, 
                'message': 'Öğrenci bulunamadı.'
            }
        
        # Konu kontrolü
        konu = Konu.query.get(konu_id)
        if not konu:
            return {
                'success': False, 
                'message': 'Konu bulunamadı.'
            }
        
        # Zaten kayıt var mı kontrol et
        mevcut = KonuTakip.query.filter_by(ogrenci_id=ogrenci_id, konu_id=konu_id).first()
        if mevcut:
            return {
                'success': False,
                'message': 'Bu konu için takip kaydı zaten mevcut.'
            }
        
        # Yeni takip oluştur
        takip = KonuTakip(
            ogrenci_id=ogrenci_id,
            konu_id=konu_id,
            tamamlandi=tamamlandi,
            calisilan_sure=calisilan_sure,
            cozulen_soru=cozulen_soru,
            dogru_soru=dogru_soru,
            son_calisma_tarihi=datetime.now() if calisilan_sure > 0 or cozulen_soru > 0 else None
        )
        
        try:
            db.session.add(takip)
            db.session.commit()
            
            # Eğer konu takibi eklendiyse, ders ilerleme yüzdesini güncelle
            ders_id = konu.ders_id
            ProgramService.update_ders_ilerleme(ogrenci_id, ders_id)
            
            return {
                'success': True,
                'message': 'Konu takibi başarıyla eklendi.',
                'id': takip.id
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def update_konu_takip(takip_id, tamamlandi, calisilan_sure, cozulen_soru, dogru_soru):
        """
        Konu takip bilgilerini güncelle
        
        Args:
            takip_id: Takip ID
            tamamlandi: Tamamlanma durumu
            calisilan_sure: Çalışılan süre (dakika)
            cozulen_soru: Çözülen soru sayısı
            dogru_soru: Doğru çözülen soru sayısı
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        takip = KonuTakip.query.get(takip_id)
        if not takip:
            return {
                'success': False,
                'message': 'Konu takibi bulunamadı.'
            }
        
        # Doğru soru sayısı çözülen soru sayısından büyük olamaz
        if dogru_soru > cozulen_soru:
            return {
                'success': False,
                'message': 'Doğru soru sayısı çözülen soru sayısından büyük olamaz.'
            }
        
        # Bilgileri güncelle
        takip.tamamlandi = tamamlandi
        takip.calisilan_sure = calisilan_sure
        takip.cozulen_soru = cozulen_soru
        takip.dogru_soru = dogru_soru
        takip.son_calisma_tarihi = datetime.now()
        
        try:
            db.session.commit()
            
            # Konu takibi güncellendiğinde ders ilerleme yüzdesini güncelle
            konu = Konu.query.get(takip.konu_id)
            ders_id = konu.ders_id
            ProgramService.update_ders_ilerleme(takip.ogrenci_id, ders_id)
            
            return {
                'success': True,
                'message': 'Konu takibi başarıyla güncellendi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def delete_konu_takip(takip_id):
        """
        Konu takibini sil
        
        Args:
            takip_id: Takip ID
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        takip = KonuTakip.query.get(takip_id)
        if not takip:
            return {
                'success': False,
                'message': 'Konu takibi bulunamadı.'
            }
        
        try:
            ogrenci_id = takip.ogrenci_id
            konu = Konu.query.get(takip.konu_id)
            ders_id = konu.ders_id
            
            db.session.delete(takip)
            db.session.commit()
            
            # Konu takibi silindiğinde ders ilerleme yüzdesini güncelle
            ProgramService.update_ders_ilerleme(ogrenci_id, ders_id)
            
            return {
                'success': True,
                'message': 'Konu takibi başarıyla silindi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def get_ders_ilerleme_by_ogrenci_id(ogrenci_id):
        """
        Öğrenciye ait ders ilerleme listesini getir
        
        Args:
            ogrenci_id: Öğrenci ID
            
        Returns:
            Ders ilerleme listesi
        """
        return DersIlerleme.query.filter_by(ogrenci_id=ogrenci_id).all()
    
    @staticmethod
    def get_ders_ilerleme_by_id(ilerleme_id):
        """
        ID'ye göre ders ilerleme getir
        
        Args:
            ilerleme_id: İlerleme ID
            
        Returns:
            Ders ilerleme nesnesi veya None
        """
        return DersIlerleme.query.get(ilerleme_id)
    
    @staticmethod
    def create_ders_ilerleme(ogrenci_id, ders_id, tamamlama_yuzdesi, tahmini_bitis_tarihi=None):
        """
        Yeni ders ilerleme oluştur
        
        Args:
            ogrenci_id: Öğrenci ID
            ders_id: Ders ID
            tamamlama_yuzdesi: Tamamlama yüzdesi (0-100)
            tahmini_bitis_tarihi: Tahmini bitiş tarihi (opsiyonel)
            
        Returns:
            Dict: İşlem sonucunu ve oluşturulan ilerleme ID'sini içeren sözlük
        """
        # Öğrenci kontrolü
        ogrenci = Ogrenci.query.get(ogrenci_id)
        if not ogrenci:
            return {
                'success': False, 
                'message': 'Öğrenci bulunamadı.'
            }
        
        # Ders kontrolü
        ders = Ders.query.get(ders_id)
        if not ders:
            return {
                'success': False, 
                'message': 'Ders bulunamadı.'
            }
        
        # Yüzde kontrolü
        if tamamlama_yuzdesi < 0 or tamamlama_yuzdesi > 100:
            return {
                'success': False,
                'message': 'Tamamlama yüzdesi 0-100 arasında olmalıdır.'
            }
        
        # Zaten kayıt var mı kontrol et
        mevcut = DersIlerleme.query.filter_by(ogrenci_id=ogrenci_id, ders_id=ders_id).first()
        if mevcut:
            return {
                'success': False,
                'message': 'Bu ders için ilerleme kaydı zaten mevcut.'
            }
        
        # Yeni ilerleme oluştur
        ilerleme = DersIlerleme(
            ogrenci_id=ogrenci_id,
            ders_id=ders_id,
            tamamlama_yuzdesi=tamamlama_yuzdesi,
            tahmini_bitis_tarihi=tahmini_bitis_tarihi,
            son_guncelleme=datetime.now()
        )
        
        try:
            db.session.add(ilerleme)
            db.session.commit()
            return {
                'success': True,
                'message': 'Ders ilerlemesi başarıyla eklendi.',
                'id': ilerleme.id
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def update_ders_ilerleme(ogrenci_id, ders_id, manual_yuzde=None, tahmini_bitis_tarihi=None):
        """
        Ders ilerleme bilgilerini güncelle
        
        Args:
            ogrenci_id: Öğrenci ID
            ders_id: Ders ID
            manual_yuzde: Manuel olarak ayarlanacak tamamlama yüzdesi (opsiyonel)
            tahmini_bitis_tarihi: Tahmini bitiş tarihi (opsiyonel)
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        # İlerleme kaydını bul
        ilerleme = DersIlerleme.query.filter_by(ogrenci_id=ogrenci_id, ders_id=ders_id).first()
        
        # Eğer ilerleme kaydı yoksa oluştur
        if not ilerleme:
            ders = Ders.query.get(ders_id)
            if not ders:
                return {
                    'success': False, 
                    'message': 'Ders bulunamadı.'
                }
            
            # Konuların tamamlanma durumuna göre yüzde hesapla
            if manual_yuzde is None:
                tamamlama_yuzdesi = ProgramService._hesapla_ders_tamamlama_yuzdesi(ogrenci_id, ders_id)
            else:
                tamamlama_yuzdesi = manual_yuzde
            
            # Yeni ilerleme oluştur
            ilerleme = DersIlerleme(
                ogrenci_id=ogrenci_id,
                ders_id=ders_id,
                tamamlama_yuzdesi=tamamlama_yuzdesi,
                tahmini_bitis_tarihi=tahmini_bitis_tarihi,
                son_guncelleme=datetime.now()
            )
            
            try:
                db.session.add(ilerleme)
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Ders ilerlemesi başarıyla oluşturuldu.',
                    'id': ilerleme.id
                }
            except Exception as e:
                db.session.rollback()
                return {
                    'success': False,
                    'message': f'Hata oluştu: {str(e)}'
                }
        
        # Mevcut ilerlemeyi güncelle
        if manual_yuzde is not None:
            # Yüzde kontrolü
            if manual_yuzde < 0 or manual_yuzde > 100:
                return {
                    'success': False,
                    'message': 'Tamamlama yüzdesi 0-100 arasında olmalıdır.'
                }
            ilerleme.tamamlama_yuzdesi = manual_yuzde
        else:
            # Konuların tamamlanma durumuna göre yüzde hesapla
            ilerleme.tamamlama_yuzdesi = ProgramService._hesapla_ders_tamamlama_yuzdesi(ogrenci_id, ders_id)
        
        if tahmini_bitis_tarihi is not None:
            ilerleme.tahmini_bitis_tarihi = tahmini_bitis_tarihi
        
        ilerleme.son_guncelleme = datetime.now()
        
        try:
            db.session.commit()
            return {
                'success': True,
                'message': 'Ders ilerlemesi başarıyla güncellendi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def delete_ders_ilerleme(ilerleme_id):
        """
        Ders ilerlemesini sil
        
        Args:
            ilerleme_id: İlerleme ID
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        ilerleme = DersIlerleme.query.get(ilerleme_id)
        if not ilerleme:
            return {
                'success': False,
                'message': 'Ders ilerlemesi bulunamadı.'
            }
        
        try:
            db.session.delete(ilerleme)
            db.session.commit()
            return {
                'success': True,
                'message': 'Ders ilerlemesi başarıyla silindi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def _hesapla_ders_tamamlama_yuzdesi(ogrenci_id, ders_id):
        """
        Ders tamamlama yüzdesini konuların durumuna göre hesapla
        
        Args:
            ogrenci_id: Öğrenci ID
            ders_id: Ders ID
            
        Returns:
            Tamamlama yüzdesi (0-100)
        """
        # Derse ait tüm konuları bul
        konular = Konu.query.filter_by(ders_id=ders_id).all()
        
        if not konular:
            return 0
        
        # Her konu için takip kaydını bul
        tamamlanan_konu_sayisi = 0
        
        for konu in konular:
            takip = KonuTakip.query.filter_by(ogrenci_id=ogrenci_id, konu_id=konu.id).first()
            if takip and takip.tamamlandi:
                tamamlanan_konu_sayisi += 1
        
        # Tamamlama yüzdesini hesapla
        if len(konular) > 0:
            return (tamamlanan_konu_sayisi / len(konular)) * 100
        else:
            return 0
    
    @staticmethod
    def generate_haftalik_plan(ogrenci_id, baslangic_tarihi=None):
        """
        Belirli bir haftaya ait ders programı ve konuları içeren haftalık plan oluştur
        
        Args:
            ogrenci_id: Öğrenci ID
            baslangic_tarihi: Hafta başlangıç tarihi (opsiyonel, varsayılan bugün)
            
        Returns:
            Dict: Haftalık plan verilerini içeren sözlük
        """
        # Başlangıç tarihini ayarla (varsayılan: bugün)
        if baslangic_tarihi is None:
            bugun = datetime.now().date()
            # Haftanın başlangıcını bul (Pazartesi)
            hafta_basi = bugun - timedelta(days=bugun.weekday())
        else:
            # Belirtilen tarihin haftasının başlangıcını bul
            if isinstance(baslangic_tarihi, str):
                baslangic_tarihi = datetime.strptime(baslangic_tarihi, '%Y-%m-%d').date()
            hafta_basi = baslangic_tarihi - timedelta(days=baslangic_tarihi.weekday())
        
        # Hafta sonu
        hafta_sonu = hafta_basi + timedelta(days=6)
        
        # Öğrenci bilgisini getir
        ogrenci = Ogrenci.query.get(ogrenci_id)
        if not ogrenci:
            return {
                'success': False,
                'message': 'Öğrenci bulunamadı.'
            }
        
        # Ders programını getir
        programlar = DersProgrami.query.filter_by(ogrenci_id=ogrenci_id).order_by(
            DersProgrami.gun, DersProgrami.baslangic_saat
        ).all()
        
        # Günleri oluştur
        gunler = []
        for i in range(7):
            gun_tarih = hafta_basi + timedelta(days=i)
            gun = {
                'index': i,
                'ad': ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"][i],
                'tarih': gun_tarih,
                'tarih_str': gun_tarih.strftime('%d.%m.%Y'),
                'dersler': []
            }
            
            # Bu güne ait dersleri bul
            for program in programlar:
                if program.gun == i:
                    ders = Ders.query.get(program.ders_id)
                    ders_bilgi = {
                        'id': program.id,
                        'ders_id': ders.id,
                        'ders_adi': ders.ad,
                        'baslangic_saat': program.baslangic_saat.strftime('%H:%M'),
                        'bitis_saat': program.bitis_saat.strftime('%H:%M'),
                        'sure_dakika': program.sure_dakika()
                    }
                    gun['dersler'].append(ders_bilgi)
            
            gunler.append(gun)
        
        # İlerleme durumunu getir
        ilerlemeler = DersIlerleme.query.filter_by(ogrenci_id=ogrenci_id).all()
        ders_ilerleme = {}
        
        for ilerleme in ilerlemeler:
            ders = Ders.query.get(ilerleme.ders_id)
            ders_ilerleme[ilerleme.ders_id] = {
                'id': ilerleme.id,
                'ders_id': ilerleme.ders_id,
                'ders_adi': ders.ad,
                'tamamlama_yuzdesi': ilerleme.tamamlama_yuzdesi,
                'tahmini_bitis_tarihi': ilerleme.tahmini_bitis_tarihi.strftime('%d.%m.%Y') if ilerleme.tahmini_bitis_tarihi else None
            }
        
        # Sonucu döndür
        return {
            'success': True,
            'ogrenci': {
                'id': ogrenci.id,
                'numara': ogrenci.numara,
                'ad_soyad': ogrenci.tam_ad(),
                'sinif': ogrenci.sinif
            },
            'hafta': {
                'baslangic': hafta_basi.strftime('%d.%m.%Y'),
                'bitis': hafta_sonu.strftime('%d.%m.%Y')
            },
            'gunler': gunler,
            'ders_ilerleme': ders_ilerleme
        }