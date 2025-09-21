"""
Ders işlemleri için servis modülü
Bu modül, ders ve konu işlemleri ile ilgili iş mantığı işlemlerini gerçekleştirir.
"""
import re
import pandas as pd
from sqlalchemy import func

from app.extensions import db
from app.blueprints.ders.models import Ders, Konu

class DersService:
    """Ders işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def get_all_dersler(sort_by='ad', sort_order='asc'):
        """
        Tüm dersleri getir, isteğe bağlı sıralama ile
        
        Args:
            sort_by: Sıralama alanı ('ad', 'id')
            sort_order: Sıralama yönü ('asc', 'desc')
            
        Returns:
            Derslerin listesi
        """
        query = Ders.query
        
        # Sıralama uygula
        if sort_by == 'id':
            order_column = Ders.id
        else:
            order_column = Ders.ad
            
        if sort_order == 'desc':
            order_column = order_column.desc()
            
        query = query.order_by(order_column)
        
        return query.all()
    
    @staticmethod
    def get_ders_by_id(ders_id):
        """
        ID'ye göre ders getir
        
        Args:
            ders_id: Ders ID
            
        Returns:
            Ders nesnesi veya None
        """
        return Ders.query.get(ders_id)
    
    @staticmethod
    def create_ders(ad, aciklama=None):
        """
        Yeni ders oluştur
        
        Args:
            ad: Ders adı
            aciklama: Açıklama (opsiyonel)
            
        Returns:
            Dict: İşlem sonucunu ve oluşturulan ders ID'sini içeren sözlük
        """
        # Ad kontrolü
        existing = Ders.query.filter_by(ad=ad).first()
        if existing:
            return {
                'success': False, 
                'message': f"'{ad}' adlı ders zaten kayıtlı."
            }
        
        # Yeni ders oluştur
        ders = Ders(
            ad=ad,
            aciklama=aciklama
        )
        
        try:
            db.session.add(ders)
            db.session.commit()
            return {
                'success': True,
                'message': 'Ders başarıyla eklendi.',
                'id': ders.id
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def update_ders(ders_id, ad, aciklama=None):
        """
        Ders bilgilerini güncelle
        
        Args:
            ders_id: Ders ID
            ad: Ders adı
            aciklama: Açıklama (opsiyonel)
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        ders = Ders.query.get(ders_id)
        if not ders:
            return {
                'success': False,
                'message': 'Ders bulunamadı.'
            }
        
        # Ad benzersizlik kontrolü
        if ad != ders.ad:
            existing = Ders.query.filter_by(ad=ad).first()
            if existing:
                return {
                    'success': False, 
                    'message': f"'{ad}' adlı başka bir ders zaten kayıtlı."
                }
        
        # Bilgileri güncelle
        ders.ad = ad
        ders.aciklama = aciklama
        
        try:
            db.session.commit()
            return {
                'success': True,
                'message': 'Ders bilgileri başarıyla güncellendi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def delete_ders(ders_id):
        """
        Dersi sil
        
        Args:
            ders_id: Ders ID
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        ders = Ders.query.get(ders_id)
        if not ders:
            return {
                'success': False,
                'message': 'Ders bulunamadı.'
            }
        
        try:
            db.session.delete(ders)
            db.session.commit()
            return {
                'success': True,
                'message': 'Ders başarıyla silindi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def get_konular_by_ders_id(ders_id):
        """
        Derse ait konuları getir
        
        Args:
            ders_id: Ders ID
            
        Returns:
            Konuların listesi
        """
        return Konu.query.filter_by(ders_id=ders_id).order_by(Konu.sira).all()
    
    @staticmethod
    def get_konu_by_id(konu_id):
        """
        ID'ye göre konu getir
        
        Args:
            konu_id: Konu ID
            
        Returns:
            Konu nesnesi veya None
        """
        return Konu.query.get(konu_id)
    
    @staticmethod
    def create_konu(ders_id, ad, tahmini_sure, sira=None):
        """
        Yeni konu oluştur
        
        Args:
            ders_id: Ders ID
            ad: Konu adı
            tahmini_sure: Tahmini çalışma süresi (dakika)
            sira: Sıra numarası (opsiyonel)
            
        Returns:
            Dict: İşlem sonucunu ve oluşturulan konu ID'sini içeren sözlük
        """
        # Ders kontrolü
        ders = Ders.query.get(ders_id)
        if not ders:
            return {
                'success': False, 
                'message': 'Ders bulunamadı.'
            }
        
        # Sıra numarası belirtilmemişse, son sıraya ekle
        if sira is None:
            max_sira = db.session.query(func.max(Konu.sira)).filter_by(ders_id=ders_id).scalar()
            sira = (max_sira or 0) + 1
        
        # Yeni konu oluştur
        konu = Konu(
            ders_id=ders_id,
            ad=ad,
            tahmini_sure=tahmini_sure,
            sira=sira
        )
        
        try:
            db.session.add(konu)
            db.session.commit()
            return {
                'success': True,
                'message': 'Konu başarıyla eklendi.',
                'id': konu.id
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def update_konu(konu_id, ad, tahmini_sure, sira=None):
        """
        Konu bilgilerini güncelle
        
        Args:
            konu_id: Konu ID
            ad: Konu adı
            tahmini_sure: Tahmini çalışma süresi (dakika)
            sira: Sıra numarası (opsiyonel)
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        konu = Konu.query.get(konu_id)
        if not konu:
            return {
                'success': False,
                'message': 'Konu bulunamadı.'
            }
        
        # Bilgileri güncelle
        konu.ad = ad
        konu.tahmini_sure = tahmini_sure
        if sira is not None:
            konu.sira = sira
        
        try:
            db.session.commit()
            return {
                'success': True,
                'message': 'Konu bilgileri başarıyla güncellendi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def delete_konu(konu_id):
        """
        Konuyu sil
        
        Args:
            konu_id: Konu ID
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        konu = Konu.query.get(konu_id)
        if not konu:
            return {
                'success': False,
                'message': 'Konu bulunamadı.'
            }
        
        try:
            db.session.delete(konu)
            db.session.commit()
            return {
                'success': True,
                'message': 'Konu başarıyla silindi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def import_konular_from_text(ders_id, konular_text):
        """
        Metin alanından konuları toplu olarak içe aktar
        
        Args:
            ders_id: Ders ID
            konular_text: Konuların bulunduğu metin
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        # Ders kontrolü
        ders = Ders.query.get(ders_id)
        if not ders:
            return {
                'success': False, 
                'message': 'Ders bulunamadı.'
            }
        
        # Satırları ayrıştır ve boş satırları temizle
        lines = [line.strip() for line in konular_text.split('\n') if line.strip()]
        
        # İçe aktarma istatistikleri
        stats = {
            'success': 0,
            'error': 0,
            'total': len(lines),
            'errors': []
        }
        
        # Son sıra numarasını bul
        max_sira = db.session.query(func.max(Konu.sira)).filter_by(ders_id=ders_id).scalar() or 0
        current_sira = max_sira + 1
        
        # Konuları ekle
        for line in lines:
            # Konu adı ve tahmini süre formatı: "Konu adı - 45" (dakika)
            match = re.match(r'(.+?)\s*-\s*(\d+)$', line)
            
            if match:
                konu_adi = match.group(1).strip()
                tahmini_sure = int(match.group(2))
                
                # Yeni konu oluştur
                result = DersService.create_konu(
                    ders_id, konu_adi, tahmini_sure, current_sira
                )
                
                if result['success']:
                    stats['success'] += 1
                    current_sira += 1
                else:
                    stats['error'] += 1
                    stats['errors'].append(f"Satır: {line} - {result['message']}")
            else:
                # Format uyumsuzsa, varsayılan süreyi 45 dakika olarak ayarla
                konu_adi = line.strip()
                tahmini_sure = 45
                
                # Yeni konu oluştur
                result = DersService.create_konu(
                    ders_id, konu_adi, tahmini_sure, current_sira
                )
                
                if result['success']:
                    stats['success'] += 1
                    current_sira += 1
                else:
                    stats['error'] += 1
                    stats['errors'].append(f"Satır: {line} - {result['message']}")
        
        # Sonucu döndür
        if stats['error'] == 0:
            return {
                'success': True,
                'message': f"Toplam {stats['success']} konu başarıyla içe aktarıldı."
            }
        else:
            return {
                'success': True,
                'message': f"Toplam {stats['success']} konu içe aktarıldı, {stats['error']} hata oluştu.",
                'errors': stats['errors']
            }
    
    @staticmethod
    def import_dersler_from_excel(file):
        """
        Excel dosyasından ders ve konu verilerini içe aktar
        
        Args:
            file: Excel dosyası
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Excel dosyasını oku
            xls = pd.ExcelFile(file)
            
            # Excel'de sayfa kontrolü
            if 'Dersler' not in xls.sheet_names:
                return {
                    'success': False,
                    'message': "Excel dosyasında 'Dersler' sayfası bulunamadı."
                }
            
            # Dersleri oku
            df_dersler = pd.read_excel(xls, 'Dersler')
            
            # Zorunlu alanları kontrol et
            if 'ders_adi' not in df_dersler.columns:
                return {
                    'success': False,
                    'message': "Excel dosyasında 'ders_adi' sütunu bulunamadı."
                }
            
            # İçe aktarma istatistikleri
            stats = {
                'dersler': {'success': 0, 'error': 0, 'total': len(df_dersler)},
                'konular': {'success': 0, 'error': 0, 'total': 0},
                'errors': []
            }
            
            # Dersleri içe aktar
            for _, row in df_dersler.iterrows():
                ders_adi = str(row['ders_adi']).strip()
                aciklama = str(row['aciklama']) if 'aciklama' in row and pd.notna(row['aciklama']) else None
                
                # Dersi oluştur
                ders_result = DersService.create_ders(ders_adi, aciklama)
                
                if ders_result['success']:
                    stats['dersler']['success'] += 1
                    
                    # Konu sayfası var mı kontrol et
                    konu_sayfa_adi = f"Konular_{ders_adi}"
                    if konu_sayfa_adi in xls.sheet_names:
                        # Konuları oku
                        df_konular = pd.read_excel(xls, konu_sayfa_adi)
                        
                        # Zorunlu alanları kontrol et
                        if 'konu_adi' in df_konular.columns:
                            stats['konular']['total'] += len(df_konular)
                            
                            # Konuları ekle
                            for k_idx, k_row in df_konular.iterrows():
                                konu_adi = str(k_row['konu_adi']).strip()
                                tahmini_sure = int(k_row['tahmini_sure']) if 'tahmini_sure' in k_row and pd.notna(k_row['tahmini_sure']) else 45
                                sira = int(k_row['sira']) if 'sira' in k_row and pd.notna(k_row['sira']) else k_idx + 1
                                
                                # Konuyu oluştur
                                konu_result = DersService.create_konu(
                                    ders_result['id'], konu_adi, tahmini_sure, sira
                                )
                                
                                if konu_result['success']:
                                    stats['konular']['success'] += 1
                                else:
                                    stats['konular']['error'] += 1
                                    stats['errors'].append(f"{ders_adi} - Konu: {konu_adi} - {konu_result['message']}")
                else:
                    stats['dersler']['error'] += 1
                    stats['errors'].append(f"Ders: {ders_adi} - {ders_result['message']}")
            
            # Sonucu döndür
            if stats['dersler']['error'] == 0 and stats['konular']['error'] == 0:
                return {
                    'success': True,
                    'message': f"Toplam {stats['dersler']['success']} ders ve {stats['konular']['success']} konu başarıyla içe aktarıldı."
                }
            else:
                return {
                    'success': True,
                    'message': f"Toplam {stats['dersler']['success']} ders ve {stats['konular']['success']} konu içe aktarıldı, {stats['dersler']['error'] + stats['konular']['error']} hata oluştu.",
                    'errors': stats['errors']
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Excel dosyası okunurken hata oluştu: {str(e)}"
            }

# Eski import'ların çalışmasını sağlamak için
# Bu satırı eklemeyin, çünkü döngüsel bir import yaratır
# from app.services.ders_service import *