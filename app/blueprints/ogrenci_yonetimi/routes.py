from flask import render_template, request, redirect, url_for, flash
import pandas as pd
from app.blueprints.ogrenci_yonetimi import ogrenci_yonetimi_bp
from app.extensions import db
from app.blueprints.ogrenci_yonetimi.models import Ogrenci
from app.blueprints.ders_konu_yonetimi.models import Konu, Ders
from app.blueprints.calisma_programi.models import DersProgrami, DersIlerleme, KonuTakip
from app.blueprints.deneme_sinavlari.models import DenemeSonuc
from app.utils.session import set_aktif_ogrenci, get_aktif_ogrenci
from app.blueprints.ogrenci_yonetimi.services import OgrenciService

@ogrenci_yonetimi_bp.route('/')
def liste():
    """Tüm öğrencilerin listelendiği sayfa"""
    ogrenciler = Ogrenci.query.order_by(Ogrenci.numara).all()
    return render_template('ogrenci_yonetimi/ogrenciler.html', ogrenciler=ogrenciler)

@ogrenci_yonetimi_bp.route('/hizli-ara')
def hizli_ara():
    """Öğrenci numarasına göre hızlı arama ve profil sayfasına yönlendirme"""
    ogrenci_no = request.args.get('ogrenci_no', '')
    
    if not ogrenci_no:
        flash('Lütfen bir öğrenci numarası girin.', 'warning')
        return redirect(url_for('ogrenci_yonetimi.liste'))
    
    # Öğrenciyi numarasına göre bul
    ogrenci = Ogrenci.query.filter_by(numara=ogrenci_no).first()
    
    if not ogrenci:
        flash(f'"{ogrenci_no}" numaralı öğrenci bulunamadı.', 'danger')
        return redirect(url_for('ogrenci_yonetimi.liste'))
    
    # Öğrenci bulundu, profiline yönlendir
    return redirect(url_for('ogrenci_yonetimi.profil', ogrenci_id=ogrenci.id))

# 'Öğrenci Seçimini Temizle' fonksiyonu kaldırıldı

