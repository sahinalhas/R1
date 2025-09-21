
"""
API Routes
RESTful API için endpoint tanımlamaları
"""

from flask import jsonify, request
from app.api import api_bp
from app.utils.auth import api_auth_required
from app.blueprints.ogrenci_yonetimi.services import OgrenciService
from app.blueprints.gorusme_defteri.services import GorusmeService
from app.blueprints.etkinlik_kayit.services import EtkinlikService

@api_bp.route('/ogrenciler', methods=['GET'])
@api_auth_required
def get_ogrenciler():
    """Öğrencileri listele"""
    sinif = request.args.get('sinif')
    
    if sinif:
        ogrenciler = OgrenciService.get_ogrenciler_by_sinif(sinif)
    else:
        ogrenciler = OgrenciService.get_all_ogrenciler()
    
    return jsonify({
        'success': True,
        'data': [ogrenci.to_dict() for ogrenci in ogrenciler]
    })

@api_bp.route('/ogrenciler/<int:ogrenci_id>', methods=['GET'])
@api_auth_required
def get_ogrenci(ogrenci_id):
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
def get_gorusmeler():
    """Görüşmeleri listele"""
    baslangic = request.args.get('baslangic')
    bitis = request.args.get('bitis')
    ogrenci_id = request.args.get('ogrenci_id')
    
    gorusmeler = GorusmeService.get_gorusmeler(
        baslangic_tarihi=baslangic,
        bitis_tarihi=bitis,
        ogrenci_id=ogrenci_id
    )
    
    return jsonify({
        'success': True,
        'data': [gorusme.to_dict() for gorusme in gorusmeler]
    })

@api_bp.route('/etkinlikler', methods=['GET'])
@api_auth_required
def get_etkinlikler():
    """Etkinlikleri listele"""
    baslangic = request.args.get('baslangic')
    bitis = request.args.get('bitis')
    
    etkinlikler = EtkinlikService.get_etkinlikler(
        baslangic_tarihi=baslangic,
        bitis_tarihi=bitis
    )
    
    return jsonify({
        'success': True,
        'data': [etkinlik.to_dict() for etkinlik in etkinlikler]
    })
