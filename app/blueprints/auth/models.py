from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    ad = db.Column(db.String(100), nullable=False)
    soyad = db.Column(db.String(100), nullable=False)
    aktif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def set_password(self, password):
        """Parolayı hash'leyerek kaydet"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Parolayı kontrol et"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def tam_ad(self):
        """Tam adı döndür"""
        return f"{self.ad} {self.soyad}"
    
    def __repr__(self):
        return f'<User {self.email}>'