@ogrenci_yonetimi_bp.route('/excel-ile-ekle', methods=['GET', 'POST'])
def excel_ile_ekle():
    """Excel ile toplu öğrenci ekleme formu ve işlemi"""
    if request.method == 'POST':
        # Excel dosyası kontrolü
        if 'excel_dosya' not in request.files:
            flash('Lütfen bir Excel dosyası seçin!', 'danger')
            return redirect(url_for('ogrenci_yonetimi.excel_ile_ekle'))
        
        dosya = request.files['excel_dosya']
        
        # Dosya adı kontrolü
        if dosya.filename == '':
            flash('Lütfen bir Excel dosyası seçin!', 'danger')
            return redirect(url_for('ogrenci_yonetimi.excel_ile_ekle'))
        
        # Dosya uzantısı kontrolü
        if not dosya.filename.endswith(('.xlsx', '.xls')):
            flash('Lütfen geçerli bir Excel dosyası (.xlsx veya .xls) seçin!', 'danger')
            return redirect(url_for('ogrenci_yonetimi.excel_ile_ekle'))
        
        try:
            # Excel dosyasını oku (ilk satır başlık olarak kabul edilir)
            df = pd.read_excel(dosya)
            
            # Başarılı ve hatalı sayıları
            eklenen = 0
            mevcut = 0
            hatali = 0
            
            # Her satırı işle
            for index, row in df.iterrows():
                try:
                    # Eğer Excel başlıklara sahipse (ki olmalı)
                    try:
                        # Yeni sütun başlıklarına göre değerleri al
                        numara = str(row['Numara']).strip() if 'Numara' in row and pd.notna(row['Numara']) else None
                        
                        # Adı Soyadı sütunundan ad ve soyadı ayrıştırma
                        adi_soyadi = str(row['Adı Soyadı']).strip() if 'Adı Soyadı' in row and pd.notna(row['Adı Soyadı']) else None
                        
                        # Adı Soyadı'yı ad ve soyad olarak ayırma
                        if adi_soyadi and ' ' in adi_soyadi:
                            ad_parcalari = adi_soyadi.split(' ')
                            ad = ad_parcalari[0]
                            soyad = ' '.join(ad_parcalari[1:])  # Birden fazla soyadı olabilir
                        else:
                            ad = adi_soyadi
                            soyad = ""  # Boş soyad
                        
                        sinif = str(row['Sınıf']).strip() if 'Sınıf' in row and pd.notna(row['Sınıf']) else None
                        cinsiyet = str(row['Cinsiyet']).strip() if 'Cinsiyet' in row and pd.notna(row['Cinsiyet']) else None
                        
                        # İsteğe bağlı alanlar
                        telefon = str(row['Telefon']).strip() if 'Telefon' in row and pd.notna(row['Telefon']) else None
                        eposta = str(row['E-posta']).strip() if 'E-posta' in row and pd.notna(row['E-posta']) else None
                    except:
                        # Başlık yoksa indeks ile al
                        # Eski metod yedeği (kullanıcı başlıksız Excel şablonu kullanırsa)
                        if len(row) < 4:
                            hatali += 1
                            continue
                        
                        numara = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None
                        
                        # İlk sütun numara, ikinci ad-soyad olarak kabul et
                        adi_soyadi = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None
                        
                        # Adı Soyadı'yı ad ve soyad olarak ayırma
                        if adi_soyadi and ' ' in adi_soyadi:
                            ad_parcalari = adi_soyadi.split(' ')
                            ad = ad_parcalari[0]
                            soyad = ' '.join(ad_parcalari[1:])  # Birden fazla soyadı olabilir
                        else:
                            ad = adi_soyadi
                            soyad = ""  # Boş soyad
                        
                        sinif = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else None
                        cinsiyet = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else None
                        
                        # İsteğe bağlı alanlar (5. ve 6. sütunlar)
                        telefon = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else None
                        eposta = str(row.iloc[5]).strip() if len(row) > 5 and pd.notna(row.iloc[5]) else None
                    
                    # Gerekli alanların kontrolü
                    if not numara or not ad or not soyad or not sinif or not cinsiyet:
                        hatali += 1
                        continue
                    
                    # Öğrenci numarası kontrolü
                    mevcut_ogrenci = Ogrenci.query.filter_by(numara=numara).first()
                    if mevcut_ogrenci:
                        mevcut += 1
                        continue
                    
                    # Cinsiyet değerini standartlaştır
                    if cinsiyet.lower() in ['k', 'kız', 'kiz', 'k.', 'kadın', 'kadin']:
                        cinsiyet = 'Kız'
                    elif cinsiyet.lower() in ['e', 'erkek', 'e.']:
                        cinsiyet = 'Erkek'
                    else:
                        hatali += 1
                        continue
                    
                    # Yeni öğrenciyi ekle
                    yeni_ogrenci = Ogrenci(
                        numara=numara,
                        ad=ad,
                        soyad=soyad,
                        sinif=sinif,
                        cinsiyet=cinsiyet,
                        telefon=telefon,
                        eposta=eposta
                    )
                    
                    db.session.add(yeni_ogrenci)
                    eklenen += 1
                    
                except Exception as e:
                    hatali += 1
            
            # Veritabanına kaydet
            db.session.commit()
            
            # Bildirimleri oluştur
            if eklenen > 0:
                flash(f'{eklenen} öğrenci başarıyla eklendi!', 'success')
            
            if mevcut > 0:
                flash(f'{mevcut} öğrenci zaten sistemde kayıtlı olduğu için atlandı!', 'warning')
            
            if hatali > 0:
                flash(f'{hatali} öğrenci ekleme sırasında hata oluştu! Geçersiz veya eksik veriler.', 'warning')
            
            if eklenen == 0 and mevcut == 0:
                flash('Excel dosyasından hiçbir öğrenci eklenemedi!', 'danger')
            
            return redirect(url_for('ogrenci_yonetimi.liste'))
        
        except Exception as e:
            flash(f'Excel dosyası işlenirken bir hata oluştu: {str(e)}', 'danger')
            return redirect(url_for('ogrenci_yonetimi.excel_ile_ekle'))
    
    return render_template('ogrenci_yonetimi/excel_ile_ogrenci_ekle.html')

