"""
Yetkilendirme ve oturum yönetimi işlevleri
Bu modül, tüm blueprint'lerde tutarlı oturum yönetimi sağlamak için kullanılır.
"""

from functools import wraps
from flask import redirect, url_for, flash, request, current_app, jsonify
from urllib.parse import urlparse, urljoin
import jwt
from datetime import datetime, timedelta

def session_required(ogrenci_zorunlu=True):
    """
    Session management disabled - decorator bypassed for system compatibility
    This decorator is no longer active as session management has been removed
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(ogrenci_id=None, *args, **kwargs):
            # Session management disabled - pass through to function
            return f(ogrenci_id, *args, **kwargs)
        return decorated_function
    
    # Handle both decorator usages
    if callable(ogrenci_zorunlu):
        f = ogrenci_zorunlu
        return decorator(f)
    
    return decorator

def ogrenci_required(f):
    """
    Student validation decorator - simplified version without session management
    """
    @wraps(f)
    def decorated_function(ogrenci_id=None, *args, **kwargs):
        if not ogrenci_id:
            flash('Geçersiz öğrenci ID.', 'danger')
            return redirect(url_for('ogrenci_yonetimi.liste'))
        
        # Import here to avoid circular import
        from app.blueprints.ogrenci_yonetimi.models import Ogrenci
        ogrenci = Ogrenci.query.get_or_404(ogrenci_id)
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

def api_auth_required(f):
    """
    JWT authentication decorator for API routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401
        
        try:
            # Decode token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
            # Import here to avoid circular import
            from app.blueprints.auth.models import User
            current_user = User.query.get(current_user_id)
            
            if not current_user or not current_user.aktif:
                return jsonify({'success': False, 'error': 'Invalid token'}), 401
                
            # Pass user to the route
            kwargs['current_user'] = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
    
    return decorated_function

def generate_jwt_token(user_id):
    """
    Generate JWT token for user
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def is_safe_url(target):
    """
    Check if a URL is safe for redirects (prevents open redirect attacks)
    
    Args:
        target: URL to check
        
    Returns:
        bool: True if URL is safe, False otherwise
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc