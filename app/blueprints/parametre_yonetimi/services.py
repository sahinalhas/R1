"""
Sabitler işlemleri için servis modülü
Bu modül, sabit veriler ile ilgili iş mantığı işlemlerini gerçekleştirir.
"""

from datetime import datetime, time
from app.extensions import db
from app.blueprints.parametre_yonetimi.models import OkulBilgi, DersSaati, GorusmeKonusu, OgleArasi
from sqlalchemy import or_, and_

class SabitlerService:
    """Sabit verileri yöneten servis sınıfı"""
    
    @staticmethod
    def get_okul_bilgisi():
        """
        Aktif okul bilgisini getir
        
        Returns:
            OkulBilgi: Aktif okul bilgisi nesnesi veya None
        """
        return OkulBilgi.query.filter_by(aktif=True).first()
    
    @staticmethod
    def kaydet_okul_bilgisi(okul_adi, il, ilce, danisman_adi):
        """
        Okul bilgisini kaydet
        
        Args:
            okul_adi: Okul adı
            il: İl adı
            ilce: İlçe adı
            danisman_adi: Danışman adı
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Önce mevcut aktif okul bilgisini pasif yap
            mevcut_bilgiler = OkulBilgi.query.filter_by(aktif=True).all()
            for bilgi in mevcut_bilgiler:
                bilgi.aktif = False
                
            # Yeni okul bilgisini ekle
            yeni_bilgi = OkulBilgi(
                okul_adi=okul_adi,
                il=il,
                ilce=ilce,
                danisman_adi=danisman_adi,
                aktif=True
            )
            
            db.session.add(yeni_bilgi)
            db.session.commit()
            
            return {
                "success": True,
                "message": "Okul bilgileri başarıyla kaydedildi.",
                "id": yeni_bilgi.id
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Okul bilgileri kaydedilirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def get_ders_saatleri():
        """
        Tüm ders saatlerini getir
        
        Returns:
            List: Ders saatleri listesi
        """
        return DersSaati.query.order_by(DersSaati.ders_numarasi).all()
        
    @staticmethod
    def get_ogle_arasi():
        """
        Aktif öğle arası bilgisini getir
        
        Returns:
            OgleArasi: Öğle arası bilgisi nesnesi veya None
        """
        return OgleArasi.query.filter_by(aktif=True).first()
    
    @staticmethod
    def kaydet_ders_saatleri(ders_saatleri_metin, lunch_start_time='12:00', lunch_end_time='12:50'):
        """
        Ders saatlerini metin alanından toplu ekle
        Format: "1,08:30,09:10,0" (ders_no,başlangıç,bitiş,öğle_arası(0/1))
        
        Args:
            ders_saatleri_metin: Ders saatleri metni
            lunch_start_time: Öğle arası başlangıç saati (varsayılan: 12:00)
            lunch_end_time: Öğle arası bitiş saati (varsayılan: 12:50)
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Önce tüm ders saatlerini temizle
            DersSaati.query.delete()
            
            # Önce öğle arası bilgilerini güncelle
            # Öğle arası kaydını temizle ve yenisini ekle
            OgleArasi.query.delete()
            lunch_start = datetime.strptime(lunch_start_time, '%H:%M').time()
            lunch_end = datetime.strptime(lunch_end_time, '%H:%M').time()
            yeni_ogle_arasi = OgleArasi(
                baslangic_saati=lunch_start,
                bitis_saati=lunch_end,
                aktif=True
            )
            db.session.add(yeni_ogle_arasi)
            
            # Yeni ders saatlerini ekle
            satir_sayisi = 0
            hatali_satirlar = []
            
            # Eğer metin alanı doluysa, ders saatlerini işle
            if ders_saatleri_metin:
                for satir in ders_saatleri_metin.strip().split('\n'):
                    satir = satir.strip()
                    if not satir:
                        continue
                        
                    try:
                        parcalar = satir.split(',')
                        if len(parcalar) != 4:
                            hatali_satirlar.append(satir)
                            continue
                            
                        ders_no = int(parcalar[0])
                        baslangic = datetime.strptime(parcalar[1], '%H:%M').time()
                        bitis = datetime.strptime(parcalar[2], '%H:%M').time()
                        ogle_arasi = bool(int(parcalar[3]))
                        
                        yeni_ders_saati = DersSaati(
                            ders_numarasi=ders_no,
                            baslangic_saati=baslangic,
                            bitis_saati=bitis,
                            ogle_arasi=ogle_arasi
                        )
                        
                        db.session.add(yeni_ders_saati)
                        satir_sayisi += 1
                    except Exception as e:
                        hatali_satirlar.append(f"{satir} ({str(e)})")
            
            db.session.commit()
            
            # Ders saati girilmemişse de sorun değil, sadece bilgilendirme mesajı değişecek
            if satir_sayisi > 0:
                message = f"{satir_sayisi} ders saati başarıyla kaydedildi."
            else:
                message = "Ders saatleri temizlendi."
                
            if hatali_satirlar:
                message += f" {len(hatali_satirlar)} satır hatalı: {', '.join(hatali_satirlar[:3])}" 
                if len(hatali_satirlar) > 3:
                    message += f" ve {len(hatali_satirlar) - 3} adet daha."
            
            return {
                "success": True,
                "message": message
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Ders saatleri kaydedilirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def get_gorusme_konulari():
        """
        Tüm görüşme konularını getir
        
        Returns:
            List: Görüşme konuları listesi
        """
        return GorusmeKonusu.query.order_by(GorusmeKonusu.baslik).all()
    
    @staticmethod
    def kaydet_gorusme_konulari(konular_metni):
        """
        Görüşme konularını metin alanından toplu ekle
        Her satır bir konu başlığı olarak eklenir.
        
        Args:
            konular_metni: Görüşme konuları metni
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Önce tüm görüşme konularını temizle
            GorusmeKonusu.query.delete()
            
            # Yeni görüşme konularını ekle
            konu_sayisi = 0
            hatali_konular = []
            
            for satir in konular_metni.strip().split('\n'):
                satir = satir.strip()
                if not satir:
                    continue
                    
                try:
                    yeni_konu = GorusmeKonusu(baslik=satir)
                    db.session.add(yeni_konu)
                    konu_sayisi += 1
                except Exception as e:
                    hatali_konular.append(f"{satir} ({str(e)})")
            
            db.session.commit()
            
            message = f"{konu_sayisi} görüşme konusu başarıyla kaydedildi."
            if hatali_konular:
                message += f" {len(hatali_konular)} konu hatalı: {', '.join(hatali_konular[:3])}" 
                if len(hatali_konular) > 3:
                    message += f" ve {len(hatali_konular) - 3} adet daha."
            
            return {
                "success": True,
                "message": message
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Görüşme konuları kaydedilirken bir hata oluştu: {str(e)}"
            }
            
    @staticmethod
    def sil_gorusme_konusu(konu_id):
        """
        Belirtilen ID'ye sahip görüşme konusunu sil
        
        Args:
            konu_id: Silinecek görüşme konusunun ID'si
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            konu = GorusmeKonusu.query.get(konu_id)
            
            if not konu:
                return {
                    "success": False,
                    "message": "Görüşme konusu bulunamadı!"
                }
                
            baslik = konu.baslik
            db.session.delete(konu)
            db.session.commit()
            
            return {
                "success": True,
                "message": f"\"{baslik}\" konusu başarıyla silindi."
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Görüşme konusu silinirken bir hata oluştu: {str(e)}"
            }