@ogrenci_yonetimi_bp.route('/ekle', methods=['GET', 'POST'])
def ekle():
    """Yeni öğrenci ekleme formu ve işlemi"""
    if request.method == 'POST':
        # Form verilerini al
        numara = request.form.get('numara')
        ad = request.form.get('ad')
        soyad = request.form.get('soyad')
        sinif = request.form.get('sinif')
        cinsiyet = request.form.get('cinsiyet')
        telefon = request.form.get('telefon')
        eposta = request.form.get('eposta')
        
        # Validasyon
        if not numara or not ad or not soyad or not sinif or not cinsiyet:
            flash('Lütfen tüm zorunlu alanları doldurun!', 'danger')
            return redirect(url_for('ogrenci_yonetimi.ekle'))
        
        # Öğrenci numarası kontrol
        mevcut_ogrenci = Ogrenci.query.filter_by(numara=numara).first()
        if mevcut_ogrenci:
            flash(f'"{numara}" numaralı öğrenci zaten sistemde kayıtlı!', 'danger')
            return redirect(url_for('ogrenci_yonetimi.ekle'))
        
        # Yeni öğrenciyi ekle
        yeni_ogrenci = Ogrenci(
            numara=numara,
            ad=ad,
            soyad=soyad,
            sinif=sinif,
            cinsiyet=cinsiyet,
            telefon=telefon if telefon else None,
            eposta=eposta if eposta else None
        )
        
        # Veritabanına kaydet
        db.session.add(yeni_ogrenci)
        db.session.commit()
        
        flash(f'"{ad} {soyad}" öğrencisi başarıyla eklendi!', 'success')
        return redirect(url_for('ogrenci_yonetimi.liste'))
    
    return render_template('ogrenci_yonetimi/ogrenci_ekle.html')

@ogrenci_yonetimi_bp.route('/<int:ogrenci_id>')
def profil(ogrenci_id):
    """Öğrenci profil sayfası"""
    ogrenci = Ogrenci.query.get_or_404(ogrenci_id)
    
    # Bu öğrenciyi aktif öğrenci olarak ayarla
    set_aktif_ogrenci(ogrenci_id)
    
    # Öğrencinin ders ilerlemeleri
    ders_ilerlemeleri = DersIlerleme.query.filter_by(ogrenci_id=ogrenci_id).all()
    
    # Ders bilgilerini ayrıca çekelim
    dersler = {d.id: d.ad for d in Ders.query.all()}
    
    # Öğrencinin deneme sonuçları (son 5 deneme)
    deneme_sonuclari = DenemeSonuc.query.filter_by(ogrenci_id=ogrenci_id).order_by(DenemeSonuc.tarih.desc()).limit(5).all()
    
    # Haftalık ders programı
    ders_programi = DersProgrami.query.filter_by(ogrenci_id=ogrenci_id).all()
    
    # Tamamlanan konular
    tamamlanan_konular = KonuTakip.query.filter_by(ogrenci_id=ogrenci_id, tamamlandi=True).count()
    
    # Toplam konular (öğrencinin derslerindeki)
    ogrenci_ders_ids = set(dp.ders_id for dp in ders_programi)
    toplam_konu_sayisi = Konu.query.filter(Konu.ders_id.in_(ogrenci_ders_ids)).count() if ogrenci_ders_ids else 0
    
    return render_template('ogrenci_yonetimi/ogrenci_profil.html', 
                         ogrenci=ogrenci, 
                         ders_ilerlemeleri=ders_ilerlemeleri,
                         dersler=dersler,
                         deneme_sonuclari=deneme_sonuclari,
                         ders_programi=ders_programi,
                         tamamlanan_konular=tamamlanan_konular,
                         toplam_konu_sayisi=toplam_konu_sayisi)

