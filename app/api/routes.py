
"""
API Routes
RESTful API için endpoint tanımlamaları
"""

from flask import jsonify, request
from app.api import api_bp
from app.utils.auth import api_auth_required, generate_jwt_token
from app.blueprints.ogrenci_yonetimi.services import OgrenciService
from app.blueprints.gorusme_defteri.services import GorusmeService
from app.blueprints.etkinlik_kayit.services import EtkinlikService
from app.blueprints.auth.models import User
from app.extensions import db
from datetime import datetime, timedelta

# Student CRUD API endpoints
@api_bp.route('/ogrenciler', methods=['GET'])
@api_auth_required
def get_ogrenciler(current_user):
    """Öğrencileri listele"""
    sinif = request.args.get('sinif')
    
    # Filter by class if provided
    ogrenciler = OgrenciService.get_all_ogrenciler()
    if sinif:
        ogrenciler = [o for o in ogrenciler if o.sinif == sinif]
    
    return jsonify({
        'success': True,
        'data': [ogrenci.to_dict() for ogrenci in ogrenciler]
    })

@api_bp.route('/ogrenciler/<int:ogrenci_id>', methods=['GET'])
@api_auth_required
def get_ogrenci(ogrenci_id, current_user):
    """Öğrenci detayı"""
    ogrenci = OgrenciService.get_ogrenci_by_id(ogrenci_id)
    
    if not ogrenci:
        return jsonify({
            'success': False,
            'error': 'Öğrenci bulunamadı'
        }), 404
    
    return jsonify({
        'success': True,
        'data': ogrenci.to_dict()
    })

@api_bp.route('/gorusmeler', methods=['GET'])
@api_auth_required
def get_gorusmeler(current_user):
    """Görüşmeleri listele"""
    baslangic = request.args.get('baslangic')
    bitis = request.args.get('bitis')
    ogrenci_id = request.args.get('ogrenci_id')
    
    # Get all meetings and filter
    gorusmeler = GorusmeService.get_all_gorusme_kayitlari()
    
    # Apply filters
    if baslangic:
        baslangic_date = datetime.strptime(baslangic, '%Y-%m-%d').date()
        gorusmeler = [g for g in gorusmeler if g.tarih >= baslangic_date]
    if bitis:
        bitis_date = datetime.strptime(bitis, '%Y-%m-%d').date()
        gorusmeler = [g for g in gorusmeler if g.tarih <= bitis_date]
    if ogrenci_id:
        gorusmeler = [g for g in gorusmeler if g.ogrenci_id == int(ogrenci_id)]
    
    return jsonify({
        'success': True,
        'data': [gorusme.to_dict() for gorusme in gorusmeler]
    })

@api_bp.route('/etkinlikler', methods=['GET'])
@api_auth_required
def get_etkinlikler(current_user):
    """Etkinlikleri listele"""
    baslangic = request.args.get('baslangic')
    bitis = request.args.get('bitis')
    
    # Get all activities and filter
    etkinlikler = EtkinlikService.get_all_etkinlikler()
    
    # Apply filters
    if baslangic:
        baslangic_date = datetime.strptime(baslangic, '%Y-%m-%d').date()
        etkinlikler = [e for e in etkinlikler if e.etkinlik_tarihi >= baslangic_date]
    if bitis:
        bitis_date = datetime.strptime(bitis, '%Y-%m-%d').date()
        etkinlikler = [e for e in etkinlikler if e.etkinlik_tarihi <= bitis_date]
    
    return jsonify({
        'success': True,
        'data': [etkinlik.to_dict() for etkinlik in etkinlikler]
    })

