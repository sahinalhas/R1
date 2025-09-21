"""
Yetkilendirme ve oturum yönetimi işlevleri
Bu modül, tüm blueprint'lerde tutarlı oturum yönetimi sağlamak için kullanılır.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request, current_app
from app.utils.session import get_aktif_ogrenci, set_aktif_ogrenci
from app.blueprints.ogrenci_yonetimi.models import Ogrenci

def session_required(ogrenci_zorunlu=True):
    """
    Oturum kontrolü için dekoratör
    Eğer ogrenci_zorunlu=True ise aktif bir öğrenci seçili değilse kullanıcıyı öğrenci listesine yönlendirir
    Eğer ogrenci_zorunlu=False ise öğrenci seçilmese bile sayfayı gösterir
    
    Args:
        ogrenci_zorunlu: Öğrenci seçiminin zorunlu olup olmadığı (default: True)
        
    Returns:
        Dekoratör fonksiyonu
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(ogrenci_id=None, *args, **kwargs):
            # Eğer oturum zorunlu değilse doğrudan işleme devam et
            if current_app.config.get('SESSION_REQUIRED', True) is False:
                return f(ogrenci_id, *args, **kwargs)
                
            # Url'den gelen ogrenci_id parametresi varsa, aktif öğrenciyi ayarla
            if ogrenci_id:
                set_aktif_ogrenci(ogrenci_id)
                return f(ogrenci_id, *args, **kwargs)
                
            # Aktif öğrenci kontrolü
            aktif_ogrenci = get_aktif_ogrenci()
            
            # Eğer öğrenci zorunlu değilse, öğrenci olmadan devam et
            if not ogrenci_zorunlu:
                return f(ogrenci_id=None, *args, **kwargs)
                
            # Öğrenci zorunlu ve aktif öğrenci yoksa
            if not aktif_ogrenci:
                flash('Lütfen bir öğrenci seçin.', 'warning')
                return redirect(url_for('ogrenci_yonetimi.liste'))
                
            # Eğer url'de ogrenci_id yoksa ve aktif öğrenci varsa, aktif öğrenciyi kullan
            return f(aktif_ogrenci.id, *args, **kwargs)
        
        return decorated_function
    
    # Eğer dekoratör doğrudan bir fonksiyona uygulanmışsa (yaygın kullanım)
    if callable(ogrenci_zorunlu):
        f = ogrenci_zorunlu
        ogrenci_zorunlu = True
        return decorator(f)
    
    # Parametreli kullanım için
    return decorator

def ogrenci_required(f):
    """
    Öğrenci kontrol dekoratörü
    URL'den gelen öğrenci ID'sini kontrol eder ve öğrenciyi görünüme aktarır
    
    Args:
        f: Dekorlanacak view fonksiyonu
        
    Returns:
        Wrapper fonksiyonu
    """
    @wraps(f)
    def decorated_function(ogrenci_id=None, *args, **kwargs):
        # Öğrenci ID'si kontrolü
        if not ogrenci_id:
            flash('Geçersiz öğrenci ID.', 'danger')
            return redirect(url_for('ogrenci_yonetimi.liste'))
            
        # Öğrenciyi veritabanından al
        ogrenci = Ogrenci.query.get_or_404(ogrenci_id)
        
        # Mevcut aktif öğrenciyi oturumda ayarla
        set_aktif_ogrenci(ogrenci_id)
        
        # Fonksiyonu çağır ve öğrenciyi parametre olarak gönder
        kwargs['ogrenci'] = ogrenci
        return f(ogrenci_id, *args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """
    Admin yetki kontrolü için dekoratör (ileride kullanılacak)
    Kullanıcı admin değilse ana sayfaya yönlendirir
    
    Args:
        f: Dekorlanacak view fonksiyonu
        
    Returns:
        Wrapper fonksiyonu
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Admin kontrolü gerçekleştir
        # Şu an için bypass ediyoruz, ileride admin sistemi geldiğinde aktif olacak
        return f(*args, **kwargs)
    
    return decorated_function

def log_activity(activity_type, description=None):
    """
    Kullanıcı aktivitelerini loglama dekoratörü (ileride kullanılacak)
    
    Args:
        activity_type: Aktivite tipi (örn: 'ogrenci_ekle', 'ders_guncelle')
        description: Aktivite açıklaması
        
    Returns:
        Dekoratör fonksiyonu
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # İşlemi gerçekleştir
            result = f(*args, **kwargs)
            
            # TODO: Aktivite logu kaydet
            # Şu an için bypass ediyoruz, ileride loglama sistemi geldiğinde aktif olacak
            
            return result
        return decorated_function
    return decorator