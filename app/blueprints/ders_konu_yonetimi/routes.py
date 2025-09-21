from flask import render_template, request, redirect, url_for, flash
import pandas as pd
from app.blueprints.ders_konu_yonetimi import ders_konu_yonetimi_bp
from app.extensions import db
from app.blueprints.ders_konu_yonetimi.models import Ders, Konu

@ders_konu_yonetimi_bp.route('/')
def lista():
    """Tüm derslerin listelendiği sayfa"""
    dersler = Ders.query.order_by(Ders.ad).all()
    return render_template('ders_konu_yonetimi/dersler.html', dersler=dersler)

@ders_konu_yonetimi_bp.route('/excel-ile-ekle', methods=['GET', 'POST'])
def excel_ile_ekle():
    """Excel ile toplu ders ve konu ekleme formu ve işlemi"""
    if request.method == 'POST':
        # Excel dosyası kontrolü
        if 'excel_dosya' not in request.files:
            flash('Lütfen bir Excel dosyası seçin!', 'danger')
            return redirect(url_for('ders_konu_yonetimi.excel_ile_ekle'))
        
        dosya = request.files['excel_dosya']
        
        # Dosya adı kontrolü
        if dosya.filename == '':
            flash('Lütfen bir Excel dosyası seçin!', 'danger')
            return redirect(url_for('ders_konu_yonetimi.excel_ile_ekle'))
        
        # Dosya uzantısı kontrolü
        if not dosya.filename.endswith(('.xlsx', '.xls')):
            flash('Lütfen geçerli bir Excel dosyası (.xlsx veya .xls) seçin!', 'danger')
            return redirect(url_for('ders_konu_yonetimi.excel_ile_ekle'))
        
        try:
            # Excel dosyasını oku
            df = pd.read_excel(dosya, header=None)
            
            # Başarılı ve hatalı sayıları
            eklenen_ders = 0
            eklenen_konu = 0
            hatali = 0
            
            # Excel içeriğini işle
            col = 0
            while col < df.shape[1]:
                # Ders adını A1, C1, E1... gibi hücrelerden al
                ders_adi = df.iloc[0, col]
                
                # Geçerli bir ders adı varsa işleme devam et
                if pd.notna(ders_adi) and isinstance(ders_adi, str) and ders_adi.strip():
                    ders_adi = ders_adi.strip()
                    
                    # Dersin TYT, AYT, YDT gruplarından hangisine ait olduğunu belirle
                    ders_grubu = None
                    if 'TYT' in ders_adi:
                        ders_grubu = 'TYT'
                    elif 'AYT' in ders_adi:
                        ders_grubu = 'AYT'
                    elif 'YDT' in ders_adi:
                        ders_grubu = 'YDT'
                    
                    # Ders zaten var mı kontrol et
                    mevcut_ders = Ders.query.filter_by(ad=ders_adi).first()
                    if mevcut_ders:
                        ders_id = mevcut_ders.id
                    else:
                        # Yeni ders oluştur
                        yeni_ders = Ders(
                            ad=ders_adi,
                            aciklama=f"{ders_grubu} grubu dersi" if ders_grubu else ""
                        )
                        db.session.add(yeni_ders)
                        db.session.flush()  # ID alabilmek için flush işlemi
                        ders_id = yeni_ders.id
                        eklenen_ders += 1
                    
                    # Sıra değeri (bu dersteki son konudan sonra gelecek)
                    son_konu = Konu.query.filter_by(ders_id=ders_id).order_by(Konu.sira.desc()).first()
                    sira = 1
                    if son_konu:
                        sira = son_konu.sira + 1
                    
                    # Konuları işle (A2, A3,... ve B2, B3,... gibi)
                    for row in range(1, df.shape[0]):
                        # Konu adı
                        konu_adi = df.iloc[row, col]
                        
                        # Konu süresi (bir sonraki sütun)
                        if col + 1 < df.shape[1]:
                            sure = df.iloc[row, col + 1]
                        else:
                            sure = None
                        
                        # Geçerli bir konu adı ve süresi varsa ekle
                        if pd.notna(konu_adi) and pd.notna(sure) and isinstance(konu_adi, str) and konu_adi.strip():
                            konu_adi = konu_adi.strip()
                            
                            try:
                                # Süresi sayı olarak al
                                tahmini_sure = int(float(sure))
                                if tahmini_sure <= 0:
                                    raise ValueError()
                                
                                # Yeni konuyu ekle
                                yeni_konu = Konu(
                                    ders_id=ders_id,
                                    ad=konu_adi,
                                    tahmini_sure=tahmini_sure,
                                    sira=sira
                                )
                                db.session.add(yeni_konu)
                                sira += 1
                                eklenen_konu += 1
                                
                            except:
                                hatali += 1
                
                # Sonraki sütuna geç (konu ve süre sütunları)
                col += 2
            
            # Veritabanına kaydet
            db.session.commit()
            
            # Bildirimleri oluştur
            if eklenen_ders > 0:
                flash(f'{eklenen_ders} ders başarıyla eklendi!', 'success')
            
            if eklenen_konu > 0:
                flash(f'{eklenen_konu} konu başarıyla eklendi!', 'success')
            
            if hatali > 0:
                flash(f'{hatali} konu ekleme sırasında hata oluştu! Geçersiz veya eksik veriler.', 'warning')
            
            if eklenen_ders == 0 and eklenen_konu == 0:
                flash('Excel dosyasından hiçbir ders veya konu eklenemedi!', 'danger')
            
            return redirect(url_for('ders_konu_yonetimi.lista'))
        
        except Exception as e:
            flash(f'Excel dosyası işlenirken bir hata oluştu: {str(e)}', 'danger')
            return redirect(url_for('ders_konu_yonetimi.excel_ile_ekle'))
    
    return render_template('ders_konu_yonetimi/excel_ile_ders_ekle.html')

