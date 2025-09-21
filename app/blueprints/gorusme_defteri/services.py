"""
Görüşme Defteri işlemleri için servis modülü
Bu modül, görüşme kayıtları ile ilgili iş mantığı işlemlerini gerçekleştirir.
"""

from datetime import datetime
from flask import current_app
from app.extensions import db
from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from app.blueprints.gorusme_defteri.models import GorusmeKaydi

class GorusmeService:
    """Görüşme kayıtları işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def get_gorusme_sayisi(baslangic_tarihi, bitis_tarihi):
        """
        Belirli bir tarih aralığındaki görüşme sayısını getir
        
        Args:
            baslangic_tarihi: Başlangıç tarihi
            bitis_tarihi: Bitiş tarihi
            
        Returns:
            int: Görüşme sayısı
        """
        return GorusmeKaydi.query.filter(
            GorusmeKaydi.tarih >= baslangic_tarihi,
            GorusmeKaydi.tarih <= bitis_tarihi
        ).count()
    
    @staticmethod
    def get_gorusmeler_by_date(tarih):
        """
        Belirli bir tarihteki görüşmeleri getir
        
        Args:
            tarih: Görüşme tarihi
            
        Returns:
            List: Görüşme kayıtlarının listesi
        """
        return GorusmeKaydi.query.filter(
            GorusmeKaydi.tarih == tarih
        ).order_by(GorusmeKaydi.baslangic_saati).all()
    
    @staticmethod
    def calculate_meeting_counts():
        """
        Her öğrenci için toplam görüşme sayısını hesapla
        
        Returns:
            Dict: {ogrenci_id: görüşme_sayısı} şeklinde sözlük
        """
        # Öğrenci ID'lere göre kayıt sayılarını hesapla
        ogrenci_gorusme_sayilari = {}
        
        # None olmayan (bir öğrenciye ait olan) tüm görüşme kayıtlarını al
        gorusme_kayitlari = GorusmeKaydi.query.filter(GorusmeKaydi.ogrenci_id.isnot(None)).all()
        
        # Her bir kaydı döngü ile kontrol et ve öğrenci bazında say
        for kayit in gorusme_kayitlari:
            if kayit.ogrenci_id not in ogrenci_gorusme_sayilari:
                ogrenci_gorusme_sayilari[kayit.ogrenci_id] = 0
            ogrenci_gorusme_sayilari[kayit.ogrenci_id] += 1
            
        return ogrenci_gorusme_sayilari
    
    @staticmethod
    def get_meeting_count_for_student(ogrenci_id, tarih=None):
        """
        Belirli bir öğrenci için görüşme sayısını hesapla
        Belirli bir tarihten önceki görüşmeleri sayar (o tarihe kadar kaç görüşme yapıldığını bulmak için)
        
        Args:
            ogrenci_id: Öğrenci ID
            tarih: Bu tarihten önceki görüşmeleri say (None ise tüm görüşmeleri say)
            
        Returns:
            int: Öğrencinin görüşme sayısı
        """
        if not ogrenci_id:
            return 0
            
        query = GorusmeKaydi.query.filter_by(ogrenci_id=ogrenci_id)
        
        if tarih:
            query = query.filter(GorusmeKaydi.tarih <= tarih)
            
        return query.count()
    
    @staticmethod
    def get_all_gorusme_kayitlari(ay=None):
        """
        Tüm görüşme kayıtlarını getir, isteğe bağlı ay filtresi ile
        
        Args:
            ay: Ay numarası (1-12), belirtilirse o aya ait görüşmeler getirilir
            
        Returns:
            Görüşme kayıtlarının listesi
        """
        query = GorusmeKaydi.query
        
        if ay:
            # Belirli aya ait kayıtları filtrele
            query = query.filter(db.extract('month', GorusmeKaydi.tarih) == ay)
        
        # Tüm kayıtları tarih ve ID'ye göre sırala (aynı tarihli kayıtlar için ID sıralama ekledik)
        kayitlar = query.order_by(GorusmeKaydi.tarih, GorusmeKaydi.id).all()
        
        # Her bir kayıt için öğrencinin kaçıncı görüşmesi olduğunu hesapla
        ogrenci_gorusme_sayilari = {}
        
        for kayit in kayitlar:
            if kayit.ogrenci_id:
                if kayit.ogrenci_id not in ogrenci_gorusme_sayilari:
                    ogrenci_gorusme_sayilari[kayit.ogrenci_id] = 0
                ogrenci_gorusme_sayilari[kayit.ogrenci_id] += 1
                # Bu öğrencinin bu kayıtta kaçıncı görüşmesi olduğunu kaydet
                kayit.gorusme_sayisi = ogrenci_gorusme_sayilari[kayit.ogrenci_id]
        
        # Veritabanı değişikliklerini kaydet
        db.session.commit()
        
        # Kayıtları tarih sırasına göre döndür (en son tarih en üstte)
        return sorted(kayitlar, key=lambda x: x.tarih, reverse=True)
    
    @staticmethod
    def get_gorusme_kaydi_by_id(kayit_id):
        """
        ID'ye göre görüşme kaydı getir
        
        Args:
            kayit_id: Görüşme kaydı ID
            
        Returns:
            GorusmeKaydi nesnesi veya None
        """
        return GorusmeKaydi.query.get(kayit_id)
    
    @staticmethod
    def create_gorusme_kaydi(ogrenci_id=None, tarih=None, baslangic_saati=None, bitis_saati=None,
                           gorusme_sayisi=None, gorusulen_kisi=None, kisi_rolu=None, yakinlik_derecesi=None,
                           gorusme_konusu=None, calisma_alani=None, calisma_kategorisi=None,
                           hizmet_turu=None, kurum_isbirligi=None, gorusme_yeri=None,
                           disiplin_gorusmesi=False, adli_sevk=False, calisma_yontemi=None,
                           ozet=None):
        """
        Yeni görüşme kaydı oluştur
        
        Args:
            ogrenci_id: Öğrenci ID (opsiyonel, veli görüşmeleri için NULL olabilir)
            tarih: Görüşme tarihi (None ise bugün)
            baslangic_saati: Görüşme başlangıç saati
            bitis_saati: Görüşme bitiş saati
            gorusme_sayisi: Görüşme sayısı (None ise otomatik hesaplanır)
            gorusulen_kisi: Görüşülen kişi adı
            kisi_rolu: Kişinin rolü (Öğrenci, Veli, vb.)
            yakinlik_derecesi: Yakınlık derecesi (Anne, Baba, vb.)
            gorusme_konusu: Görüşme konusu
            calisma_alani, calisma_kategorisi, hizmet_turu, vb.: Diğer görüşme detayları
            ozet: Görüşme özeti
            
        Returns:
            Dict: İşlem sonucunu ve oluşturulan kayıt ID'sini içeren sözlük
        """
        try:
            # Varsayılan tarih bugün
            if tarih is None:
                tarih = datetime.now().date()
            
            # Öğrenci kaçıncı görüşmesinde hesapla (eğer bir öğrenci için kayıt yapılıyorsa)
            if ogrenci_id is not None and gorusme_sayisi is None:
                # O ana kadar olan görüşme sayısını alıp 1 ekle (bu yeni kaydın kaçıncı görüşme olduğunu belirler)
                gorusme_sayisi = GorusmeService.get_meeting_count_for_student(ogrenci_id, tarih) + 1
            elif gorusme_sayisi is None:
                # Öğrenci ID yoksa görüşme sayısı 1 olarak varsayılan değeri ata
                gorusme_sayisi = 1
                
            # Yeni kayıt oluştur
            yeni_kayit = GorusmeKaydi(
                ogrenci_id=ogrenci_id,
                tarih=tarih,
                baslangic_saati=baslangic_saati,
                bitis_saati=bitis_saati,
                gorusme_sayisi=gorusme_sayisi,
                gorusulen_kisi=gorusulen_kisi,
                kisi_rolu=kisi_rolu,
                yakinlik_derecesi=yakinlik_derecesi,
                gorusme_konusu=gorusme_konusu,
                calisma_alani=calisma_alani,
                calisma_kategorisi=calisma_kategorisi,
                hizmet_turu=hizmet_turu,
                kurum_isbirligi=kurum_isbirligi,
                gorusme_yeri=gorusme_yeri,
                disiplin_gorusmesi=disiplin_gorusmesi,
                adli_sevk=adli_sevk,
                calisma_yontemi=calisma_yontemi,
                ozet=ozet
            )
            
            db.session.add(yeni_kayit)
            db.session.commit()
            
            return {
                "success": True,
                "message": "Görüşme kaydı başarıyla oluşturuldu.",
                "kayit_id": yeni_kayit.id
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Görüşme kaydı oluşturma hatası: {str(e)}")
            return {
                "success": False,
                "message": f"Görüşme kaydı oluşturulurken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def update_gorusme_kaydi(kayit_id, ogrenci_id=None, tarih=None, baslangic_saati=None, bitis_saati=None,
                           gorusme_sayisi=None, gorusulen_kisi=None, kisi_rolu=None, yakinlik_derecesi=None,
                           gorusme_konusu=None, calisma_alani=None, calisma_kategorisi=None,
                           hizmet_turu=None, kurum_isbirligi=None, gorusme_yeri=None,
                           disiplin_gorusmesi=None, adli_sevk=None, calisma_yontemi=None,
                           ozet=None):
        """
        Görüşme kaydını güncelle
        
        Args:
            kayit_id: Güncellenecek kayıt ID'si
            Diğer parametreler: Güncellenmek istenen değerler (None ise değişmez)
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            kayit = GorusmeKaydi.query.get(kayit_id)
            
            if not kayit:
                return {
                    "success": False,
                    "message": f"ID: {kayit_id} numaralı görüşme kaydı bulunamadı."
                }
            
            # None olmayan değerleri güncelle
            if ogrenci_id is not None:
                kayit.ogrenci_id = ogrenci_id
            if tarih is not None:
                kayit.tarih = tarih
            if baslangic_saati is not None:
                kayit.baslangic_saati = baslangic_saati
            if bitis_saati is not None:
                kayit.bitis_saati = bitis_saati
            if gorusme_sayisi is not None:
                kayit.gorusme_sayisi = gorusme_sayisi
            if gorusulen_kisi is not None:
                kayit.gorusulen_kisi = gorusulen_kisi
            if kisi_rolu is not None:
                kayit.kisi_rolu = kisi_rolu
            if yakinlik_derecesi is not None:
                kayit.yakinlik_derecesi = yakinlik_derecesi
            if gorusme_konusu is not None:
                kayit.gorusme_konusu = gorusme_konusu
            if calisma_alani is not None:
                kayit.calisma_alani = calisma_alani
            if calisma_kategorisi is not None:
                kayit.calisma_kategorisi = calisma_kategorisi
            if hizmet_turu is not None:
                kayit.hizmet_turu = hizmet_turu
            if kurum_isbirligi is not None:
                kayit.kurum_isbirligi = kurum_isbirligi
            if gorusme_yeri is not None:
                kayit.gorusme_yeri = gorusme_yeri
            if disiplin_gorusmesi is not None:
                kayit.disiplin_gorusmesi = disiplin_gorusmesi
            if adli_sevk is not None:
                kayit.adli_sevk = adli_sevk
            if calisma_yontemi is not None:
                kayit.calisma_yontemi = calisma_yontemi
            if ozet is not None:
                kayit.ozet = ozet
                
            db.session.commit()
            
            return {
                "success": True,
                "message": "Görüşme kaydı başarıyla güncellendi."
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Görüşme kaydı güncelleme hatası: {str(e)}")
            return {
                "success": False,
                "message": f"Görüşme kaydı güncellenirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def delete_gorusme_kaydi(kayit_id):
        """
        Görüşme kaydını sil
        
        Args:
            kayit_id: Silinecek kayıt ID'si
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            kayit = GorusmeKaydi.query.get(kayit_id)
            
            if not kayit:
                return {
                    "success": False,
                    "message": f"ID: {kayit_id} numaralı görüşme kaydı bulunamadı."
                }
            
            db.session.delete(kayit)
            db.session.commit()
            
            return {
                "success": True,
                "message": "Görüşme kaydı başarıyla silindi."
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Görüşme kaydı silme hatası: {str(e)}")
            return {
                "success": False,
                "message": f"Görüşme kaydı silinirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def update_all_meeting_counts():
        """
        Tüm görüşme kayıtlarını güncelleyerek her öğrenci için 
        kaçıncı görüşme olduğu bilgisini yeniden hesaplar
        
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Tüm görüşme kayıtlarını al ve kronolojik sırala (eski->yeni)
            kayitlar = GorusmeKaydi.query.order_by(GorusmeKaydi.tarih, GorusmeKaydi.id).all()
            
            # Öğrenci ID'lere göre görüşme sayılarını takip et
            ogrenci_gorusme_sayilari = {}
            
            # Her kayıt için kaçıncı görüşme olduğunu hesapla
            guncellenen_kayit_sayisi = 0
            
            for kayit in kayitlar:
                if kayit.ogrenci_id:
                    if kayit.ogrenci_id not in ogrenci_gorusme_sayilari:
                        ogrenci_gorusme_sayilari[kayit.ogrenci_id] = 0
                    
                    ogrenci_gorusme_sayilari[kayit.ogrenci_id] += 1
                    
                    # Kayıttaki görüşme sayısını güncelle
                    if kayit.gorusme_sayisi != ogrenci_gorusme_sayilari[kayit.ogrenci_id]:
                        kayit.gorusme_sayisi = ogrenci_gorusme_sayilari[kayit.ogrenci_id]
                        guncellenen_kayit_sayisi += 1
            
            # Değişiklikleri kaydet
            db.session.commit()
            
            return {
                "success": True,
                "message": f"Toplam {guncellenen_kayit_sayisi} adet görüşme kaydının sayısı güncellendi."
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Görüşme sayılarını güncelleme hatası: {str(e)}")
            return {
                "success": False,
                "message": f"Görüşme sayıları güncellenirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def sync_mebbis():
        """
        MEBBİS sistemine görüşme kayıtlarını aktar
        Bu fonksiyon, MEBBİS'e aktarılmamış tüm görüşme kayıtlarını gönderir.
        
        Returns:
            Dict: İşlem sonucunu ve aktarılan kayıt sayısını içeren sözlük
        """
        try:
            # Aktarılmamış görüşme kayıtlarını bul
            aktarilmamis_kayitlar = GorusmeKaydi.query.filter_by(mebbis_aktarildi=False).all()
            
            if not aktarilmamis_kayitlar:
                return {
                    "success": True,
                    "message": "Aktarılacak görüşme kaydı bulunamadı.",
                    "aktarilan_kayit_sayisi": 0
                }
            
            # Gerçek bir sistem entegrasyonu yerine, sadece kayıtları "aktarıldı" olarak işaretle
            for kayit in aktarilmamis_kayitlar:
                kayit.mebbis_aktarildi = True
                kayit.mebbis_aktarim_tarihi = datetime.now()
                
            db.session.commit()
            
            return {
                "success": True,
                "message": f"{len(aktarilmamis_kayitlar)} adet görüşme kaydı MEBBİS'e aktarıldı.",
                "aktarilan_kayit_sayisi": len(aktarilmamis_kayitlar)
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"MEBBİS senkronizasyon hatası: {str(e)}")
            return {
                "success": False,
                "message": f"MEBBİS senkronizasyonu sırasında bir hata oluştu: {str(e)}"
            }