# Student CRUD endpoints
@api_bp.route('/ogrenciler', methods=['POST'])
@api_auth_required
def create_ogrenci(current_user):
    """Create new student"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'JSON data required'}), 400
        
        # Validate required fields
        required_fields = ['numara', 'ad', 'soyad', 'sinif', 'cinsiyet']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        result = OgrenciService.create_ogrenci(
            numara=data['numara'],
            ad=data['ad'],
            soyad=data['soyad'],
            sinif=data['sinif'],
            cinsiyet=data['cinsiyet'],
            telefon=data.get('telefon'),
            eposta=data.get('eposta')
        )
        
        if result['success']:
            return jsonify({'success': True, 'data': {'id': result['id']}}), 201
        else:
            return jsonify({'success': False, 'error': result['message']}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'Invalid request data'}), 400

@api_bp.route('/ogrenciler/<int:ogrenci_id>', methods=['PUT'])
@api_auth_required
def update_ogrenci(ogrenci_id, current_user):
    """Update student"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'JSON data required'}), 400
        
        # Validate required fields
        required_fields = ['numara', 'ad', 'soyad', 'sinif', 'cinsiyet']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        result = OgrenciService.update_ogrenci(
            ogrenci_id=ogrenci_id,
            numara=data['numara'],
            ad=data['ad'],
            soyad=data['soyad'],
            sinif=data['sinif'],
            cinsiyet=data['cinsiyet'],
            telefon=data.get('telefon'),
            eposta=data.get('eposta')
        )
        
        if result['success']:
            return jsonify({'success': True, 'message': result['message']})
        else:
            return jsonify({'success': False, 'error': result['message']}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'Invalid request data'}), 400

