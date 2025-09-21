"""
Öğrenci işlemleri için servis modülü
Bu modül, öğrenci işlemleri ile ilgili iş mantığı işlemlerini gerçekleştirir.
"""

from datetime import datetime
import pandas as pd

from app.extensions import db
from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from app.blueprints.calisma_programi.models import DersIlerleme

class OgrenciService:
    """Öğrenci işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def get_risk_altindaki_ogrenci_sayisi():
        """
        Risk altındaki öğrenci sayısını getir
        (İlerleme durumu %25'in altında olan öğrenciler)
        
        Returns:
            int: Risk altındaki öğrenci sayısı
        """
        risk_altindaki_ogrenciler = OgrenciService.get_risk_altindaki_ogrenciler()
        return len(risk_altindaki_ogrenciler)
    
    @staticmethod
    def get_risk_altindaki_ogrenciler(limit=None):
        """
        Risk altındaki öğrencileri getir
        (İlerleme durumu %25'in altında olan öğrenciler)
        
        Args:
            limit: Kaç öğrenci getirileceği (None ise tümü)
            
        Returns:
            List: Öğrencilerin listesi
        """
        # Tüm öğrencileri getir
        ogrenciler = Ogrenci.query.all()
        
        # İlerleme durumu düşük olanları filtrele
        risk_altindaki_ogrenciler = []
        for ogrenci in ogrenciler:
            ilerleme = ogrenci.genel_ilerleme()
            if ilerleme < 25:  # %25'in altındaysa risk altında kabul et
                risk_altindaki_ogrenciler.append(ogrenci)
        
        # Sırala ve limitle
        risk_altindaki_ogrenciler.sort(key=lambda o: o.genel_ilerleme())
        
        if limit is not None and limit > 0:
            return risk_altindaki_ogrenciler[:limit]
            
        return risk_altindaki_ogrenciler
    
    @staticmethod
    def get_all_ogrenciler(search_term=None, sort_by='numara', sort_order='asc'):
        """
        Tüm öğrencileri getir, isteğe bağlı filtreleme ve sıralama ile
        
        Args:
            search_term: Arama terimi (numara, ad, soyad)
            sort_by: Sıralama alanı ('numara', 'ad', 'soyad', 'sinif')
            sort_order: Sıralama yönü ('asc', 'desc')
            
        Returns:
            Öğrencilerin listesi
        """
        query = Ogrenci.query
        
        # Arama filtresi uygula
        if search_term:
            search_term = f"%{search_term}%"
            query = query.filter(
                (Ogrenci.numara.like(search_term)) |
                (Ogrenci.ad.like(search_term)) |
                (Ogrenci.soyad.like(search_term))
            )
        
        # Sıralama uygula
        if sort_by == 'ad':
            order_column = Ogrenci.ad
        elif sort_by == 'soyad':
            order_column = Ogrenci.soyad
        elif sort_by == 'sinif':
            order_column = Ogrenci.sinif
        else:
            order_column = Ogrenci.numara
            
        if sort_order == 'desc':
            order_column = order_column.desc()
            
        query = query.order_by(order_column)
        
        return query.all()
    
    @staticmethod
    def get_ogrenci_by_id(ogrenci_id):
        """
        ID'ye göre öğrenci getir
        
        Args:
            ogrenci_id: Öğrenci ID
            
        Returns:
            Öğrenci nesnesi veya None
        """
        return Ogrenci.query.get(ogrenci_id)
    
    @staticmethod
    def get_ogrenci_by_numara(numara):
        """
        Numaraya göre öğrenci getir
        
        Args:
            numara: Öğrenci numarası
            
        Returns:
            Öğrenci nesnesi veya None
        """
        return Ogrenci.query.filter_by(numara=numara).first()
    
    @staticmethod
    def create_ogrenci(numara, ad, soyad, sinif, cinsiyet, telefon=None, eposta=None):
        """
        Yeni öğrenci oluştur
        
        Args:
            numara: Öğrenci numarası
            ad: Ad
            soyad: Soyad
            sinif: Sınıf
            cinsiyet: Cinsiyet
            telefon: Telefon (opsiyonel)
            eposta: E-posta (opsiyonel)
            
        Returns:
            Dict: İşlem sonucunu ve oluşturulan öğrenci ID'sini içeren sözlük
        """
        # Numara kontrolü
        existing = Ogrenci.query.filter_by(numara=numara).first()
        if existing:
            return {
                'success': False, 
                'message': f"'{numara}' numaralı öğrenci zaten kayıtlı."
            }
        
        # Yeni öğrenci oluştur
        ogrenci = Ogrenci(
            numara=numara,
            ad=ad,
            soyad=soyad,
            sinif=sinif,
            cinsiyet=cinsiyet,
            telefon=telefon,
            eposta=eposta
        )
        
        try:
            db.session.add(ogrenci)
            db.session.commit()
            return {
                'success': True,
                'message': 'Öğrenci başarıyla eklendi.',
                'id': ogrenci.id
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def update_ogrenci(ogrenci_id, numara, ad, soyad, sinif, cinsiyet, telefon=None, eposta=None):
        """
        Öğrenci bilgilerini güncelle
        
        Args:
            ogrenci_id: Öğrenci ID
            numara: Öğrenci numarası
            ad: Ad
            soyad: Soyad
            sinif: Sınıf
            cinsiyet: Cinsiyet
            telefon: Telefon (opsiyonel)
            eposta: E-posta (opsiyonel)
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        ogrenci = Ogrenci.query.get(ogrenci_id)
        if not ogrenci:
            return {
                'success': False,
                'message': 'Öğrenci bulunamadı.'
            }
        
        # Numara benzersizlik kontrolü
        if numara != ogrenci.numara:
            existing = Ogrenci.query.filter_by(numara=numara).first()
            if existing:
                return {
                    'success': False, 
                    'message': f"'{numara}' numaralı başka bir öğrenci zaten kayıtlı."
                }
        
        # Bilgileri güncelle
        ogrenci.numara = numara
        ogrenci.ad = ad
        ogrenci.soyad = soyad
        ogrenci.sinif = sinif
        ogrenci.cinsiyet = cinsiyet
        ogrenci.telefon = telefon
        ogrenci.eposta = eposta
        
        try:
            db.session.commit()
            return {
                'success': True,
                'message': 'Öğrenci bilgileri başarıyla güncellendi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def delete_ogrenci(ogrenci_id):
        """
        Öğrenciyi ve ilişkili kayıtları sil
        
        Args:
            ogrenci_id: Öğrenci ID
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        ogrenci = Ogrenci.query.get(ogrenci_id)
        if not ogrenci:
            return {
                'success': False,
                'message': 'Öğrenci bulunamadı.'
            }
        
        try:
            # İlişkili anket atamalarını silme
            # Not: Anket modülü geçici olarak devre dışı bırakıldı
            # from app.blueprints.rehberlik_anketleri.models import AnketAtama
            # anket_atamalari = AnketAtama.query.filter_by(ogrenci_id=ogrenci_id).all()
            # for atama in anket_atamalari:
            #     db.session.delete(atama)
            
            # Öğrenciyi silme
            db.session.delete(ogrenci)
            db.session.commit()
            return {
                'success': True,
                'message': 'Öğrenci ve ilişkili tüm verileri başarıyla silindi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def get_ogrenci_sayisi():
        """
        Toplam öğrenci sayısını getir
        
        Returns:
            int: Toplam öğrenci sayısı
        """
        return Ogrenci.query.count()
    
    @staticmethod
    def import_ogrenciler_from_excel(file):
        """
        Excel dosyasından öğrenci verilerini içe aktar
        
        Args:
            file: Excel dosyası
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Excel dosyasını oku
            df = pd.read_excel(file)
            
            # Zorunlu alanları kontrol et
            required_columns = ['numara', 'ad', 'soyad', 'sinif', 'cinsiyet']
            for col in required_columns:
                if col not in df.columns:
                    return {
                        'success': False,
                        'message': f"Excel dosyasında '{col}' sütunu bulunamadı."
                    }
            
            # İçe aktarma istatistikleri
            stats = {
                'success': 0,
                'error': 0,
                'total': len(df),
                'errors': []
            }
            
            # Öğrencileri ekle
            for idx, row in df.iterrows():
                numara = str(row['numara']).strip()
                ad = str(row['ad']).strip()
                soyad = str(row['soyad']).strip()
                sinif = str(row['sinif']).strip()
                cinsiyet = str(row['cinsiyet']).strip()
                
                # Opsiyonel alanlar
                telefon = str(row['telefon']) if 'telefon' in row and pd.notna(row['telefon']) else None
                eposta = str(row['eposta']) if 'eposta' in row and pd.notna(row['eposta']) else None
                
                # Öğrenciyi ekle
                result = OgrenciService.create_ogrenci(
                    numara, ad, soyad, sinif, cinsiyet, telefon, eposta
                )
                
                if result['success']:
                    stats['success'] += 1
                else:
                    stats['error'] += 1
                    stats['errors'].append(f"Satır {idx+2}: {result['message']}")
            
            # Sonucu döndür
            if stats['error'] == 0:
                return {
                    'success': True,
                    'message': f"Toplam {stats['success']} öğrenci başarıyla içe aktarıldı."
                }
            else:
                return {
                    'success': True,
                    'message': f"Toplam {stats['success']} öğrenci içe aktarıldı, {stats['error']} hata oluştu.",
                    'errors': stats['errors']
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Excel dosyası okunurken hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def get_ogrenci_ilerleme_durumu(ogrenci_id):
        """
        Öğrencinin ders ilerleme durumunu getir
        
        Args:
            ogrenci_id: Öğrenci ID
            
        Returns:
            Dict: Ders ilerlemeleri, genel ilerleme ve hedef tarihi içeren sözlük
        """
        from app.blueprints.ders_konu_yonetimi.models import Ders
        
        ogrenci = Ogrenci.query.get(ogrenci_id)
        if not ogrenci:
            return None
            
        # Ders ilerlemelerini al
        ilerlemeler = DersIlerleme.query.filter_by(ogrenci_id=ogrenci_id).all()
        
        # Ders detaylarını ekle
        ders_ilerlemeleri = []
        for ilerleme in ilerlemeler:
            ders = Ders.query.get(ilerleme.ders_id)
            if ders:
                ders_ilerlemeleri.append({
                    'ders_id': ders.id,
                    'ders_adi': ders.ad,
                    'ilerleme_yuzdesi': ilerleme.tamamlama_yuzdesi,
                    'tahmini_bitis': ilerleme.tahmini_bitis_tarihi,
                    'son_guncelleme': ilerleme.son_guncelleme
                })
        
        # Genel ilerlemeyi hesapla
        genel_ilerleme = ogrenci.genel_ilerleme()
        
        # En son bitiş tahminini bul
        hedef_tarih = None
        for ilerleme in ilerlemeler:
            if ilerleme.tahmini_bitis_tarihi:
                if hedef_tarih is None or ilerleme.tahmini_bitis_tarihi > hedef_tarih:
                    hedef_tarih = ilerleme.tahmini_bitis_tarihi
        
        return {
            'ders_ilerlemeleri': ders_ilerlemeleri,
            'genel_ilerleme': genel_ilerleme,
            'hedef_tarih': hedef_tarih
        }

# Eski import'ların çalışmasını sağlamak için
# Bu satırı eklemeyin, çünkü döngüsel bir import yaratır
# from app.services.ogrenci_service import *