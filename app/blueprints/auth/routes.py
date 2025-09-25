from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse, urljoin
from app.blueprints.auth import auth_bp
from app.blueprints.auth.forms import LoginForm, RegisterForm, ChangePasswordForm
from app.blueprints.auth.models import User
from app.extensions import db


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Giriş sayfası"""
    # Eğer kullanıcı zaten giriş yapmışsa ana sayfaya yönlendir
    if current_user.is_authenticated:
        return redirect(url_for('ana_sayfa.index'))
    
    # Login formu oluştur
    form = LoginForm()

    # Geliştirme sırasında otomatik doldurma
    try:
        from flask import current_app
        if request.method == 'GET' and current_app.config.get('AUTO_LOGIN_ENABLED'):
            form.email.data = current_app.config.get('AUTO_LOGIN_EMAIL')
            form.password.data = current_app.config.get('AUTO_LOGIN_PASSWORD')
    except Exception:
        pass

    # POST istekleri için login işlemi
    if form.validate_on_submit():
        # Email'i normalize et
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(form.password.data):
            if user.aktif:
                login_user(user, remember=form.remember_me.data)
                flash(f'Hoş geldiniz, {user.tam_ad}!', 'success')
                
                # Güvenli yönlendirme - sadece aynı domain'e izin ver
                next_page = request.args.get('next')
                if next_page and is_safe_url(next_page):
                    return redirect(next_page)
                return redirect(url_for('ana_sayfa.index'))
            else:
                flash('Hesabınız aktif değil. Lütfen yöneticiye başvurun.', 'warning')
        else:
            flash('Hatalı e-posta adresi veya parola.', 'danger')
    
    # Form doğrulaması başarısız olursa login sayfasını tekrar göster
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Kayıt sayfası"""
    # Eğer kullanıcı zaten giriş yapmışsa ana sayfaya yönlendir
    if current_user.is_authenticated:
        return redirect(url_for('ana_sayfa.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Yeni kullanıcı oluştur
        user = User()
        user.email = form.email.data.lower().strip()  # Email'i normalize et
        user.ad = form.ad.data.strip()
        user.soyad = form.soyad.data.strip()
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            flash('Kayıt işlemi başarılı! Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'danger')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/dev-login', methods=['POST'])
def dev_login():
    """Geliştirme aşaması için hızlı giriş"""
    try:
        # Geliştirme kullanıcısını bul veya oluştur
        dev_email = "dev@test.com"
        user = User.query.filter_by(email=dev_email).first()
        
        if not user:
            # Geliştirme kullanıcısı yoksa oluştur
            user = User(
                email=dev_email,
                ad="Geliştirici",
                soyad="Test",
                aktif=True
            )
            user.set_password("123456")
            db.session.add(user)
            db.session.commit()
            
        if user.aktif:
            login_user(user, remember=True)
            flash(f'Geliştirici girişi başarılı! Hoş geldiniz {user.tam_ad}', 'success')
            return redirect(url_for('ana_sayfa.index'))
        else:
            flash('Geliştirici hesabı aktif değil.', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash('Geliştirici girişi sırasında hata oluştu.', 'danger')
    
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Çıkış işlemi - CSRF koruması için POST"""
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('ana_sayfa.index'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Parola değiştirme"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            try:
                db.session.commit()
                flash('Parolanız başarıyla güncellendi.', 'success')
                return redirect(url_for('ana_sayfa.index'))
            except Exception as e:
                db.session.rollback()
                flash('Parola güncellenirken bir hata oluştu.', 'danger')
        else:
            flash('Mevcut parolanız hatalı.', 'danger')
    
    return render_template('auth/change_password.html', form=form)


@auth_bp.route('/profile')
@login_required
def profile():
    """Kullanıcı profili"""
    return render_template('auth/profile.html')


def is_safe_url(target):
    """URL'in güvenli olup olmadığını kontrol et (open redirect koruması)"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