@api_bp.route('/ogrenciler/<int:ogrenci_id>', methods=['DELETE'])
@api_auth_required
def delete_ogrenci(ogrenci_id, current_user):
    """Delete student"""
    try:
        result = OgrenciService.delete_ogrenci(ogrenci_id)
        
        if result['success']:
            return jsonify({'success': True, 'message': result['message']})
        else:
            return jsonify({'success': False, 'error': result['message']}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to delete student'}), 500

# Meeting CRUD endpoints
@api_bp.route('/gorusmeler', methods=['POST'])
@api_auth_required
def create_gorusme(current_user):
    """Create new meeting"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'JSON data required'}), 400
        
        # Validate required fields
        required_fields = ['gorusulen_kisi', 'gorusme_konusu', 'baslangic_saati', 'bitis_saati']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Parse date
        tarih = None
        if data.get('tarih'):
            try:
                tarih = datetime.strptime(data['tarih'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format (use YYYY-MM-DD)'}), 400
        
        result = GorusmeService.create_gorusme_kaydi(
            ogrenci_id=data.get('ogrenci_id'),
            tarih=tarih,
            baslangic_saati=data['baslangic_saati'],
            bitis_saati=data['bitis_saati'],
            gorusulen_kisi=data['gorusulen_kisi'],
            kisi_rolu=data.get('kisi_rolu'),
            yakinlik_derecesi=data.get('yakinlik_derecesi'),
            gorusme_konusu=data['gorusme_konusu'],
            calisma_alani=data.get('calisma_alani'),
            calisma_kategorisi=data.get('calisma_kategorisi'),
            hizmet_turu=data.get('hizmet_turu'),
            kurum_isbirligi=data.get('kurum_isbirligi'),
            gorusme_yeri=data.get('gorusme_yeri'),
            disiplin_gorusmesi=data.get('disiplin_gorusmesi', False),
            adli_sevk=data.get('adli_sevk', False),
            calisma_yontemi=data.get('calisma_yontemi'),
            ozet=data.get('ozet')
        )
        
        if result['success']:
            return jsonify({'success': True, 'data': {'id': result['kayit_id']}}), 201
        else:
            return jsonify({'success': False, 'error': result['message']}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'Invalid request data'}), 400

@api_bp.route('/gorusmeler/<int:gorusme_id>', methods=['PUT'])
@api_auth_required
def update_gorusme(gorusme_id, current_user):
    """Update meeting"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'JSON data required'}), 400
        
        # Parse date if provided
        tarih = None
        if data.get('tarih'):
            try:
                tarih = datetime.strptime(data['tarih'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format (use YYYY-MM-DD)'}), 400
        
        result = GorusmeService.update_gorusme_kaydi(
            kayit_id=gorusme_id,
            ogrenci_id=data.get('ogrenci_id'),
            tarih=tarih,
            baslangic_saati=data.get('baslangic_saati'),
            bitis_saati=data.get('bitis_saati'),
            gorusulen_kisi=data.get('gorusulen_kisi'),
            kisi_rolu=data.get('kisi_rolu'),
            yakinlik_derecesi=data.get('yakinlik_derecesi'),
            gorusme_konusu=data.get('gorusme_konusu'),
            calisma_alani=data.get('calisma_alani'),
            calisma_kategorisi=data.get('calisma_kategorisi'),
            hizmet_turu=data.get('hizmet_turu'),
            kurum_isbirligi=data.get('kurum_isbirligi'),
            gorusme_yeri=data.get('gorusme_yeri'),
            disiplin_gorusmesi=data.get('disiplin_gorusmesi'),
            adli_sevk=data.get('adli_sevk'),
            calisma_yontemi=data.get('calisma_yontemi'),
            ozet=data.get('ozet')
        )
        
        if result['success']:
            return jsonify({'success': True, 'message': result['message']})
        else:
            return jsonify({'success': False, 'error': result['message']}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'Invalid request data'}), 400

@api_bp.route('/gorusmeler/<int:gorusme_id>', methods=['DELETE'])
@api_auth_required
def delete_gorusme(gorusme_id, current_user):
    """Delete meeting"""
    try:
        result = GorusmeService.delete_gorusme_kaydi(gorusme_id)
        
        if result['success']:
            return jsonify({'success': True, 'message': result['message']})
        else:
            return jsonify({'success': False, 'error': result['message']}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to delete meeting'}), 500

# Activity CRUD endpoints
@api_bp.route('/etkinlikler', methods=['POST'])
@api_auth_required
def create_etkinlik(current_user):
    """Create new activity"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'JSON data required'}), 400
        
        # Validate required fields
        required_fields = ['etkinlik_tarihi', 'calisma_yontemi', 'aciklama', 'hedef_turu', 'faaliyet_turu']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Parse date
        try:
            etkinlik_tarihi = datetime.strptime(data['etkinlik_tarihi'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format (use YYYY-MM-DD)'}), 400
        
        form_data = {
            'etkinlik_tarihi': etkinlik_tarihi,
            'calisma_yontemi': data['calisma_yontemi'],
            'aciklama': data['aciklama'],
            'hedef_turu': data['hedef_turu'],
            'faaliyet_turu': data['faaliyet_turu'],
            'ogretmen_sayisi': data.get('ogretmen_sayisi', 0),
            'veli_sayisi': data.get('veli_sayisi', 0),
            'diger_katilimci_sayisi': data.get('diger_katilimci_sayisi', 0),
            'erkek_ogrenci_sayisi': data.get('erkek_ogrenci_sayisi', 0),
            'kiz_ogrenci_sayisi': data.get('kiz_ogrenci_sayisi', 0),
            'sinif_bilgisi': data.get('sinif_bilgisi', ''),
            'resmi_yazi_sayisi': data.get('resmi_yazi_sayisi', '')
        }
        
        etkinlik = EtkinlikService.create_etkinlik(form_data)
        return jsonify({'success': True, 'data': {'id': etkinlik.id}}), 201
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'Invalid request data'}), 400

@api_bp.route('/etkinlikler/<int:etkinlik_id>', methods=['PUT'])
@api_auth_required
def update_etkinlik(etkinlik_id, current_user):
    """Update activity"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'JSON data required'}), 400
        
        # Validate required fields
        required_fields = ['etkinlik_tarihi', 'calisma_yontemi', 'aciklama', 'hedef_turu', 'faaliyet_turu']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Parse date
        try:
            etkinlik_tarihi = datetime.strptime(data['etkinlik_tarihi'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format (use YYYY-MM-DD)'}), 400
        
        form_data = {
            'etkinlik_tarihi': etkinlik_tarihi,
            'calisma_yontemi': data['calisma_yontemi'],
            'aciklama': data['aciklama'],
            'hedef_turu': data['hedef_turu'],
            'faaliyet_turu': data['faaliyet_turu'],
            'ogretmen_sayisi': data.get('ogretmen_sayisi', 0),
            'veli_sayisi': data.get('veli_sayisi', 0),
            'diger_katilimci_sayisi': data.get('diger_katilimci_sayisi', 0),
            'erkek_ogrenci_sayisi': data.get('erkek_ogrenci_sayisi', 0),
            'kiz_ogrenci_sayisi': data.get('kiz_ogrenci_sayisi', 0),
            'sinif_bilgisi': data.get('sinif_bilgisi', ''),
            'resmi_yazi_sayisi': data.get('resmi_yazi_sayisi', '')
        }
        
        etkinlik = EtkinlikService.update_etkinlik(etkinlik_id, form_data)
        if etkinlik:
            return jsonify({'success': True, 'message': 'Activity updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Activity not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'Invalid request data'}), 400

@api_bp.route('/etkinlikler/<int:etkinlik_id>', methods=['DELETE'])
@api_auth_required
def delete_etkinlik(etkinlik_id, current_user):
    """Delete activity"""
    try:
        success = EtkinlikService.delete_etkinlik(etkinlik_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Activity deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Activity not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to delete activity'}), 500

# Authentication API endpoints
@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """API Login endpoint"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({
            'success': False,
            'error': 'Email ve parola gereklidir'
        }), 400
    
    email = data['email'].lower().strip()
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(data['password']):
        if user.aktif:
            token = generate_jwt_token(user.id)
            return jsonify({
                'success': True,
                'data': {
                    'token': token,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'tam_ad': user.tam_ad
                    }
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Hesabınız aktif değil'
            }), 403
    else:
        return jsonify({
            'success': False,
            'error': 'Hatalı email veya parola'
        }), 401

@api_bp.route('/auth/logout', methods=['POST'])
@api_auth_required
def api_logout(current_user):
    """API Logout endpoint"""
    # JWT is stateless, logout is handled client-side by removing token
    return jsonify({
        'success': True,
        'message': 'Başarıyla çıkış yapıldı'
    })

@api_bp.route('/auth/me', methods=['GET'])
@api_auth_required
def api_me(current_user):
    """Get current user info"""
    return jsonify({
        'success': True,
        'data': {
            'id': current_user.id,
            'email': current_user.email,
            'tam_ad': current_user.tam_ad
        }
    })

# Dashboard API endpoints
@api_bp.route('/dashboard/stats', methods=['GET'])
@api_auth_required
def api_dashboard_stats(current_user):
    """Dashboard istatistikleri"""
    try:
        # Toplam öğrenci sayısı
        ogrenci_sayisi = OgrenciService.get_ogrenci_sayisi()
        
        # Bu ay görüşme sayısı
        bu_ay_baslangic = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        bu_ay_bitis = (bu_ay_baslangic + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        bu_ay_gorusme_sayisi = GorusmeService.get_gorusme_sayisi(bu_ay_baslangic, bu_ay_bitis)
        
        # Bu ay etkinlik sayısı
        bu_ay_etkinlik_sayisi = EtkinlikService.get_etkinlik_sayisi(bu_ay_baslangic, bu_ay_bitis)
        
        # Ortalama ilerleme hesabı (basit implementasyon)
        ortalama_ilerleme = 75.0  # Placeholder - will implement later
        
        return jsonify({
            'success': True,
            'data': {
                'ogrenci_sayisi': ogrenci_sayisi,
                'bu_ay_gorusme_sayisi': bu_ay_gorusme_sayisi,
                'bu_ay_etkinlik_sayisi': bu_ay_etkinlik_sayisi,
                'ortalama_ilerleme': ortalama_ilerleme
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'İstatistikler yüklenirken hata: {str(e)}'
        }), 500

@api_bp.route('/dashboard/recent-students', methods=['GET'])
@api_auth_required
def api_recent_students(current_user):
    """Son eklenen öğrenciler"""
    try:
        students = OgrenciService.get_all_ogrenciler()[:5]  # Get first 5 students as recent
        return jsonify({
            'success': True,
            'data': [student.to_dict() for student in students]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Son öğrenciler yüklenirken hata: {str(e)}'
        }), 500
