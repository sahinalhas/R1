"""
Ders tamamlanma tarihini hesaplama işlemleri
"""
from datetime import datetime, timedelta
from app.extensions import db
from app.blueprints.calisma_programi.models import DersProgrami, DersIlerleme, KonuTakip
from app.blueprints.ders_konu_yonetimi.models import Ders, Konu

def calculate_ders_completion_date(ogrenci_id, ders_id):
    """
    Ders tamamlanma tarihini hesapla
    
    Args:
        ogrenci_id: Öğrenci ID
        ders_id: Ders ID
        
    Returns:
        Dict: Hesaplanan tamamlanma bilgilerini içeren sözlük
    """
    try:
        # Dersin konularını al
        konular = Konu.query.filter_by(ders_id=ders_id).all()
        toplam_konu_sayisi = len(konular)
        
        if toplam_konu_sayisi == 0:
            return {
                'success': False,
                'message': 'Ders için tanımlanmış konu bulunmamaktadır.'
            }
        
        # Öğrencinin ders takip verilerini al
        konu_takipleri = KonuTakip.query.filter_by(
            ogrenci_id=ogrenci_id
        ).filter(
            KonuTakip.konu_id.in_([konu.id for konu in konular])
        ).all()
        
        # Tamamlanan konuları say
        tamamlanan_konu_sayisi = sum(1 for takip in konu_takipleri if takip.tamamlandi)
        
        # Tamamlanma yüzdesi
        tamamlanma_yuzdesi = (tamamlanan_konu_sayisi / toplam_konu_sayisi) * 100 if toplam_konu_sayisi > 0 else 0
        
        # Kalan konular
        kalan_konu_sayisi = toplam_konu_sayisi - tamamlanan_konu_sayisi
        
        # Haftalık ders programından bu derse ayrılan toplam süreyi hesapla (dakika)
        ders_programlari = DersProgrami.query.filter_by(
            ogrenci_id=ogrenci_id,
            ders_id=ders_id
        ).all()
        
        # Haftalık toplam ders süresi (dakika)
        haftalik_sure = sum(dp.sure_dakika() for dp in ders_programlari)
        
        # Eğer haftalık süre yoksa (program tanımlanmamışsa)
        if haftalik_sure == 0:
            return {
                'success': True,
                'tamamlanma_yuzdesi': tamamlanma_yuzdesi,
                'tamamlanan_konu': tamamlanan_konu_sayisi,
                'toplam_konu': toplam_konu_sayisi,
                'kalan_konu': kalan_konu_sayisi,
                'tahmini_bitis_tarihi': None,
                'haftalik_sure': 0,
                'kalan_hafta': None,
                'message': 'Ders için haftalık program tanımlanmamış.'
            }
        
        # Kalan konuların tahmini süresini hesapla
        kalan_sure = 0
        for konu in konular:
            takip = next((t for t in konu_takipleri if t.konu_id == konu.id), None)
            if not takip or not takip.tamamlandi:
                kalan_sure += konu.tahmini_sure  # Dakika cinsinden
        
        # Kalan süreyi tamamlamak için gereken hafta sayısı
        kalan_hafta = kalan_sure / haftalik_sure if haftalik_sure > 0 else None
        
        # Tahmini bitiş tarihi
        tahmini_bitis_tarihi = None
        if kalan_hafta is not None:
            kalan_gun = int(kalan_hafta * 7)
            tahmini_bitis_tarihi = (datetime.now() + timedelta(days=kalan_gun)).date()
        
        return {
            'success': True,
            'tamamlanma_yuzdesi': tamamlanma_yuzdesi,
            'tamamlanan_konu': tamamlanan_konu_sayisi,
            'toplam_konu': toplam_konu_sayisi,
            'kalan_konu': kalan_konu_sayisi,
            'tahmini_bitis_tarihi': tahmini_bitis_tarihi,
            'haftalik_sure': haftalik_sure,
            'kalan_hafta': kalan_hafta,
            'message': 'Tahmini bitiş süresi hesaplandı.'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Hesaplama sırasında hata oluştu: {str(e)}"
        }

def calculate_all_ders_completion_dates(ogrenci_id):
    """
    Öğrencinin tüm derslerinin tahmini bitiş tarihlerini hesapla
    
    Args:
        ogrenci_id: Öğrenci ID
        
    Returns:
        Dict: Her ders için hesaplanan tamamlanma bilgilerini içeren sözlük
    """
    # Öğrencinin program tanımlı tüm derslerini al
    ders_ids = db.session.query(DersProgrami.ders_id).filter_by(ogrenci_id=ogrenci_id).distinct().all()
    ders_ids = [d[0] for d in ders_ids]
    
    ders_bilgileri = {}
    for ders_id in ders_ids:
        ders = Ders.query.get(ders_id)
        if ders:
            ders_bilgileri[ders_id] = {
                'ders': ders,
                'bilgiler': calculate_ders_completion_date(ogrenci_id, ders_id)
            }
    
    # Genel tahmini tamamlanma tarihini hesapla (en geç tamamlanacak ders)
    en_gec_tamamlanma = None
    for ders_id, bilgi in ders_bilgileri.items():
        if bilgi['bilgiler']['success'] and bilgi['bilgiler']['tahmini_bitis_tarihi']:
            if en_gec_tamamlanma is None or bilgi['bilgiler']['tahmini_bitis_tarihi'] > en_gec_tamamlanma:
                en_gec_tamamlanma = bilgi['bilgiler']['tahmini_bitis_tarihi']
    
    return {
        'success': True,
        'ders_bilgileri': ders_bilgileri,
        'en_gec_tamamlanma_tarihi': en_gec_tamamlanma
    }

def update_ders_completion_dates(ogrenci_id):
    """
    Öğrencinin tüm derslerinin tahmini bitiş tarihlerini hesaplayıp DersIlerleme tablosuna kaydet
    
    Args:
        ogrenci_id: Öğrenci ID
        
    Returns:
        Dict: İşlem sonucunu içeren sözlük
    """
    try:
        # Tüm derslerin tamamlanma bilgilerini al
        sonuc = calculate_all_ders_completion_dates(ogrenci_id)
        
        if not sonuc['success']:
            return sonuc
        
        # Her ders için ilerleme bilgilerini güncelle
        for ders_id, bilgi in sonuc['ders_bilgileri'].items():
            if bilgi['bilgiler']['success']:
                # DersIlerleme kaydını bul veya oluştur
                ilerleme = DersIlerleme.query.filter_by(
                    ogrenci_id=ogrenci_id, 
                    ders_id=ders_id
                ).first()
                
                if not ilerleme:
                    ilerleme = DersIlerleme(
                        ogrenci_id=ogrenci_id,
                        ders_id=ders_id,
                        tamamlama_yuzdesi=bilgi['bilgiler']['tamamlanma_yuzdesi'],
                        tahmini_bitis_tarihi=bilgi['bilgiler']['tahmini_bitis_tarihi']
                    )
                    db.session.add(ilerleme)
                else:
                    ilerleme.tamamlama_yuzdesi = bilgi['bilgiler']['tamamlanma_yuzdesi']
                    ilerleme.tahmini_bitis_tarihi = bilgi['bilgiler']['tahmini_bitis_tarihi']
                    ilerleme.son_guncelleme = datetime.now()
        
        db.session.commit()
        return {
            'success': True,
            'message': 'Tüm derslerin tahmini bitiş tarihleri güncellendi.',
            'en_gec_tamamlanma_tarihi': sonuc['en_gec_tamamlanma_tarihi']
        }
    
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f"Güncelleme sırasında hata oluştu: {str(e)}"
        }