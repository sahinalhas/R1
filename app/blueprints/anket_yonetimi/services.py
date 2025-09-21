"""
Anket Yönetimi işlemleri için servis modülü
Bu modül, anket yönetimi ile ilgili iş mantığı işlemlerini gerçekleştirir.
"""

import json
import csv
import io
from datetime import datetime
from app.extensions import db
from app.blueprints.anket_yonetimi.models import (
    AnketTuru, CevapTuru, Anket, AnketSoru, 
    OgrenciAnket, AnketCevap, SinifAnketSonuc
)
from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from sqlalchemy import or_, and_, func

class AnketService:
    """Anket işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def get_anket_turleri():
        """
        Tüm anket türlerini getir
        
        Returns:
            List: Anket türleri listesi
        """
        return AnketTuru.query.order_by(AnketTuru.tur_adi).all()
    
    @staticmethod
    def get_cevap_turleri():
        """
        Tüm cevap türlerini getir
        
        Returns:
            List: Cevap türleri listesi
        """
        return CevapTuru.query.order_by(CevapTuru.tur_adi).all()
    
    @staticmethod
    def get_anketler(aktif_mi=None):
        """
        Anketleri getir, isteğe bağlı olarak aktif filtrelemesi yapabilir
        
        Args:
            aktif_mi: Aktif filtresi (True, False veya None)
            
        Returns:
            List: Anket listesi
        """
        if aktif_mi is None:
            return Anket.query.order_by(Anket.olusturma_tarihi.desc()).all()
        else:
            return Anket.query.filter_by(aktif=aktif_mi).order_by(Anket.olusturma_tarihi.desc()).all()
    
    @staticmethod
    def get_anket(anket_id):
        """
        ID'ye göre anket getir
        
        Args:
            anket_id: Anket ID
            
        Returns:
            Anket: Anket nesnesi veya None
        """
        return Anket.query.get(anket_id)
    
    @staticmethod
    def kaydet_anket_turu(tur_adi, aciklama=None):
        """
        Anket türü kaydet
        
        Args:
            tur_adi: Anket türü adı
            aciklama: Açıklama
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Aynı isimde anket türü var mı kontrol et
            mevcut = AnketTuru.query.filter(func.lower(AnketTuru.tur_adi) == func.lower(tur_adi)).first()
            if mevcut:
                return {
                    "success": False,
                    "message": f"'{tur_adi}' isimli anket türü zaten mevcut."
                }
            
            yeni_tur = AnketTuru(
                tur_adi=tur_adi,
                aciklama=aciklama
            )
            
            db.session.add(yeni_tur)
            db.session.commit()
            
            return {
                "success": True,
                "message": f"'{tur_adi}' anket türü başarıyla eklendi.",
                "id": yeni_tur.id
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Anket türü eklenirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def kaydet_cevap_turu(tur_adi, aciklama=None):
        """
        Cevap türü kaydet
        
        Args:
            tur_adi: Cevap türü adı
            aciklama: Açıklama
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Aynı isimde cevap türü var mı kontrol et
            mevcut = CevapTuru.query.filter(func.lower(CevapTuru.tur_adi) == func.lower(tur_adi)).first()
            if mevcut:
                return {
                    "success": False,
                    "message": f"'{tur_adi}' isimli cevap türü zaten mevcut."
                }
            
            yeni_tur = CevapTuru(
                tur_adi=tur_adi,
                aciklama=aciklama
            )
            
            db.session.add(yeni_tur)
            db.session.commit()
            
            return {
                "success": True,
                "message": f"'{tur_adi}' cevap türü başarıyla eklendi.",
                "id": yeni_tur.id
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Cevap türü eklenirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def kaydet_anket(baslik, anket_turu_id, aciklama=None, anket_id=None):
        """
        Anket kaydet (yeni veya güncelleme)
        
        Args:
            baslik: Anket başlığı
            anket_turu_id: Anket türü ID
            aciklama: Açıklama
            anket_id: Güncellenecek anket ID (None ise yeni anket)
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Anket türü var mı kontrol et
            anket_turu = AnketTuru.query.get(anket_turu_id)
            if not anket_turu:
                return {
                    "success": False,
                    "message": "Geçersiz anket türü seçildi."
                }
            
            # Yeni anket mi yoksa güncelleme mi kontrol et
            if anket_id:
                anket = Anket.query.get(anket_id)
                if not anket:
                    return {
                        "success": False,
                        "message": "Güncellenecek anket bulunamadı."
                    }
                
                # Anketi güncelle
                anket.baslik = baslik
                anket.anket_turu_id = anket_turu_id
                anket.aciklama = aciklama
                anket.guncelleme_tarihi = datetime.now()
                
                message = f"'{baslik}' anketi başarıyla güncellendi."
            else:
                # Yeni anket oluştur
                anket = Anket(
                    baslik=baslik,
                    anket_turu_id=anket_turu_id,
                    aciklama=aciklama
                )
                db.session.add(anket)
                
                message = f"'{baslik}' anketi başarıyla oluşturuldu."
            
            db.session.commit()
            
            return {
                "success": True,
                "message": message,
                "id": anket.id
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Anket kaydedilirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def kaydet_anket_soru(anket_id, soru_metni, cevap_turu_id, soru_sirasi=None, 
                        cevap_secenekleri=None, zorunlu=True, ters_puanlama=False, soru_id=None):
        """
        Anket sorusu kaydet (yeni veya güncelleme)
        
        Args:
            anket_id: Anket ID
            soru_metni: Soru metni
            cevap_turu_id: Cevap türü ID
            soru_sirasi: Soru sırası
            cevap_secenekleri: Cevap seçenekleri (liste veya JSON string)
            zorunlu: Zorunlu mu
            ters_puanlama: Ters puanlama yapılacak mı
            soru_id: Güncellenecek soru ID (None ise yeni soru)
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Anket var mı kontrol et
            anket = Anket.query.get(anket_id)
            if not anket:
                return {
                    "success": False,
                    "message": "Anket bulunamadı."
                }
            
            # Cevap türü var mı kontrol et
            cevap_turu = CevapTuru.query.get(cevap_turu_id)
            if not cevap_turu:
                return {
                    "success": False,
                    "message": "Geçersiz cevap türü seçildi."
                }
            
            # Cevap seçeneklerini JSON formatına çevir
            if cevap_secenekleri:
                if isinstance(cevap_secenekleri, list):
                    cevap_secenekleri_json = json.dumps(cevap_secenekleri)
                elif isinstance(cevap_secenekleri, str):
                    try:
                        # String zaten JSON formatında mı kontrol et
                        json.loads(cevap_secenekleri)
                        cevap_secenekleri_json = cevap_secenekleri
                    except:
                        # JSON formatında değilse, satır satır olduğunu varsay
                        secenekler_liste = [s.strip() for s in cevap_secenekleri.strip().split('\n') if s.strip()]
                        cevap_secenekleri_json = json.dumps(secenekler_liste)
                else:
                    cevap_secenekleri_json = None
            else:
                cevap_secenekleri_json = None
            
            # Soru sırası belirlenmemişse, en son sıra numarasını bul ve 1 ekle
            if not soru_sirasi:
                max_sira = db.session.query(func.max(AnketSoru.soru_sirasi)).filter_by(anket_id=anket_id).scalar()
                soru_sirasi = (max_sira or 0) + 1
            
            # Yeni soru mu yoksa güncelleme mi kontrol et
            if soru_id:
                soru = AnketSoru.query.get(soru_id)
                if not soru:
                    return {
                        "success": False,
                        "message": "Güncellenecek soru bulunamadı."
                    }
                
                # Soruyu güncelle
                soru.soru_metni = soru_metni
                soru.cevap_turu_id = cevap_turu_id
                soru.soru_sirasi = soru_sirasi
                soru.cevap_secenekleri = cevap_secenekleri_json
                soru.zorunlu = zorunlu
                soru.ters_puanlama = ters_puanlama
                
                message = "Soru başarıyla güncellendi."
            else:
                # Yeni soru oluştur
                soru = AnketSoru(
                    anket_id=anket_id,
                    soru_metni=soru_metni,
                    cevap_turu_id=cevap_turu_id,
                    soru_sirasi=soru_sirasi,
                    cevap_secenekleri=cevap_secenekleri_json,
                    zorunlu=zorunlu,
                    ters_puanlama=ters_puanlama
                )
                db.session.add(soru)
                
                message = "Soru başarıyla eklendi."
            
            db.session.commit()
            
            return {
                "success": True,
                "message": message,
                "id": soru.id
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Soru kaydedilirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def sil_anket_soru(soru_id):
        """
        Anket sorusunu sil
        
        Args:
            soru_id: Silinecek soru ID
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            soru = AnketSoru.query.get(soru_id)
            
            if not soru:
                return {
                    "success": False,
                    "message": "Silinecek soru bulunamadı."
                }
            
            # Cevapları ve soruyu sil
            db.session.delete(soru)
            db.session.commit()
            
            return {
                "success": True,
                "message": "Soru başarıyla silindi."
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Soru silinirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def sil_anket(anket_id):
        """
        Anketi ve tüm bağlantılı soruları, cevapları sil
        
        Args:
            anket_id: Silinecek anket ID
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            anket = Anket.query.get(anket_id)
            
            if not anket:
                return {
                    "success": False,
                    "message": "Silinecek anket bulunamadı."
                }
            
            # Cascade silme yapacak
            db.session.delete(anket)
            db.session.commit()
            
            return {
                "success": True,
                "message": f"'{anket.baslik}' anketi başarıyla silindi."
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Anket silinirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def anket_durum_degistir(anket_id, aktif_mi):
        """
        Anketin aktiflik durumunu değiştir
        
        Args:
            anket_id: Anket ID
            aktif_mi: Aktif mi (True/False)
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            anket = Anket.query.get(anket_id)
            
            if not anket:
                return {
                    "success": False,
                    "message": "Anket bulunamadı."
                }
            
            anket.aktif = aktif_mi
            db.session.commit()
            
            durum = "aktifleştirildi" if aktif_mi else "pasifleştirildi"
            return {
                "success": True,
                "message": f"'{anket.baslik}' anketi başarıyla {durum}."
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Anket durumu değiştirilirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def ogrencilere_anket_ata(anket_id, ogrenci_listesi):
        """
        Belirtilen öğrencilere anketi ata
        
        Args:
            anket_id: Anket ID
            ogrenci_listesi: Öğrenci ID listesi
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            anket = Anket.query.get(anket_id)
            
            if not anket:
                return {
                    "success": False,
                    "message": "Atanacak anket bulunamadı."
                }
            
            if not anket.aktif:
                return {
                    "success": False,
                    "message": "Pasif bir anket öğrencilere atanamaz."
                }
            
            # Öğrencilere anketi ata
            eklenen_sayisi = 0
            zaten_var_sayisi = 0
            
            for ogrenci_id in ogrenci_listesi:
                # Öğrenci var mı kontrol et
                ogrenci = Ogrenci.query.get(ogrenci_id)
                if not ogrenci:
                    continue
                
                # Bu anket zaten öğrenciye atanmış mı kontrol et
                mevcut = OgrenciAnket.query.filter_by(
                    ogrenci_id=ogrenci_id,
                    anket_id=anket_id
                ).first()
                
                if mevcut:
                    zaten_var_sayisi += 1
                    continue
                
                # Yeni atama oluştur
                yeni_atama = OgrenciAnket(
                    ogrenci_id=ogrenci_id,
                    anket_id=anket_id
                )
                db.session.add(yeni_atama)
                eklenen_sayisi += 1
            
            db.session.commit()
            
            message = f"{eklenen_sayisi} öğrenciye anket başarıyla atandı."
            if zaten_var_sayisi > 0:
                message += f" {zaten_var_sayisi} öğrenciye daha önce atandığı için yeniden atanmadı."
            
            return {
                "success": True,
                "message": message,
                "eklenen": eklenen_sayisi,
                "zaten_var": zaten_var_sayisi
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Anket atanırken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def toplu_cevap_yukle(anket_id, file_content, sinif=None, dosya_turu='csv'):
        """
        CSV veya Excel dosyasından toplu cevap yükle
        
        Format:
        ogrenci_no,soru1,soru2,soru3,...
        123,cevap1,cevap2,cevap3,...
        
        Args:
            anket_id: Anket ID
            file_content: CSV veya Excel dosya içeriği
            sinif: Sınıf bilgisi (isteğe bağlı)
            dosya_turu: Dosya türü ('csv' veya 'excel')
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            anket = Anket.query.get(anket_id)
            
            if not anket:
                return {
                    "success": False,
                    "message": "Anket bulunamadı."
                }
            
            # Anketin sorularını al
            sorular = AnketSoru.query.filter_by(anket_id=anket_id).order_by(AnketSoru.soru_sirasi).all()
            
            if not sorular:
                return {
                    "success": False,
                    "message": "Anketin hiç sorusu bulunamadı."
                }
            
            # Dosya türüne göre işle
            if dosya_turu == 'csv':
                # CSV dosyasını oku
                csv_data = io.StringIO(file_content)
                csv_reader = csv.reader(csv_data)
                
                # Başlık satırını oku
                try:
                    headers = next(csv_reader)
                except StopIteration:
                    return {
                        "success": False,
                        "message": "CSV dosyası boş veya geçersiz."
                    }
                
                # Veriyi rows listesine al
                rows = list(csv_reader)
                
            elif dosya_turu == 'excel':
                # Excel dosyasını oku (openpyxl kullanarak)
                import openpyxl
                from io import BytesIO
                
                wb = openpyxl.load_workbook(BytesIO(file_content), read_only=True)
                sheet = wb.active
                
                # Excel'den verileri okuma
                rows = []
                headers = None
                
                # openpyxl ile veri okuma
                all_rows = list(sheet.iter_rows(values_only=True))
                if all_rows:
                    # İlk satır başlık
                    headers = [str(cell) if cell is not None else "" for cell in all_rows[0]]
                    
                    # Diğer satırlar veri
                    for row in all_rows[1:]:
                        row_data = [str(cell) if cell is not None else "" for cell in row]
                        if any(row_data):  # Boş satırları atla
                            rows.append(row_data)
                            
            else:
                return {
                    "success": False,
                    "message": "Desteklenmeyen dosya formatı."
                }
            
            # Başlıkları kontrol et
            if not headers or len(headers) < 2:  # En az öğrenci_no ve bir cevap olmalı
                return {
                    "success": False,
                    "message": "Dosya formatı geçersiz. En az öğrenci_no ve bir cevap sütunu olmalı."
                }
            # İlk sütun adını kontrol et
            if headers[0].lower() != "ogrenci_no":
                return {
                    "success": False,
                    "message": "Dosyanın ilk sütunu 'ogrenci_no' olmalıdır."
                }
                
            # Beklenen soru sayısı
            beklenen_soru_sayisi = len(sorular)
            
            # Başlıktaki soru sayısı
            cevap_sayisi = len(headers) - 1  # İlk sütun öğrenci_no
            
            if cevap_sayisi != beklenen_soru_sayisi:
                return {
                    "success": False,
                    "message": f"Dosyadaki soru sayısı ({cevap_sayisi}) ile anketin soru sayısı ({beklenen_soru_sayisi}) eşleşmiyor."
                }
            
            # İstatistikler
            basarili_ogrenci = 0
            basarisiz_ogrenci = 0
            bulunamayan_ogrenci = 0
            
            # Her satırı işle (her satır bir öğrenci)
            for row in rows:
                if len(row) < 2:  # Satır geçersiz, atla
                    basarisiz_ogrenci += 1
                    continue
                
                ogrenci_no = str(row[0]).strip()
                
                # Öğrenci numarasına göre öğrenciyi bul
                ogrenci = Ogrenci.query.filter_by(numara=ogrenci_no).first()
                
                if not ogrenci:
                    bulunamayan_ogrenci += 1
                    continue
                
                # Öğrenci için anket atama var mı kontrol et
                ogrenci_anket = OgrenciAnket.query.filter_by(
                    ogrenci_id=ogrenci.id,
                    anket_id=anket_id
                ).first()
                
                # Yoksa yeni bir atama oluştur
                if not ogrenci_anket:
                    ogrenci_anket = OgrenciAnket(
                        ogrenci_id=ogrenci.id,
                        anket_id=anket_id
                    )
                    db.session.add(ogrenci_anket)
                    db.session.flush()  # ID ataması için flush
                
                try:
                    # Cevapları ekle, soru sayısı kadar (en fazla sütun sayısı - 1)
                    for i, soru in enumerate(sorular):
                        if i + 1 >= len(row):  # Satırda yeterli veri yoksa
                            continue
                            
                        cevap_metni = row[i + 1].strip()
                        
                        # Cevap zaten var mı kontrol et
                        mevcut_cevap = AnketCevap.query.filter_by(
                            ogrenci_anket_id=ogrenci_anket.id,
                            soru_id=soru.id
                        ).first()
                        
                        if mevcut_cevap:
                            # Mevcut cevabı güncelle
                            mevcut_cevap.cevap = cevap_metni
                        else:
                            # Yeni cevap ekle
                            yeni_cevap = AnketCevap(
                                ogrenci_anket_id=ogrenci_anket.id,
                                soru_id=soru.id,
                                cevap=cevap_metni
                            )
                            db.session.add(yeni_cevap)
                    
                    # Anketi tamamlanmış olarak işaretle
                    ogrenci_anket.tamamlandi = True
                    ogrenci_anket.tamamlanma_tarihi = datetime.now()
                    
                    basarili_ogrenci += 1
                except Exception as e:
                    basarisiz_ogrenci += 1
                    continue
            
            # Sınıf bazlı sonuç kaydı
            if sinif and basarili_ogrenci > 0:
                # Mevcut sınıf sonucu var mı kontrol et
                sinif_sonuc = SinifAnketSonuc.query.filter_by(
                    anket_id=anket_id,
                    sinif=sinif
                ).first()
                
                if sinif_sonuc:
                    # Güncelle
                    sinif_sonuc.cevaplayan_sayisi += basarili_ogrenci
                    sinif_sonuc.olusturma_tarihi = datetime.now()
                else:
                    # Yeni ekle
                    yeni_sinif_sonuc = SinifAnketSonuc(
                        anket_id=anket_id,
                        sinif=sinif,
                        cevaplayan_sayisi=basarili_ogrenci
                    )
                    db.session.add(yeni_sinif_sonuc)
            
            db.session.commit()
            
            message = f"{basarili_ogrenci} öğrenci için anket cevapları başarıyla kaydedildi."
            if basarisiz_ogrenci > 0:
                message += f" {basarisiz_ogrenci} öğrenci için işlem sırasında hata oluştu."
            if bulunamayan_ogrenci > 0:
                message += f" {bulunamayan_ogrenci} öğrenci sistemde bulunamadı."
            
            return {
                "success": True,
                "message": message,
                "basarili": basarili_ogrenci,
                "basarisiz": basarisiz_ogrenci,
                "bulunamayan": bulunamayan_ogrenci
            }
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Toplu cevap yüklenirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def get_anket_sonuclari(anket_id):
        """
        Anket sonuçlarını getir
        
        Args:
            anket_id: Anket ID
            
        Returns:
            Dict: Anket sonuçlarını içeren sözlük
        """
        try:
            anket = Anket.query.get(anket_id)
            
            if not anket:
                return {
                    "success": False,
                    "message": "Anket bulunamadı."
                }
            
            # Temel istatistikler
            toplam_atanan = OgrenciAnket.query.filter_by(anket_id=anket_id).count()
            tamamlanan = OgrenciAnket.query.filter_by(anket_id=anket_id, tamamlandi=True).count()
            tamamlanma_orani = round((tamamlanan / toplam_atanan) * 100) if toplam_atanan > 0 else 0
            
            # Sınıf bazlı sonuçlar
            sinif_sonuclari = SinifAnketSonuc.query.filter_by(anket_id=anket_id).all()
            
            siniflar = []
            for ss in sinif_sonuclari:
                siniflar.append({
                    "sinif": ss.sinif,
                    "cevaplayan_sayisi": ss.cevaplayan_sayisi
                })
            
            return {
                "success": True,
                "anket": {
                    "id": anket.id,
                    "baslik": anket.baslik,
                    "aciklama": anket.aciklama
                },
                "istatistikler": {
                    "toplam_atanan": toplam_atanan,
                    "tamamlanan": tamamlanan,
                    "tamamlanma_orani": tamamlanma_orani
                },
                "siniflar": siniflar
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Anket sonuçları alınırken bir hata oluştu: {str(e)}"
            }