@ogrenci_yonetimi_bp.route('/<int:ogrenci_id>/duzenle', methods=['GET', 'POST'])
def duzenle(ogrenci_id):
    """Öğrenci bilgilerini düzenleme formu ve işlemi"""
    ogrenci = Ogrenci.query.get_or_404(ogrenci_id)
    
    if request.method == 'POST':
        # Form verilerini al
        numara = request.form.get('numara')
        ad = request.form.get('ad')
        soyad = request.form.get('soyad')
        sinif = request.form.get('sinif')
        cinsiyet = request.form.get('cinsiyet')
        telefon = request.form.get('telefon')
        eposta = request.form.get('eposta')
        
        # Validasyon
        if not numara or not ad or not soyad or not sinif or not cinsiyet:
            flash('Lütfen tüm zorunlu alanları doldurun!', 'danger')
            return redirect(url_for('ogrenci_yonetimi.duzenle', ogrenci_id=ogrenci_id))
        
        # Eğer numara değiştiyse ve başka öğrencide bu numara varsa
        if numara != ogrenci.numara:
            mevcut_ogrenci = Ogrenci.query.filter_by(numara=numara).first()
            if mevcut_ogrenci:
                flash(f'"{numara}" numaralı başka bir öğrenci zaten sistemde kayıtlı!', 'danger')
                return redirect(url_for('ogrenci_yonetimi.duzenle', ogrenci_id=ogrenci_id))
        
        # Öğrenci bilgilerini güncelle
        ogrenci.numara = numara
        ogrenci.ad = ad
        ogrenci.soyad = soyad
        ogrenci.sinif = sinif
        ogrenci.cinsiyet = cinsiyet
        ogrenci.telefon = telefon if telefon else None
        ogrenci.eposta = eposta if eposta else None
        
        # Veritabanına kaydet
        db.session.commit()
        
        flash(f'"{ad} {soyad}" öğrencisinin bilgileri başarıyla güncellendi!', 'success')
        return redirect(url_for('ogrenci_yonetimi.profil', ogrenci_id=ogrenci_id))
    
    return render_template('ogrenci_yonetimi/ogrenci_ekle.html', ogrenci=ogrenci)

@ogrenci_yonetimi_bp.route('/<int:ogrenci_id>/sil', methods=['POST'])
def sil(ogrenci_id):
    """Öğrenciyi sistemden silme işlemi"""
    # Öğrenci servis sınıfını kullanarak silme işlemini gerçekleştir    
    # Önce öğrenciyi çekelim
    ogrenci = Ogrenci.query.get_or_404(ogrenci_id)
    ogrenci_adi = f"{ogrenci.ad} {ogrenci.soyad}"
    
    # Eğer silinen öğrenci aktif öğrenci ise, aktif öğrenci bilgisini temizle
    aktif_ogrenci = get_aktif_ogrenci()
    if aktif_ogrenci and aktif_ogrenci.id == ogrenci_id:
        clear_aktif_ogrenci()
    
    # Servis metodunu kullanarak tüm ilişkili verileri silme
    result = OgrenciService.delete_ogrenci(ogrenci_id)
    
    if result.get('success') == True:
        flash(f'"{ogrenci_adi}" öğrencisi sistemden silindi!', 'success')
    else:
        flash(f'Öğrenci silinirken bir hata oluştu: {result.get("message")}', 'danger')
    
    return redirect(url_for('ogrenci_yonetimi.liste'))