@ders_konu_yonetimi_bp.route('/ekle', methods=['GET', 'POST'])
def ekle():
    """Yeni ders ekleme formu ve işlemi"""
    if request.method == 'POST':
        # Form verilerini al
        ad = request.form.get('ad')
        aciklama = request.form.get('aciklama')
        
        # Validasyon
        if not ad:
            flash('Lütfen ders adını girin!', 'danger')
            return redirect(url_for('ders_konu_yonetimi.ekle'))
        
        # Ders adı kontrolü
        mevcut_ders = Ders.query.filter_by(ad=ad).first()
        if mevcut_ders:
            flash(f'"{ad}" adında bir ders zaten sistemde kayıtlı!', 'danger')
            return redirect(url_for('ders_konu_yonetimi.ekle'))
        
        # Yeni dersi ekle
        yeni_ders = Ders(
            ad=ad,
            aciklama=aciklama if aciklama else None
        )
        
        # Veritabanına kaydet
        db.session.add(yeni_ders)
        db.session.commit()
        
        flash(f'"{ad}" dersi başarıyla eklendi!', 'success')
        return redirect(url_for('ders_konu_yonetimi.lista'))
    
    return render_template('ders_konu_yonetimi/ders_ekle.html')

@ders_konu_yonetimi_bp.route('/<int:ders_id>')
def detay(ders_id):
    """Ders detay sayfası ve konuların listesi"""
    ders = Ders.query.get_or_404(ders_id)
    
    # Konuları sıra numarasına göre getir
    konular = Konu.query.filter_by(ders_id=ders_id).order_by(Konu.sira).all()
    
    return render_template('ders_konu_yonetimi/ders_detay.html', ders=ders, konular=konular)

