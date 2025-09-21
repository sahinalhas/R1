"""
Yapay Zeka Asistanı işlemleri için servis modülü.
Bu modül, yapay zeka ile ilgili iş mantığı işlemlerini gerçekleştirir.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import joblib

from app.extensions import db
from app.blueprints.yapay_zeka_asistan.models import (
    YapayZekaModel, YapayZekaAnaliz, OgrenciAnaliz, OgrenciOneri, DuyguAnalizi
)
from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from app.blueprints.deneme_sinavlari.models import DenemeSonuc
from app.blueprints.calisma_programi.models import DersIlerleme

# Model dosyalarının kaydedileceği klasör
MODEL_DIR = os.path.join('app', 'blueprints', 'yapay_zeka_asistan', 'model_files')
os.makedirs(MODEL_DIR, exist_ok=True)

class YapayZekaService:
    """Yapay zeka işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def get_modeller(aktif_mi=None):
        """
        Yapay zeka modellerini getir, isteğe bağlı olarak aktif filtrelemesi yapabilir
        
        Args:
            aktif_mi: Aktif filtresi (True, False veya None)
            
        Returns:
            List: Model listesi
        """
        query = YapayZekaModel.query
        
        if aktif_mi is not None:
            query = query.filter_by(aktif=aktif_mi)
            
        return query.order_by(YapayZekaModel.olusturma_tarihi.desc()).all()
    
    @staticmethod
    def get_model(model_id):
        """
        ID'ye göre yapay zeka modelini getir
        
        Args:
            model_id: Model ID
            
        Returns:
            YapayZekaModel: Model nesnesi veya None
        """
        return YapayZekaModel.query.get(model_id)
    
    @staticmethod
    def olustur_akademik_risk_modeli(sinif=None, model_tipi='gelismis'):
        """
        Akademik risk modeli oluştur - Geliştirilmiş versiyon
        
        Args:
            sinif: Sınıf filtresi (örn: '9', '10', '11', '12' veya None)
            model_tipi: Model tipi ('temel', 'gelismis' veya 'kapsamli')
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Öğrenci verilerini al
            ogrenciler = Ogrenci.query.all()
            if not ogrenciler:
                return {
                    'success': False,
                    'message': 'Sistem içerisinde yeterli sayıda öğrenci verisi bulunmuyor.'
                }
            
            # Veri hazırlama
            veri = []
            for ogrenci in ogrenciler:
                # Sınıf filtrelemesi
                if sinif and ogrenci.sinif.startswith(sinif):
                    continue
                
                # Deneme sınavı sonuçları
                sonuclar = DenemeSonuc.query.filter_by(ogrenci_id=ogrenci.id).all()
                
                # İlerleme durumları
                ilerlemeler = DersIlerleme.query.filter_by(ogrenci_id=ogrenci.id).all()
                
                # Temel özellikler hesaplama (Deneme sınavı ortalaması)
                if sonuclar:
                    ort_net = sum(s.toplam_net for s in sonuclar) / len(sonuclar)
                    ort_dogru = sum(s.toplam_dogru for s in sonuclar) / len(sonuclar)
                    ort_yanlis = sum(s.toplam_yanlis for s in sonuclar) / len(sonuclar)
                    
                    # Gelişmiş model için zaman içindeki trend hesaplamaları
                    if len(sonuclar) >= 2 and model_tipi in ['gelismis', 'kapsamli']:
                        # Sonuçları tarihe göre sırala
                        sirali_sonuclar = sorted(sonuclar, key=lambda s: s.sinav_tarihi if s.sinav_tarihi else datetime.now())
                        
                        # Son 3 sınavdaki değişim trendini hesapla
                        son_sonuclar = sirali_sonuclar[-3:] if len(sirali_sonuclar) >= 3 else sirali_sonuclar
                        net_degisim = son_sonuclar[-1].toplam_net - son_sonuclar[0].toplam_net
                        
                        # Trend skorunu -1 ile 1 arasında normalize et
                        trend_skoru = min(max(net_degisim / (son_sonuclar[0].toplam_net + 0.1), -1), 1)
                    else:
                        trend_skoru = 0
                else:
                    ort_net = 0
                    ort_dogru = 0
                    ort_yanlis = 0
                    trend_skoru = 0
                
                # İlerleme durumu
                ilerleme_yuzdesi = ogrenci.genel_ilerleme()
                
                # Devamsızlık (varsayılan olarak sıfır, gerçek veri geldiğinde güncellenecek)
                devamsizlik = 0  # İleride eklenecek
                
                # Kapsamlı model için ek özellikler
                if model_tipi == 'kapsamli':
                    # Düzenli çalışma süreleri (haftalık ortalama)
                    haftalik_calisma_saati = 0  # İleride ders programı verilerinden hesaplanacak
                    
                    # Anket sonuçlarından motivasyon skoru
                    motivasyon_skoru = 0  # İleride anket verilerinden hesaplanacak
                    
                    # Hedeflerin belirlenme oranı
                    hedef_belirleme_orani = 0  # İleride hedef listesinden hesaplanacak
                else:
                    haftalik_calisma_saati = 0
                    motivasyon_skoru = 0
                    hedef_belirleme_orani = 0
                
                # Risk durumu (manuel etiketleme)
                # Not: Gerçek modelde bu veri önceden etiketlenmiş olmalı
                # Burada örnek bir kuralla otomatik etiketleme yapıyoruz
                if model_tipi == 'temel':
                    risk = 1 if (ort_net < 20 or ilerleme_yuzdesi < 30 or devamsizlik > 10) else 0
                elif model_tipi == 'gelismis':
                    # Trend faktörünü de dahil et
                    risk = 1 if (ort_net < 20 or ilerleme_yuzdesi < 30 or trend_skoru < -0.3 or devamsizlik > 10) else 0
                else:  # kapsamlı
                    # Daha kapsamlı risk hesaplama
                    risk_puani = 0
                    risk_puani += 1 if ort_net < 20 else 0
                    risk_puani += 1 if ilerleme_yuzdesi < 30 else 0
                    risk_puani += 1 if trend_skoru < -0.3 else 0
                    risk_puani += 1 if devamsizlik > 10 else 0
                    risk_puani += 1 if haftalik_calisma_saati < 10 else 0
                    risk_puani += 1 if motivasyon_skoru < 3 else 0
                    risk_puani += 1 if hedef_belirleme_orani < 0.5 else 0
                    
                    risk = 1 if risk_puani >= 3 else 0
                
                # Veri sözlüğü
                ogrenci_veri = {
                    'ogrenci_id': ogrenci.id,
                    'ort_net': ort_net,
                    'ort_dogru': ort_dogru,
                    'ort_yanlis': ort_yanlis,
                    'ilerleme_yuzdesi': ilerleme_yuzdesi,
                    'devamsizlik': devamsizlik,
                    'risk': risk
                }
                
                # Gelişmiş model için ek özellikler
                if model_tipi in ['gelismis', 'kapsamli']:
                    ogrenci_veri['trend_skoru'] = trend_skoru
                
                # Kapsamlı model için ek özellikler
                if model_tipi == 'kapsamli':
                    ogrenci_veri['haftalik_calisma_saati'] = haftalik_calisma_saati
                    ogrenci_veri['motivasyon_skoru'] = motivasyon_skoru
                    ogrenci_veri['hedef_belirleme_orani'] = hedef_belirleme_orani
                
                veri.append(ogrenci_veri)
            
            # DataFrame oluştur
            df = pd.DataFrame(veri)
            
            # En az 10 öğrenci verisi gerekli
            if len(df) < 10:
                return {
                    'success': False,
                    'message': 'Model eğitimi için yeterli sayıda öğrenci verisi bulunmuyor (en az 10 gerekli).'
                }
            
            # Özellik seçimi modele göre
            if model_tipi == 'temel':
                features = ['ort_net', 'ort_dogru', 'ort_yanlis', 'ilerleme_yuzdesi', 'devamsizlik']
            elif model_tipi == 'gelismis':
                features = ['ort_net', 'ort_dogru', 'ort_yanlis', 'ilerleme_yuzdesi', 'devamsizlik', 'trend_skoru']
            else:  # kapsamlı
                features = [
                    'ort_net', 'ort_dogru', 'ort_yanlis', 'ilerleme_yuzdesi', 'devamsizlik', 
                    'trend_skoru', 'haftalik_calisma_saati', 'motivasyon_skoru', 'hedef_belirleme_orani'
                ]
            
            # Veriyi eğitim ve test olarak ayır
            X = df[features]
            y = df['risk']
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
            
            # Model seçimi ve eğitimi
            if model_tipi == 'temel':
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            elif model_tipi == 'gelismis':
                model = GradientBoostingClassifier(
                    n_estimators=150, 
                    learning_rate=0.1, 
                    max_depth=5,
                    random_state=42
                )
            else:  # kapsamlı
                # Çoklu model yaklaşımı (Model Ensemble)
                rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
                gb_model = GradientBoostingClassifier(n_estimators=150, learning_rate=0.1, random_state=42)
                lr_model = LogisticRegression(C=1.0, random_state=42, max_iter=1000)
                
                # Her modeli ayrı ayrı eğit
                rf_model.fit(X_train, y_train)
                gb_model.fit(X_train, y_train)
                lr_model.fit(X_train, y_train)
                
                # Tahminleri al
                rf_pred_train = rf_model.predict_proba(X_train)[:, 1]
                gb_pred_train = gb_model.predict_proba(X_train)[:, 1]
                lr_pred_train = lr_model.predict_proba(X_train)[:, 1]
                
                rf_pred_test = rf_model.predict_proba(X_test)[:, 1]
                gb_pred_test = gb_model.predict_proba(X_test)[:, 1]
                lr_pred_test = lr_model.predict_proba(X_test)[:, 1]
                
                # Ağırlıklı ortalama
                def weighted_avg(preds, weights=[0.5, 0.3, 0.2]):
                    return np.average(preds, axis=0, weights=weights)
                
                # Birleştirme
                y_pred_train_proba = weighted_avg([rf_pred_train, gb_pred_train, lr_pred_train])
                y_pred_test_proba = weighted_avg([rf_pred_test, gb_pred_test, lr_pred_test])
                
                y_pred_train = (y_pred_train_proba > 0.5).astype(int)
                y_pred_test = (y_pred_test_proba > 0.5).astype(int)
                
                # Ana model olarak Gradient Boosting'i kullan
                model = gb_model
                
                # Modeller topluluğunu kaydet
                ensemble_models = {
                    'rf_model': rf_model,
                    'gb_model': gb_model,
                    'lr_model': lr_model,
                    'weights': [0.5, 0.3, 0.2]
                }
                ensemble_filename = f"akademik_risk_ensemble_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
                ensemble_path = os.path.join(MODEL_DIR, ensemble_filename)
                joblib.dump(ensemble_models, ensemble_path)
            
            # Tekli model durumunda eğitim
            if model_tipi != 'kapsamli':
                model.fit(X_train, y_train)
                
                # Model performansını değerlendir
                y_pred_train = model.predict(X_train)
                y_pred_test = model.predict(X_test)
            
            train_acc = accuracy_score(y_train, y_pred_train)
            test_acc = accuracy_score(y_test, y_pred_test)
            
            # Modeli kaydet
            model_filename = f"akademik_risk_model_{model_tipi}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
            model_path = os.path.join(MODEL_DIR, model_filename)
            joblib.dump(model, model_path)
            
            # Veritabanına model kaydet
            model_aciklamasi = ""
            if model_tipi == 'temel':
                model_aciklamasi = "Temel sınav sonuçları ve ilerleme verilerine dayalı basit model."
            elif model_tipi == 'gelismis':
                model_aciklamasi = "Sınav sonuçları, ilerleme ve trend analizi içeren gelişmiş model."
            else:  # kapsamlı
                model_aciklamasi = "Çoklu model yaklaşımı kullanan ve motivasyon, çalışma düzeni gibi faktörleri de içeren kapsamlı model."
                
            yeni_model = YapayZekaModel(
                model_adi=f"Akademik Risk Modeli ({model_tipi.capitalize()}) - {datetime.now().strftime('%d.%m.%Y')}",
                model_turu="akademik_risk",
                aciklama=f"Bu model, öğrencilerin akademik risk durumlarını tahmin eder. {model_aciklamasi} Sınıf filtresi: {sinif if sinif else 'Tüm sınıflar'}",
                model_dosya_yolu=model_path,
                egitim_dogrulugu=train_acc,
                test_dogrulugu=test_acc,
                aktif=True
            )
            
            db.session.add(yeni_model)
            db.session.commit()
            
            # Analiz sonuçlarını hazırla
            analiz_sonuclari = {
                'train_accuracy': train_acc,
                'test_accuracy': test_acc,
                'model_tipi': model_tipi,
                'ozellikler': features
            }
            
            # Özellik önemlerini ekle
            if model_tipi != 'kapsamli':
                feature_importance = {}
                for i, feature in enumerate(features):
                    feature_importance[feature] = float(model.feature_importances_[i])
                analiz_sonuclari['feature_importance'] = feature_importance
            else:
                # Ensemble modeli için birleşik özellik önemi
                feature_importance = {}
                for i, feature in enumerate(features):
                    # Gradient Boosting modelinin özellik önemlerini kullan
                    feature_importance[feature] = float(gb_model.feature_importances_[i])
                analiz_sonuclari['feature_importance'] = feature_importance
                analiz_sonuclari['ensemble_info'] = {
                    'model_sayisi': 3,
                    'ensemble_dosyasi': ensemble_filename
                }
            
            # Analiz tanımı oluştur
            analiz = YapayZekaAnaliz(
                model_id=yeni_model.id,
                analiz_adi=f"Akademik Risk Analizi ({model_tipi.capitalize()}) - {datetime.now().strftime('%d.%m.%Y')}",
                analiz_turu="akademik_risk",
                aciklama=f"Bu analiz, öğrencilerin akademik risk durumlarını ölçer ve riskli öğrenciler için öneriler sunar. Model tipi: {model_tipi}",
                sonuclar=json.dumps(analiz_sonuclari)
            )
            
            db.session.add(analiz)
            db.session.commit()
            
            return {
                'success': True,
                'message': f"Akademik Risk Modeli ({model_tipi.capitalize()}) başarıyla oluşturuldu. Eğitim doğruluğu: {train_acc:.2%}, Test doğruluğu: {test_acc:.2%}",
                'model_id': yeni_model.id
            }
            
        except Exception as e:
            logging.error(f"Akademik risk modeli oluşturma hatası: {str(e)}")
            db.session.rollback()
            import traceback
            logging.error(traceback.format_exc())
            return {
                'success': False,
                'message': f"Model oluşturulurken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def ogrenci_analiz_yap(ogrenci_id, model_id):
        """
        Belirtilen model kullanarak öğrenci için analiz yap
        
        Args:
            ogrenci_id: Öğrenci ID
            model_id: Model ID
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Öğrenci ve model kontrolleri
            ogrenci = Ogrenci.query.get(ogrenci_id)
            if not ogrenci:
                return {
                    'success': False,
                    'message': 'Öğrenci bulunamadı.'
                }
            
            model_kayit = YapayZekaModel.query.get(model_id)
            if not model_kayit:
                return {
                    'success': False,
                    'message': 'Model bulunamadı.'
                }
            
            if not model_kayit.aktif:
                return {
                    'success': False,
                    'message': 'Bu model pasif durumda, analiz yapılamaz.'
                }
            
            if not os.path.exists(model_kayit.model_dosya_yolu):
                return {
                    'success': False,
                    'message': 'Model dosyası bulunamadı.'
                }
            
            # Model tipine göre analiz yap
            if model_kayit.model_turu == "akademik_risk":
                return YapayZekaService._akademik_risk_analizi(ogrenci_id, model_kayit)
            else:
                return {
                    'success': False,
                    'message': f"Desteklenmeyen model türü: {model_kayit.model_turu}"
                }
                
        except Exception as e:
            logging.error(f"Öğrenci analiz yapma hatası: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'message': f"Analiz yapılırken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def _akademik_risk_analizi(ogrenci_id, model_kayit):
        """
        Akademik risk analizi yap
        
        Args:
            ogrenci_id: Öğrenci ID
            model_kayit: YapayZekaModel nesnesi
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        # Öğrencinin verilerini al
        ogrenci = Ogrenci.query.get(ogrenci_id)
        sonuclar = DenemeSonuc.query.filter_by(ogrenci_id=ogrenci_id).all()
        ilerlemeler = DersIlerleme.query.filter_by(ogrenci_id=ogrenci_id).all()
        
        # Deneme sınavı ortalaması
        if sonuclar:
            ort_net = sum(s.toplam_net for s in sonuclar) / len(sonuclar)
            ort_dogru = sum(s.toplam_dogru for s in sonuclar) / len(sonuclar)
            ort_yanlis = sum(s.toplam_yanlis for s in sonuclar) / len(sonuclar)
        else:
            ort_net = 0
            ort_dogru = 0
            ort_yanlis = 0
        
        # İlerleme durumu
        ilerleme_yuzdesi = ogrenci.genel_ilerleme()
        
        # Devamsızlık (varsayılan olarak sıfır, gerçek veri geldiğinde güncellenecek)
        devamsizlik = 0  # İleride eklenecek
        
        # Özellikleri numpy dizisine dönüştür
        ozellikler = np.array([[ort_net, ort_dogru, ort_yanlis, ilerleme_yuzdesi, devamsizlik]])
        
        # Modeli yükle ve tahmin yap
        model = joblib.load(model_kayit.model_dosya_yolu)
        risk_tahmini = model.predict(ozellikler)[0]
        risk_olasiligi = model.predict_proba(ozellikler)[0][1]  # Sınıf 1 (risk) olasılığı
        
        # Analiz sonuçlarını değerlendir
        if risk_tahmini == 1:
            risk_metni = "Yüksek Risk"
            yorumlar = f"Öğrenci akademik risk altında görünüyor. Ortalama net: {ort_net:.1f}, İlerleme: {ilerleme_yuzdesi:.1f}%. Öğrencinin akademik durumunu iyileştirmek için acil müdahale gerekebilir."
        else:
            risk_metni = "Düşük Risk"
            yorumlar = f"Öğrenci akademik olarak iyi durumda görünüyor. Ortalama net: {ort_net:.1f}, İlerleme: {ilerleme_yuzdesi:.1f}%. Mevcut performansını korumak için destekleyici önlemler alınabilir."
        
        # Analiz kaydını oluştur
        try:
            # İlgili analiz nesnesi
            analiz_kayit = YapayZekaAnaliz.query.filter_by(model_id=model_kayit.id).first()
            
            if not analiz_kayit:
                return {
                    'success': False,
                    'message': 'Bu model için tanımlı analiz bulunamadı.'
                }
            
            # Öğrenci analizini kaydet
            ogrenci_analiz = OgrenciAnaliz(
                ogrenci_id=ogrenci_id,
                analiz_id=analiz_kayit.id,
                risk_seviyesi=float(risk_olasiligi),
                yorumlar=yorumlar
                # ham_sonuclar alanı veritabanında olmadığı için kaldırıldı
                # ham_sonuclar=json.dumps({
                #     'ort_net': float(ort_net),
                #     'ort_dogru': float(ort_dogru),
                #     'ort_yanlis': float(ort_yanlis),
                #     'ilerleme_yuzdesi': float(ilerleme_yuzdesi),
                #     'devamsizlik': float(devamsizlik),
                #     'risk_tahmini': int(risk_tahmini),
                #     'risk_olasiligi': float(risk_olasiligi)
                # })
            )
            
            db.session.add(ogrenci_analiz)
            db.session.commit()
            
            # Önerileri oluştur
            YapayZekaService._oneriler_olustur(ogrenci_analiz.id, risk_tahmini)
            
            return {
                'success': True,
                'message': f"Analiz başarıyla tamamlandı. Sonuç: {risk_metni} ({risk_olasiligi:.1%})",
                'analiz_id': ogrenci_analiz.id
            }
            
        except Exception as e:
            logging.error(f"Analiz kaydetme hatası: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'message': f"Analiz sonuçları kaydedilirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def _oneriler_olustur(analiz_id, risk_tahmini):
        """
        Analiz sonucuna göre öneriler oluştur
        
        Args:
            analiz_id: OgrenciAnaliz ID
            risk_tahmini: Risk tahmini (0 veya 1)
        """
        ogrenci_analiz = OgrenciAnaliz.query.get(analiz_id)
        if not ogrenci_analiz:
            return
        
        # Öğrenci ve analiz bilgileri
        ogrenci = Ogrenci.query.get(ogrenci_analiz.ogrenci_id)
        
        # Risk seviyesine göre öneriler
        oneriler = []
        
        if risk_tahmini == 1:  # Yüksek risk
            # Müdahale önerileri
            oneriler.append({
                'oneri_metni': "Öğrencinin akademik durumunu iyileştirmek için birebir çalışma programı hazırlanmalı.",
                'oneri_turu': "mudahale",
                'oncelik': 2  # Yüksek öncelik
            })
            
            oneriler.append({
                'oneri_metni': "Haftalık ilerleme değerlendirmeleri yapılarak öğrencinin motivasyonu artırılmalı.",
                'oneri_turu': "mudahale",
                'oncelik': 1  # Orta öncelik
            })
            
            # Kaynak önerileri
            oneriler.append({
                'oneri_metni': "Öğrencinin eksik olduğu konular için ek kaynak ve çalışma materyalleri sağlanmalı.",
                'oneri_turu': "kaynak",
                'oncelik': 1  # Orta öncelik
            })
            
            # Aktivite önerileri
            oneriler.append({
                'oneri_metni': "Akran çalışma grubu oluşturarak işbirlikli öğrenme ortamı sağlanmalı.",
                'oneri_turu': "aktivite",
                'oncelik': 0  # Düşük öncelik
            })
        else:  # Düşük risk
            # Müdahale önerileri
            oneriler.append({
                'oneri_metni': "Mevcut çalışma programı devam ettirilerek öğrencinin motivasyonu korunmalı.",
                'oneri_turu': "mudahale",
                'oncelik': 0  # Düşük öncelik
            })
            
            # Kaynak önerileri
            oneriler.append({
                'oneri_metni': "Öğrencinin ilgi alanlarına yönelik ek okuma kaynakları önerilebilir.",
                'oneri_turu': "kaynak",
                'oncelik': 0  # Düşük öncelik
            })
            
            # Aktivite önerileri
            oneriler.append({
                'oneri_metni': "Üst düzey düşünme becerilerini geliştirmek için proje tabanlı aktiviteler planlanabilir.",
                'oneri_turu': "aktivite",
                'oncelik': 1  # Orta öncelik
            })
        
        # Önerileri veritabanına kaydet
        for oneri in oneriler:
            yeni_oneri = OgrenciOneri(
                analiz_id=analiz_id,
                oneri_metni=oneri['oneri_metni'],
                oneri_turu=oneri['oneri_turu'],
                oncelik=oneri['oncelik']
            )
            db.session.add(yeni_oneri)
        
        db.session.commit()
    
    @staticmethod
    def get_ogrenci_analiz_sonuclari(ogrenci_id):
        """
        Öğrenci için yapılmış analizleri getir
        
        Args:
            ogrenci_id: Öğrenci ID
            
        Returns:
            List: Analiz listesi
        """
        return OgrenciAnaliz.query.filter_by(ogrenci_id=ogrenci_id).order_by(OgrenciAnaliz.analiz_tarihi.desc()).all()
    
    @staticmethod
    def get_analiz_onerileri(analiz_id):
        """
        Analiz için oluşturulmuş önerileri getir
        
        Args:
            analiz_id: Analiz ID
            
        Returns:
            List: Öneri listesi
        """
        return OgrenciOneri.query.filter_by(analiz_id=analiz_id).all()
    
    @staticmethod
    def oneri_uygulama_durumu_guncelle(oneri_id, uygulamaya_alindi, uygulama_sonucu=None):
        """
        Öneri uygulama durumunu güncelle
        
        Args:
            oneri_id: Öneri ID
            uygulamaya_alindi: Uygulamaya alındı mı (True/False)
            uygulama_sonucu: Uygulama sonucu/yorumu
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            oneri = OgrenciOneri.query.get(oneri_id)
            if not oneri:
                return {
                    'success': False,
                    'message': 'Öneri bulunamadı.'
                }
            
            oneri.uygulamaya_alindi = uygulamaya_alindi
            oneri.uygulama_sonucu = uygulama_sonucu
            
            if uygulamaya_alindi and not oneri.uygulama_tarihi:
                oneri.uygulama_tarihi = datetime.now()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Öneri durumu başarıyla güncellendi.'
            }
            
        except Exception as e:
            logging.error(f"Öneri güncelleme hatası: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'message': f"Öneri güncellenirken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def metin_duygu_analizi_yap(ogrenci_id, metin, metin_kaynagi, analiz_tipi='gelismis'):
        """
        Metin için duygu analizi yap - Geliştirilmiş versiyon
        
        Args:
            ogrenci_id: Öğrenci ID
            metin: Analiz edilecek metin
            metin_kaynagi: Metnin kaynağı (kompozisyon, anket_cevabi, refleksiyon, gorusme_notu, vb.)
            analiz_tipi: Analiz tipi ('basit', 'gelismis' veya 'kapsamli')
            
        Returns:
            Dict: İşlem sonucunu içeren sözlük
        """
        try:
            # Öğrenci kontrolü
            ogrenci = Ogrenci.query.get(ogrenci_id)
            if not ogrenci:
                return {
                    'success': False,
                    'message': 'Öğrenci bulunamadı.'
                }
            
            # Geniş Türkçe duygu sözlükleri
            olumlu_kelimeler = [
                'güzel', 'harika', 'mükemmel', 'iyi', 'başarılı', 'mutlu', 'seviyorum', 'teşekkür', 'olumlu', 
                'kolay', 'başardım', 'anladım', 'sevindim', 'memnun', 'keyifli', 'hoş', 'güven', 'tatmin', 
                'sakin', 'rahat', 'huzurlu', 'neşeli', 'coşkulu', 'heyecanlı', 'umutlu', 'motivasyon', 
                'azim', 'kararlı', 'istekli', 'sevgi', 'beğeni', 'takdir', 'gurur', 'memnuniyet', 'tatmin',
                'zevkli', 'eğlenceli', 'ödül', 'başarı', 'zafer', 'faydalı', 'yararlı', 'değerli', 'önemli',
                'anlamlı', 'gelişim', 'ilerleme', 'öğrenme', 'anlama', 'kavrama', 'çözme', 'keşfetme'
            ]
            
            olumsuz_kelimeler = [
                'kötü', 'zor', 'yapamadım', 'anlamadım', 'üzgün', 'mutsuz', 'problem', 'sorun', 'sıkıntı', 
                'başarısız', 'hata', 'zayıf', 'yetersiz', 'kaygı', 'korku', 'endişe', 'stres', 'gergin', 
                'tedirgin', 'karamsarlık', 'umutsuz', 'bezgin', 'bıkkın', 'yorgun', 'tükenmişlik', 'çaresiz', 
                'güçsüz', 'kayıp', 'başarısızlık', 'yenilgi', 'karmaşık', 'zorluk', 'engel', 'baskı', 'gerilim',
                'kızgın', 'öfkeli', 'sinirli', 'hayal kırıklığı', 'üzüntü', 'hüzün', 'keder', 'ağır', 'yetersiz',
                'eksik', 'anlamsız', 'faydasız', 'boşuna', 'beyhude', 'imkansız', 'karışık', 'anlaşılmaz',
                'çözülmez', 'başedemiyorum', 'yetişemiyorum', 'yapamıyorum', 'zorlanıyorum', 'sıkılıyorum'
            ]
            
            # Motivasyon ile ilgili kelimeler
            motivasyon_kelimeleri = [
                'istek', 'arzu', 'motivasyon', 'azim', 'kararlılık', 'hedef', 'amaç', 'başarma', 
                'çabalamak', 'gayret', 'emek', 'istikrar', 'çalışmak', 'odaklanmak', 'disiplin', 
                'adanmak', 'sebat', 'ısrar', 'süreklilik', 'düzenli', 'planlı', 'programlı'
            ]
            
            # Akademik kaygı ile ilgili kelimeler
            kaygi_kelimeleri = [
                'sınav', 'sonuç', 'korku', 'endişe', 'stres', 'baskı', 'kaygı', 'gerginlik', 
                'tedirginlik', 'panik', 'başarısızlık', 'yetersizlik', 'karşılaştırma', 'rakip', 
                'rekabet', 'yarış', 'derece', 'sıralama', 'puan', 'yüksek', 'düşük', 'geçme', 'kalma'
            ]
            
            # Metni temizleme (Türkçe karakterler korunarak)
            def metin_temizle(text):
                text = text.lower()
                # Noktalama işaretlerini boşluklarla değiştir
                for p in '.,;:?!-()[]{}':
                    text = text.replace(p, ' ')
                # Fazla boşlukları temizle
                return ' '.join(text.split())
            
            # Basit duygu analizi - kelime eşleştirmesine dayalı
            def basit_duygu_analizi(text):
                # Metni temizle
                temiz_metin = metin_temizle(text)
                kelimeler = temiz_metin.split()
                
                # Kelime eşleştirme
                olumlu_sayisi = sum(1 for k in kelimeler if k in olumlu_kelimeler)
                olumsuz_sayisi = sum(1 for k in kelimeler if k in olumsuz_kelimeler)
                
                # Skorlar (0-1 arası)
                toplam = olumlu_sayisi + olumsuz_sayisi
                if toplam == 0:
                    olumlu_skor = 0.33
                    olumsuz_skor = 0.33
                    notr_skor = 0.34
                else:
                    olumlu_skor = olumlu_sayisi / (toplam * 2)  # * 2 ile en fazla 0.5 yapıyoruz
                    olumsuz_skor = olumsuz_sayisi / (toplam * 2)
                    notr_skor = 1 - (olumlu_skor + olumsuz_skor)
                
                # Baskın duygu
                if olumlu_skor > olumsuz_skor and olumlu_skor > notr_skor:
                    baskin_duygu = 'olumlu'
                elif olumsuz_skor > olumlu_skor and olumsuz_skor > notr_skor:
                    baskin_duygu = 'olumsuz'
                else:
                    baskin_duygu = 'notr'
                
                return {
                    'baskin_duygu': baskin_duygu,
                    'olumlu_skor': olumlu_skor,
                    'olumsuz_skor': olumsuz_skor,
                    'notr_skor': notr_skor
                }
            
            # Gelişmiş duygu analizi - TF-IDF ve bağlam analizi
            def gelismis_duygu_analizi(text):
                # Metni temizle
                temiz_metin = metin_temizle(text)
                
                # TF-IDF vektörleştirici oluştur
                # Bu vektörleştirici kelime frekansı ve ters doküman frekansına dayalı
                # bir ağırlıklandırma yaparak kelimelerin önem derecesini hesaplar
                vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words=None  # Türkçe için stop words yok
                )
                
                # Vektörleştirme için eğitim metinleri oluştur
                # (gerçek bir uygulamada önceden eğitilmiş bir model kullanılmalı)
                egitim_metinleri = [
                    ' '.join(olumlu_kelimeler),  # Olumlu örnek
                    ' '.join(olumsuz_kelimeler)  # Olumsuz örnek
                ]
                egitim_metinleri.append(temiz_metin)  # Analiz edilecek metin
                
                # Vektörleştiriciyi eğit ve metin vektörlerini oluştur
                tfidf_matrix = vectorizer.fit_transform(egitim_metinleri)
                
                # Benzerlik hesaplama (kosinüs benzerliği)
                from sklearn.metrics.pairwise import cosine_similarity
                benzerlik_skoru = cosine_similarity(
                    tfidf_matrix[2:3],  # Analiz metni vektörü
                    tfidf_matrix[0:2]   # Olumlu ve olumsuz örnek vektörleri
                )[0]
                
                # Skorları normalize et
                olumlu_benzerlik = max(0, benzerlik_skoru[0])
                olumsuz_benzerlik = max(0, benzerlik_skoru[1])
                
                # Bağlam analizi için n-gramlar kullan
                # Bu, sadece tek kelimelere değil, kelime gruplarına da bakarak
                # daha fazla bağlam analizi yapar
                bigram_vectorizer = CountVectorizer(
                    ngram_range=(2, 3),  # 2-gram ve 3-gram kullan
                    max_features=500
                )
                
                # Bigram analizi yap
                try:
                    bigram_matrix = bigram_vectorizer.fit_transform(egitim_metinleri)
                    bigram_benzerlik = cosine_similarity(
                        bigram_matrix[2:3], 
                        bigram_matrix[0:2]
                    )[0]
                    
                    # Bigram benzerlik skorlarını ana skorlarla birleştir
                    olumlu_bigram = max(0, bigram_benzerlik[0])
                    olumsuz_bigram = max(0, bigram_benzerlik[1])
                    
                    # Ağırlıklı ortalama (kelime bazlı ve bigram bazlı)
                    olumlu_skor = 0.7 * olumlu_benzerlik + 0.3 * olumlu_bigram
                    olumsuz_skor = 0.7 * olumsuz_benzerlik + 0.3 * olumsuz_bigram
                except:
                    # Bigram analizi yapılamazsa (metin çok kısaysa)
                    olumlu_skor = olumlu_benzerlik
                    olumsuz_skor = olumsuz_benzerlik
                
                # Toplam skoru normalize et
                toplam_skor = olumlu_skor + olumsuz_skor
                if toplam_skor > 0:
                    olumlu_skor = olumlu_skor / toplam_skor * 0.8
                    olumsuz_skor = olumsuz_skor / toplam_skor * 0.8
                else:
                    olumlu_skor = 0.4
                    olumsuz_skor = 0.4
                
                notr_skor = 1 - (olumlu_skor + olumsuz_skor)
                
                # Baskın duygu
                if olumlu_skor > olumsuz_skor and olumlu_skor > notr_skor:
                    baskin_duygu = 'olumlu'
                elif olumsuz_skor > olumlu_skor and olumsuz_skor > notr_skor:
                    baskin_duygu = 'olumsuz'
                else:
                    baskin_duygu = 'notr'
                
                # Kelime bazlı analiz sonuçlarını da ekle
                kelimeler = temiz_metin.split()
                onemli_kelimeler = vectorizer.get_feature_names_out()
                
                # En önemli kelimeleri belirle
                kelime_onem = {}
                for kelime in kelimeler:
                    if kelime in onemli_kelimeler:
                        kelime_vektoru = vectorizer.transform([kelime])
                        kelime_benzerlik = cosine_similarity(
                            kelime_vektoru,
                            tfidf_matrix[0:2]
                        )[0]
                        
                        # Kelimenin duygusal yükünü belirle
                        kelime_duygusal_yuk = 'olumlu' if kelime_benzerlik[0] > kelime_benzerlik[1] else 'olumsuz'
                        kelime_onem[kelime] = {
                            'duygu': kelime_duygusal_yuk,
                            'skor': abs(kelime_benzerlik[0] - kelime_benzerlik[1])
                        }
                
                # Sonuç sözlüğü
                return {
                    'baskin_duygu': baskin_duygu,
                    'olumlu_skor': olumlu_skor,
                    'olumsuz_skor': olumsuz_skor,
                    'notr_skor': notr_skor,
                    'onemli_kelimeler': {k: v for k, v in sorted(
                        kelime_onem.items(), 
                        key=lambda item: item[1]['skor'], 
                        reverse=True
                    )[:10]}  # En etkili 10 kelime
                }
            
            # Kapsamlı duygu analizi - Duygu kategorileri ve motivasyon analizi
            def kapsamli_duygu_analizi(text):
                # Önce gelişmiş analizi yap
                temel_sonuc = gelismis_duygu_analizi(text)
                
                # Metni temizle
                temiz_metin = metin_temizle(text)
                kelimeler = temiz_metin.split()
                
                # Motivasyon ve kaygı skorları
                motivasyon_skoru = sum(1 for k in kelimeler if k in motivasyon_kelimeleri) / max(len(kelimeler), 1)
                kaygi_skoru = sum(1 for k in kelimeler if k in kaygi_kelimeleri) / max(len(kelimeler), 1)
                
                # Duygu kategorileri
                duygu_kategorileri = {
                    'motivasyon': motivasyon_skoru,
                    'kaygi': kaygi_skoru
                }
                
                # Motivasyon-kaygı dengesi
                motivasyon_kaygi_dengesi = motivasyon_skoru - kaygi_skoru
                
                # Cümle analizi
                cumleler = text.split('.')
                cumle_analizleri = []
                
                for cumle in cumleler:
                    if len(cumle.strip()) > 5:  # Anlamlı uzunluktaki cümleler
                        cumle_analiz = basit_duygu_analizi(cumle)
                        cumle_analizleri.append({
                            'cumle': cumle.strip(),
                            'duygu': cumle_analiz['baskin_duygu'],
                            'skor': max(cumle_analiz['olumlu_skor'], cumle_analiz['olumsuz_skor'])
                        })
                
                # Duygu yoğunluğu ve değişimi
                duygu_yogunlugu = max(temel_sonuc['olumlu_skor'], temel_sonuc['olumsuz_skor'])
                
                # Sonuçları birleştir
                kapsamli_sonuc = temel_sonuc.copy()
                kapsamli_sonuc.update({
                    'duygu_kategorileri': duygu_kategorileri,
                    'motivasyon_kaygi_dengesi': motivasyon_kaygi_dengesi,
                    'cumle_analizleri': cumle_analizleri,
                    'duygu_yogunlugu': duygu_yogunlugu
                })
                
                return kapsamli_sonuc
            
            # Analiz tipine göre uygun analiz fonksiyonunu çağır
            if analiz_tipi == 'basit':
                analiz_sonucu = basit_duygu_analizi(metin)
            elif analiz_tipi == 'gelismis':
                analiz_sonucu = gelismis_duygu_analizi(metin)
            else:  # kapsamlı
                analiz_sonucu = kapsamli_duygu_analizi(metin)
            
            # Sonuçtan sadece veritabanı alanlarına kaydedilecek bilgileri çıkart
            db_kaydi = {
                'baskin_duygu': analiz_sonucu['baskin_duygu'],
                'olumlu_skor': analiz_sonucu['olumlu_skor'],
                'olumsuz_skor': analiz_sonucu['olumsuz_skor'],
                'notr_skor': analiz_sonucu['notr_skor']
            }
            
            # Detaylı analiz sonuçlarını JSON formatında sakla
            sonuc_detay = {
                'analiz_tipi': analiz_tipi,
                'duygu_yogunlugu': max(db_kaydi['olumlu_skor'], db_kaydi['olumsuz_skor'])
            }
            
            # Gelişmiş ve kapsamlı analizler için ek özellikleri ekle
            if analiz_tipi in ['gelismis', 'kapsamli'] and 'onemli_kelimeler' in analiz_sonucu:
                sonuc_detay['onemli_kelimeler'] = analiz_sonucu['onemli_kelimeler']
            
            # Kapsamlı analiz için duygu kategorileri ve diğer detaylar
            if analiz_tipi == 'kapsamli':
                if 'duygu_kategorileri' in analiz_sonucu:
                    sonuc_detay['duygu_kategorileri'] = analiz_sonucu['duygu_kategorileri']
                if 'motivasyon_kaygi_dengesi' in analiz_sonucu:
                    sonuc_detay['motivasyon_kaygi_dengesi'] = analiz_sonucu['motivasyon_kaygi_dengesi']
                if 'cumle_analizleri' in analiz_sonucu:
                    sonuc_detay['cumle_analizleri'] = analiz_sonucu['cumle_analizleri']
            
            # Duygu analizi kaydı oluştur
            duygu_analizi = DuyguAnalizi(
                ogrenci_id=ogrenci_id,
                metin=metin,
                metin_kaynagi=metin_kaynagi,
                baskın_duygu=db_kaydi['baskin_duygu'],
                olumlu_skor=db_kaydi['olumlu_skor'],
                olumsuz_skor=db_kaydi['olumsuz_skor'],
                notr_skor=db_kaydi['notr_skor'],
                sonuc_detay=json.dumps(sonuc_detay)
            )
            
            db.session.add(duygu_analizi)
            db.session.commit()
            
            return {
                'success': True,
                'message': f"{analiz_tipi.capitalize()} duygu analizi başarıyla tamamlandı. Sonuç: {analiz_sonucu['baskin_duygu'].capitalize()}",
                'analiz_id': duygu_analizi.id,
                'sonuc': analiz_sonucu
            }
            
        except Exception as e:
            logging.error(f"Duygu analizi hatası: {str(e)}")
            db.session.rollback()
            import traceback
            logging.error(traceback.format_exc())
            return {
                'success': False,
                'message': f"Duygu analizi yapılırken bir hata oluştu: {str(e)}"
            }
    
    @staticmethod
    def get_duygu_analizi(analiz_id):
        """
        ID'ye göre duygu analizini getir
        
        Args:
            analiz_id: Duygu Analizi ID
            
        Returns:
            DuyguAnalizi: Duygu analizi nesnesi veya None
        """
        return DuyguAnalizi.query.get(analiz_id)
    
    @staticmethod
    def get_duygu_analizleri(ogrenci_id):
        """
        Öğrenci için yapılmış duygu analizlerini getir
        
        Args:
            ogrenci_id: Öğrenci ID
            
        Returns:
            List: Duygu analizi listesi
        """
        return DuyguAnalizi.query.filter_by(ogrenci_id=ogrenci_id).order_by(DuyguAnalizi.analiz_tarihi.desc()).all()