from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.blueprints.auth.models import User


class LoginForm(FlaskForm):
    email = EmailField('E-posta Adresi', validators=[
        DataRequired(message='E-posta adresi gereklidir.'),
        Email(message='Geçerli bir e-posta adresi giriniz.')
    ])
    password = PasswordField('Parola', validators=[
        DataRequired(message='Parola gereklidir.')
    ])
    remember_me = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')


class RegisterForm(FlaskForm):
    email = EmailField('E-posta Adresi', validators=[
        DataRequired(message='E-posta adresi gereklidir.'),
        Email(message='Geçerli bir e-posta adresi giriniz.')
    ])
    ad = StringField('Ad', validators=[
        DataRequired(message='Ad gereklidir.'),
        Length(min=2, max=100, message='Ad en az 2, en fazla 100 karakter olmalıdır.')
    ])
    soyad = StringField('Soyad', validators=[
        DataRequired(message='Soyad gereklidir.'),
        Length(min=2, max=100, message='Soyad en az 2, en fazla 100 karakter olmalıdır.')
    ])
    password = PasswordField('Parola', validators=[
        DataRequired(message='Parola gereklidir.'),
        Length(min=6, message='Parola en az 6 karakter olmalıdır.')
    ])
    password2 = PasswordField('Parola Tekrarı', validators=[
        DataRequired(message='Parola tekrarı gereklidir.'),
        EqualTo('password', message='Parolalar eşleşmiyor.')
    ])
    submit = SubmitField('Kayıt Ol')
    
    def validate_email(self, email):
        # Email'i normalize ederek kontrol et
        normalized_email = email.data.lower().strip()
        user = User.query.filter_by(email=normalized_email).first()
        if user:
            raise ValidationError('Bu e-posta adresi zaten kullanılıyor.')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mevcut Parola', validators=[
        DataRequired(message='Mevcut parola gereklidir.')
    ])
    new_password = PasswordField('Yeni Parola', validators=[
        DataRequired(message='Yeni parola gereklidir.'),
        Length(min=6, message='Parola en az 6 karakter olmalıdır.')
    ])
    new_password2 = PasswordField('Yeni Parola Tekrarı', validators=[
        DataRequired(message='Yeni parola tekrarı gereklidir.'),
        EqualTo('new_password', message='Parolalar eşleşmiyor.')
    ])
    submit = SubmitField('Parolayı Güncelle')