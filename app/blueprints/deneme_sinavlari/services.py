"""
Deneme işlemleri için servis modülü
Bu modül, deneme sınavı sonuçları ile ilgili iş mantığı işlemlerini gerçekleştirir.
"""
from datetime import datetime
import pandas as pd

from app.extensions import db
from app.blueprints.deneme.models import DenemeSonuc
from app.blueprints.ogrenci_yonetimi.models import Ogrenci

class DenemeService:
    """Deneme sınavı işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def get_deneme_sonuclari_by_ogrenci_id(ogrenci_id):
        """
        Öğrenciye ait deneme sonuçlarını getir
        
        Args:
            ogrenci_id: Öğrenci ID
            
        Returns:
            Deneme sonuçları listesi
        """
        return DenemeSonuc.query.filter_by(ogrenci_id=ogrenci_id).order_by(DenemeSonuc.tarih.desc()).all()
    
    @staticmethod
    def get_deneme_sonuc_by_id(sonuc_id):
        """
        ID'ye göre deneme sonucu getir
        
        Args:
            sonuc_id: Sonuç ID
            
        Returns:
            Deneme sonucu nesnesi veya None
        """
        return DenemeSonuc.query.get(sonuc_id)
    
    @staticmethod
    def create_deneme_sonuc(ogrenci_id, deneme_adi, tarih, 
                           net_tyt_turkce=0, net_tyt_sosyal=0, net_tyt_matematik=0, net_tyt_fen=0,
                           net_ayt_matematik=0, net_ayt_fizik=0, net_ayt_kimya=0, net_ayt_biyoloji=0,
                           net_ayt_edebiyat=0, net_ayt_tarih=0, net_ayt_cografya=0, net_ayt_felsefe=0,
                           puan_tyt=0, puan_say=0, puan_ea=0, puan_soz=0):
        """
        Yeni deneme sonucu oluştur
        
        Args:
            ogrenci_id: Öğrenci ID
            deneme_adi: Deneme sınavının adı
            tarih: Deneme sınavının tarihi
            net_* ve puan_*: Sonuç değerleri
            
        Returns:
            Dict: İşlem sonucunu ve oluşturulan sonuç ID'sini içeren sözlük
        """
        # Öğrenci kontrolü
        ogrenci = Ogrenci.query.get(ogrenci_id)
        if not ogrenci:
            return {
                'success': False, 
                'message': 'Öğrenci bulunamadı.'
            }
        
        # Tarih formatı kontrolü ve çevirme
        if isinstance(tarih, str):
            try:
                tarih = datetime.strptime(tarih, '%Y-%m-%d').date()
            except ValueError:
                try:
                    tarih = datetime.strptime(tarih, '%d.%m.%Y').date()
                except ValueError:
                    return {
                        'success': False,
                        'message': 'Tarih formatı hatalı, YYYY-MM-DD veya DD.MM.YYYY formatında olmalıdır.'
                    }
        
        # Yeni deneme sonucu oluştur
        sonuc = DenemeSonuc(
            ogrenci_id=ogrenci_id,
            deneme_adi=deneme_adi,
            tarih=tarih,
            net_tyt_turkce=net_tyt_turkce,
            net_tyt_sosyal=net_tyt_sosyal,
            net_tyt_matematik=net_tyt_matematik,
            net_tyt_fen=net_tyt_fen,
            net_ayt_matematik=net_ayt_matematik,
            net_ayt_fizik=net_ayt_fizik,
            net_ayt_kimya=net_ayt_kimya,
            net_ayt_biyoloji=net_ayt_biyoloji,
            net_ayt_edebiyat=net_ayt_edebiyat,
            net_ayt_tarih=net_ayt_tarih,
            net_ayt_cografya=net_ayt_cografya,
            net_ayt_felsefe=net_ayt_felsefe,
            puan_tyt=puan_tyt,
            puan_say=puan_say,
            puan_ea=puan_ea,
            puan_soz=puan_soz
        )
        
        try:
            db.session.add(sonuc)
            db.session.commit()
            return {
                'success': True,
                'message': 'Deneme sonucu başarıyla eklendi.',
                'id': sonuc.id
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def update_deneme_sonuc(sonuc_id, deneme_adi, tarih, 
                           net_tyt_turkce=0, net_tyt_sosyal=0, net_tyt_matematik=0, net_tyt_fen=0,
                           net_ayt_matematik=0, net_ayt_fizik=0, net_ayt_kimya=0, net_ayt_biyoloji=0,
                           net_ayt_edebiyat=0, net_ayt_tarih=0, net_ayt_cografya=0, net_ayt_felsefe=0,
                           puan_tyt=0, puan_say=0, puan_ea=0, puan_soz=0):
        """
        Deneme sonucu bilgilerini güncelle
        
        Args:
            sonuc_id: Sonuç ID
            deneme_adi: Deneme sınavının adı
            tarih: Deneme sınavının tarihi
            net_* ve puan_*: Sonuç değerleri
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        sonuc = DenemeSonuc.query.get(sonuc_id)
        if not sonuc:
            return {
                'success': False,
                'message': 'Deneme sonucu bulunamadı.'
            }
        
        # Tarih formatı kontrolü ve çevirme
        if isinstance(tarih, str):
            try:
                tarih = datetime.strptime(tarih, '%Y-%m-%d').date()
            except ValueError:
                try:
                    tarih = datetime.strptime(tarih, '%d.%m.%Y').date()
                except ValueError:
                    return {
                        'success': False,
                        'message': 'Tarih formatı hatalı, YYYY-MM-DD veya DD.MM.YYYY formatında olmalıdır.'
                    }
        
        # Bilgileri güncelle
        sonuc.deneme_adi = deneme_adi
        sonuc.tarih = tarih
        sonuc.net_tyt_turkce = net_tyt_turkce
        sonuc.net_tyt_sosyal = net_tyt_sosyal
        sonuc.net_tyt_matematik = net_tyt_matematik
        sonuc.net_tyt_fen = net_tyt_fen
        sonuc.net_ayt_matematik = net_ayt_matematik
        sonuc.net_ayt_fizik = net_ayt_fizik
        sonuc.net_ayt_kimya = net_ayt_kimya
        sonuc.net_ayt_biyoloji = net_ayt_biyoloji
        sonuc.net_ayt_edebiyat = net_ayt_edebiyat
        sonuc.net_ayt_tarih = net_ayt_tarih
        sonuc.net_ayt_cografya = net_ayt_cografya
        sonuc.net_ayt_felsefe = net_ayt_felsefe
        sonuc.puan_tyt = puan_tyt
        sonuc.puan_say = puan_say
        sonuc.puan_ea = puan_ea
        sonuc.puan_soz = puan_soz
        
        try:
            db.session.commit()
            return {
                'success': True,
                'message': 'Deneme sonucu başarıyla güncellendi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def delete_deneme_sonuc(sonuc_id):
        """
        Deneme sonucunu sil
        
        Args:
            sonuc_id: Sonuç ID
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        sonuc = DenemeSonuc.query.get(sonuc_id)
        if not sonuc:
            return {
                'success': False,
                'message': 'Deneme sonucu bulunamadı.'
            }
        
        try:
            db.session.delete(sonuc)
            db.session.commit()
            return {
                'success': True,
                'message': 'Deneme sonucu başarıyla silindi.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            }
    
    @staticmethod
    def get_ogrenci_ilerleme_raporu(ogrenci_id):
        """
        Öğrencinin deneme sonuçlarına dayalı ilerleme raporunu oluştur
        
        Args:
            ogrenci_id: Öğrenci ID
            
        Returns:
            Dict: İlerleme raporu verilerini içeren sözlük
        """
        # Öğrenci kontrolü
        ogrenci = Ogrenci.query.get(ogrenci_id)
        if not ogrenci:
            return {
                'success': False, 
                'message': 'Öğrenci bulunamadı.'
            }
        
        # Deneme sonuçlarını getir (tarih sırasına göre)
        sonuclar = DenemeSonuc.query.filter_by(ogrenci_id=ogrenci_id).order_by(DenemeSonuc.tarih).all()
        
        if not sonuclar:
            return {
                'success': False, 
                'message': 'Öğrenciye ait deneme sonucu bulunamadı.'
            }
        
        # İlerleme verileri
        tarihler = [sonuc.tarih.strftime('%d.%m.%Y') for sonuc in sonuclar]
        deneme_adlari = [sonuc.deneme_adi for sonuc in sonuclar]
        
        # TYT net verileri
        tyt_turkce = [sonuc.net_tyt_turkce for sonuc in sonuclar]
        tyt_sosyal = [sonuc.net_tyt_sosyal for sonuc in sonuclar]
        tyt_matematik = [sonuc.net_tyt_matematik for sonuc in sonuclar]
        tyt_fen = [sonuc.net_tyt_fen for sonuc in sonuclar]
        tyt_toplam = [sonuc.tyt_toplam_net() for sonuc in sonuclar]
        
        # AYT net verileri
        ayt_matematik = [sonuc.net_ayt_matematik for sonuc in sonuclar]
        ayt_fizik = [sonuc.net_ayt_fizik for sonuc in sonuclar]
        ayt_kimya = [sonuc.net_ayt_kimya for sonuc in sonuclar]
        ayt_biyoloji = [sonuc.net_ayt_biyoloji for sonuc in sonuclar]
        ayt_fen_toplam = [sonuc.net_ayt_fizik + sonuc.net_ayt_kimya + sonuc.net_ayt_biyoloji for sonuc in sonuclar]
        
        ayt_edebiyat = [sonuc.net_ayt_edebiyat for sonuc in sonuclar]
        ayt_tarih = [sonuc.net_ayt_tarih for sonuc in sonuclar]
        ayt_cografya = [sonuc.net_ayt_cografya for sonuc in sonuclar]
        ayt_felsefe = [sonuc.net_ayt_felsefe for sonuc in sonuclar]
        ayt_sosyal_toplam = [sonuc.net_ayt_edebiyat + sonuc.net_ayt_tarih + sonuc.net_ayt_cografya + sonuc.net_ayt_felsefe for sonuc in sonuclar]
        
        ayt_toplam = [sonuc.ayt_toplam_net() for sonuc in sonuclar]
        
        # Puan verileri
        puan_tyt = [sonuc.puan_tyt for sonuc in sonuclar]
        puan_say = [sonuc.puan_say for sonuc in sonuclar]
        puan_ea = [sonuc.puan_ea for sonuc in sonuclar]
        puan_soz = [sonuc.puan_soz for sonuc in sonuclar]
        
        # İlerleme analizi: Son iki deneme arasındaki değişim
        if len(sonuclar) >= 2:
            son = sonuclar[-1]
            onceki = sonuclar[-2]
            
            degisim = {
                'tyt_turkce': son.net_tyt_turkce - onceki.net_tyt_turkce,
                'tyt_sosyal': son.net_tyt_sosyal - onceki.net_tyt_sosyal,
                'tyt_matematik': son.net_tyt_matematik - onceki.net_tyt_matematik,
                'tyt_fen': son.net_tyt_fen - onceki.net_tyt_fen,
                'tyt_toplam': son.tyt_toplam_net() - onceki.tyt_toplam_net(),
                
                'ayt_matematik': son.net_ayt_matematik - onceki.net_ayt_matematik,
                'ayt_fizik': son.net_ayt_fizik - onceki.net_ayt_fizik,
                'ayt_kimya': son.net_ayt_kimya - onceki.net_ayt_kimya,
                'ayt_biyoloji': son.net_ayt_biyoloji - onceki.net_ayt_biyoloji,
                
                'ayt_edebiyat': son.net_ayt_edebiyat - onceki.net_ayt_edebiyat,
                'ayt_tarih': son.net_ayt_tarih - onceki.net_ayt_tarih,
                'ayt_cografya': son.net_ayt_cografya - onceki.net_ayt_cografya,
                'ayt_felsefe': son.net_ayt_felsefe - onceki.net_ayt_felsefe,
                
                'ayt_toplam': son.ayt_toplam_net() - onceki.ayt_toplam_net(),
                
                'puan_tyt': son.puan_tyt - onceki.puan_tyt,
                'puan_say': son.puan_say - onceki.puan_say,
                'puan_ea': son.puan_ea - onceki.puan_ea,
                'puan_soz': son.puan_soz - onceki.puan_soz,
            }
        else:
            degisim = None
        
        # Sonucu döndür
        return {
            'success': True,
            'ogrenci': {
                'id': ogrenci.id,
                'numara': ogrenci.numara,
                'ad_soyad': f"{ogrenci.ad} {ogrenci.soyad}",
                'sinif': ogrenci.sinif
            },
            'deneme_sayisi': len(sonuclar),
            'son_deneme': {
                'id': sonuclar[-1].id,
                'deneme_adi': sonuclar[-1].deneme_adi,
                'tarih': sonuclar[-1].tarih.strftime('%d.%m.%Y'),
                'tyt_toplam': sonuclar[-1].tyt_toplam_net(),
                'ayt_toplam': sonuclar[-1].ayt_toplam_net(),
                'puan_tyt': sonuclar[-1].puan_tyt,
                'puan_say': sonuclar[-1].puan_say,
                'puan_ea': sonuclar[-1].puan_ea,
                'puan_soz': sonuclar[-1].puan_soz
            },
            'tarihler': tarihler,
            'deneme_adlari': deneme_adlari,
            'tyt': {
                'turkce': tyt_turkce,
                'sosyal': tyt_sosyal,
                'matematik': tyt_matematik,
                'fen': tyt_fen,
                'toplam': tyt_toplam
            },
            'ayt': {
                'matematik': ayt_matematik,
                'fizik': ayt_fizik,
                'kimya': ayt_kimya,
                'biyoloji': ayt_biyoloji,
                'fen_toplam': ayt_fen_toplam,
                'edebiyat': ayt_edebiyat,
                'tarih': ayt_tarih,
                'cografya': ayt_cografya,
                'felsefe': ayt_felsefe,
                'sosyal_toplam': ayt_sosyal_toplam,
                'toplam': ayt_toplam
            },
            'puanlar': {
                'tyt': puan_tyt,
                'say': puan_say,
                'ea': puan_ea,
                'soz': puan_soz
            },
            'degisim': degisim
        }
    
    @staticmethod
    def import_deneme_sonuclari_from_excel(file, ogrenci_id=None):
        """
        Excel dosyasından deneme sonuçlarını içe aktar
        
        Args:
            file: Excel dosyası
            ogrenci_id: Belirli bir öğrenci ID (opsiyonel)
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Excel dosyasını oku
            df = pd.read_excel(file)
            
            # Zorunlu alanları kontrol et
            gerekli_sutunlar = ['ogrenci_numara', 'deneme_adi', 'tarih']
            for sutun in gerekli_sutunlar:
                if sutun not in df.columns:
                    return {
                        'success': False,
                        'message': f"Excel dosyasında '{sutun}' sütunu bulunamadı."
                    }
            
            # İçe aktarma istatistikleri
            stats = {
                'success': 0,
                'error': 0,
                'total': len(df),
                'errors': []
            }
            
            # Deneme sonuçlarını ekle
            for _, row in df.iterrows():
                # Öğrenci numarasına göre öğrenciyi bul
                if ogrenci_id:
                    # Belirli bir öğrenci ID belirtilmişse, sadece o öğrencinin sonuçlarını ekle
                    o_id = ogrenci_id
                else:
                    # Numaraya göre öğrenciyi bul
                    ogrenci_numara = str(row['ogrenci_numara']).strip()
                    ogrenci = Ogrenci.query.filter_by(numara=ogrenci_numara).first()
                    if not ogrenci:
                        stats['error'] += 1
                        stats['errors'].append(f"Satır {_+2}: Öğrenci bulunamadı: {ogrenci_numara}")
                        continue
                    o_id = ogrenci.id
                
                # Deneme adı ve tarih
                deneme_adi = str(row['deneme_adi']).strip()
                
                # Tarih formatı kontrolü ve çevirme
                try:
                    if isinstance(row['tarih'], str):
                        tarih = datetime.strptime(row['tarih'], '%Y-%m-%d').date()
                    else:
                        tarih = row['tarih']
                except ValueError:
                    stats['error'] += 1
                    stats['errors'].append(f"Satır {_+2}: Tarih formatı hatalı: {row['tarih']}")
                    continue
                
                # Net ve puan değerlerini al
                net_tyt_turkce = float(row['net_tyt_turkce']) if 'net_tyt_turkce' in row and pd.notna(row['net_tyt_turkce']) else 0
                net_tyt_sosyal = float(row['net_tyt_sosyal']) if 'net_tyt_sosyal' in row and pd.notna(row['net_tyt_sosyal']) else 0
                net_tyt_matematik = float(row['net_tyt_matematik']) if 'net_tyt_matematik' in row and pd.notna(row['net_tyt_matematik']) else 0
                net_tyt_fen = float(row['net_tyt_fen']) if 'net_tyt_fen' in row and pd.notna(row['net_tyt_fen']) else 0
                
                net_ayt_matematik = float(row['net_ayt_matematik']) if 'net_ayt_matematik' in row and pd.notna(row['net_ayt_matematik']) else 0
                net_ayt_fizik = float(row['net_ayt_fizik']) if 'net_ayt_fizik' in row and pd.notna(row['net_ayt_fizik']) else 0
                net_ayt_kimya = float(row['net_ayt_kimya']) if 'net_ayt_kimya' in row and pd.notna(row['net_ayt_kimya']) else 0
                net_ayt_biyoloji = float(row['net_ayt_biyoloji']) if 'net_ayt_biyoloji' in row and pd.notna(row['net_ayt_biyoloji']) else 0
                
                net_ayt_edebiyat = float(row['net_ayt_edebiyat']) if 'net_ayt_edebiyat' in row and pd.notna(row['net_ayt_edebiyat']) else 0
                net_ayt_tarih = float(row['net_ayt_tarih']) if 'net_ayt_tarih' in row and pd.notna(row['net_ayt_tarih']) else 0
                net_ayt_cografya = float(row['net_ayt_cografya']) if 'net_ayt_cografya' in row and pd.notna(row['net_ayt_cografya']) else 0
                net_ayt_felsefe = float(row['net_ayt_felsefe']) if 'net_ayt_felsefe' in row and pd.notna(row['net_ayt_felsefe']) else 0
                
                puan_tyt = float(row['puan_tyt']) if 'puan_tyt' in row and pd.notna(row['puan_tyt']) else 0
                puan_say = float(row['puan_say']) if 'puan_say' in row and pd.notna(row['puan_say']) else 0
                puan_ea = float(row['puan_ea']) if 'puan_ea' in row and pd.notna(row['puan_ea']) else 0
                puan_soz = float(row['puan_soz']) if 'puan_soz' in row and pd.notna(row['puan_soz']) else 0
                
                # Sonucu oluştur
                result = DenemeService.create_deneme_sonuc(
                    ogrenci_id=o_id,
                    deneme_adi=deneme_adi,
                    tarih=tarih,
                    net_tyt_turkce=net_tyt_turkce,
                    net_tyt_sosyal=net_tyt_sosyal,
                    net_tyt_matematik=net_tyt_matematik,
                    net_tyt_fen=net_tyt_fen,
                    net_ayt_matematik=net_ayt_matematik,
                    net_ayt_fizik=net_ayt_fizik,
                    net_ayt_kimya=net_ayt_kimya,
                    net_ayt_biyoloji=net_ayt_biyoloji,
                    net_ayt_edebiyat=net_ayt_edebiyat,
                    net_ayt_tarih=net_ayt_tarih,
                    net_ayt_cografya=net_ayt_cografya,
                    net_ayt_felsefe=net_ayt_felsefe,
                    puan_tyt=puan_tyt,
                    puan_say=puan_say,
                    puan_ea=puan_ea,
                    puan_soz=puan_soz
                )
                
                if result['success']:
                    stats['success'] += 1
                else:
                    stats['error'] += 1
                    stats['errors'].append(f"Satır {_+2}: {result['message']}")
            
            # Sonucu döndür
            if stats['error'] == 0:
                return {
                    'success': True,
                    'message': f"Toplam {stats['success']} deneme sonucu başarıyla içe aktarıldı."
                }
            else:
                return {
                    'success': True,
                    'message': f"Toplam {stats['success']} deneme sonucu içe aktarıldı, {stats['error']} hata oluştu.",
                    'errors': stats['errors']
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Excel dosyası okunurken hata oluştu: {str(e)}"
            }