@ders_konu_yonetimi_bp.route('/<int:ders_id>/duzenle', methods=['GET', 'POST'])
def duzenle(ders_id):
    """Ders bilgilerini düzenleme formu ve işlemi"""
    ders = Ders.query.get_or_404(ders_id)
    
    if request.method == 'POST':
        # Form verilerini al
        ad = request.form.get('ad')
        aciklama = request.form.get('aciklama')
        
        # Validasyon
        if not ad:
            flash('Lütfen ders adını girin!', 'danger')
            return redirect(url_for('ders_konu_yonetimi.duzenle', ders_id=ders_id))
        
        # Eğer ad değiştiyse ve bu ad başka derste varsa
        if ad != ders.ad:
            mevcut_ders = Ders.query.filter_by(ad=ad).first()
            if mevcut_ders:
                flash(f'"{ad}" adında başka bir ders zaten sistemde kayıtlı!', 'danger')
                return redirect(url_for('ders_konu_yonetimi.duzenle', ders_id=ders_id))
        
        # Ders bilgilerini güncelle
        ders.ad = ad
        ders.aciklama = aciklama if aciklama else None
        
        # Veritabanına kaydet
        db.session.commit()
        
        flash(f'"{ad}" dersinin bilgileri başarıyla güncellendi!', 'success')
        return redirect(url_for('ders_konu_yonetimi.detay', ders_id=ders_id))
    
    return render_template('ders_konu_yonetimi/ders_ekle.html', ders=ders)

@ders_konu_yonetimi_bp.route('/<int:ders_id>/sil', methods=['POST'])
def sil(ders_id):
    """Dersi sistemden silme işlemi"""
    ders = Ders.query.get_or_404(ders_id)
    
    # Dersi sil
    db.session.delete(ders)
    db.session.commit()
    
    flash(f'"{ders.ad}" dersi sistemden silindi!', 'success')
    return redirect(url_for('ders_konu_yonetimi.lista'))

@ders_konu_yonetimi_bp.route('/<int:ders_id>/konu-ekle', methods=['GET', 'POST'])
def konu_ekle(ders_id):
    """Derse konu ekleme formu ve işlemi"""
    ders = Ders.query.get_or_404(ders_id)
    
    if request.method == 'POST':
        # Form verilerini al
        ad = request.form.get('ad')
        tahmini_sure = request.form.get('tahmini_sure')
        
        # Validasyon
        if not ad or not tahmini_sure:
            flash('Lütfen tüm alanları doldurun!', 'danger')
            return redirect(url_for('ders_konu_yonetimi.konu_ekle', ders_id=ders_id))
        
        try:
            # Süreyi sayıya çevir
            tahmini_sure = int(tahmini_sure)
            if tahmini_sure <= 0:
                raise ValueError()
        except:
            flash('Lütfen tahmini süre için geçerli bir sayı girin!', 'danger')
            return redirect(url_for('ders_konu_yonetimi.konu_ekle', ders_id=ders_id))
        
        # Sıra numarası (bu dersteki son konudan sonra gelecek)
        son_konu = Konu.query.filter_by(ders_id=ders_id).order_by(Konu.sira.desc()).first()
        sira = 1
        if son_konu:
            sira = son_konu.sira + 1
        
        # Yeni konuyu ekle
        yeni_konu = Konu(
            ders_id=ders_id,
            ad=ad,
            tahmini_sure=tahmini_sure,
            sira=sira
        )
        
        # Veritabanına kaydet
        db.session.add(yeni_konu)
        db.session.commit()
        
        flash(f'"{ad}" konusu başarıyla eklendi!', 'success')
        return redirect(url_for('ders_konu_yonetimi.detay', ders_id=ders_id))
    
    return render_template('ders_konu_yonetimi/konu_ekle.html', ders=ders)

@ders_konu_yonetimi_bp.route('/konu/<int:konu_id>/duzenle', methods=['GET', 'POST'])
def konu_duzenle(konu_id):
    """Konu bilgilerini düzenleme formu ve işlemi"""
    konu = Konu.query.get_or_404(konu_id)
    ders = Ders.query.get_or_404(konu.ders_id)
    
    if request.method == 'POST':
        # Form verilerini al
        ad = request.form.get('ad')
        tahmini_sure = request.form.get('tahmini_sure')
        
        # Validasyon
        if not ad or not tahmini_sure:
            flash('Lütfen tüm alanları doldurun!', 'danger')
            return redirect(url_for('ders_konu_yonetimi.konu_duzenle', konu_id=konu_id))
        
        try:
            # Süreyi sayıya çevir
            tahmini_sure = int(tahmini_sure)
            if tahmini_sure <= 0:
                raise ValueError()
        except:
            flash('Lütfen tahmini süre için geçerli bir sayı girin!', 'danger')
            return redirect(url_for('ders_konu_yonetimi.konu_duzenle', konu_id=konu_id))
        
        # Konu bilgilerini güncelle
        konu.ad = ad
        konu.tahmini_sure = tahmini_sure
        
        # Veritabanına kaydet
        db.session.commit()
        
        flash(f'"{ad}" konusunun bilgileri başarıyla güncellendi!', 'success')
        return redirect(url_for('ders_konu_yonetimi.detay', ders_id=konu.ders_id))
    
    return render_template('ders_konu_yonetimi/konu_ekle.html', ders=ders, konu=konu)

@ders_konu_yonetimi_bp.route('/konu/<int:konu_id>/sil', methods=['POST'])
def konu_sil(konu_id):
    """Konuyu sistemden silme işlemi"""
    konu = Konu.query.get_or_404(konu_id)
    ders_id = konu.ders_id
    
    # Konuyu sil
    db.session.delete(konu)
    
    # Sıra numaralarını güncelle
    kalan_konular = Konu.query.filter_by(ders_id=ders_id).order_by(Konu.sira).all()
    for i, k in enumerate(kalan_konular, 1):
        k.sira = i
    
    # Veritabanına kaydet
    db.session.commit()
    
    flash(f'"{konu.ad}" konusu sistemden silindi!', 'success')
    return redirect(url_for('ders_konu_yonetimi.detay', ders_id=ders_id))

@ders_konu_yonetimi_bp.route('/<int:ders_id>/konular-toplu-ekle', methods=['GET', 'POST'])
def konular_toplu_ekle(ders_id):
    """Konuları toplu şekilde ekleme sayfası ve işlemi"""
    ders = Ders.query.get_or_404(ders_id)
    
    if request.method == 'POST':
        # Form verisini al
        konular_metin = request.form.get('konular_metin')
        
        # Validasyon
        if not konular_metin:
            flash('Lütfen konular listesini girin!', 'danger')
            return redirect(url_for('ders_konu_yonetimi.konular_toplu_ekle', ders_id=ders_id))
        
        # Metni satırlara böl
        konular_satir = konular_metin.strip().split('\n')
        
        # Sıra numarası (bu dersteki son konudan sonra gelecek)
        son_konu = Konu.query.filter_by(ders_id=ders_id).order_by(Konu.sira.desc()).first()
        sira = 1
        if son_konu:
            sira = son_konu.sira + 1
        
        # Satırları işle
        eklenen = 0
        hatali = 0
        
        for satir in konular_satir:
            satir = satir.strip()
            if not satir:
                continue
            
            # Konu adı ve süreyi ayır
            parcalar = satir.split(',')
            
            if len(parcalar) >= 2:
                konu_adi = parcalar[0].strip()
                sure_str = parcalar[1].strip()
                
                if konu_adi and sure_str:
                    try:
                        # Süreyi sayıya çevir
                        tahmini_sure = int(float(sure_str))
                        if tahmini_sure <= 0:
                            raise ValueError()
                        
                        # Yeni konuyu ekle
                        yeni_konu = Konu(
                            ders_id=ders_id,
                            ad=konu_adi,
                            tahmini_sure=tahmini_sure,
                            sira=sira
                        )
                        
                        db.session.add(yeni_konu)
                        sira += 1
                        eklenen += 1
                        
                    except:
                        hatali += 1
                else:
                    hatali += 1
            else:
                hatali += 1
        
        # Veritabanına kaydet
        db.session.commit()
        
        # Bildirimleri oluştur
        if eklenen > 0:
            flash(f'{eklenen} konu başarıyla eklendi!', 'success')
        
        if hatali > 0:
            flash(f'{hatali} konu ekleme sırasında hata oluştu! Geçersiz veya eksik veriler.', 'warning')
        
        if eklenen == 0:
            flash('Hiçbir konu eklenemedi!', 'danger')
        
        return redirect(url_for('ders_konu_yonetimi.detay', ders_id=ders_id))
    
    return render_template('ders_konu_yonetimi/konular_toplu_ekle.html', ders=ders)