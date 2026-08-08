from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db, limiter
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit('10 per hour', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        # Validate
        errors = []
        if not username or len(username) < 3:
            errors.append('Tên đăng nhập phải có ít nhất 3 ký tự.')
        if not email or '@' not in email:
            errors.append('Email không hợp lệ.')
        if len(password) < 6:
            errors.append('Mật khẩu phải có ít nhất 6 ký tự.')
        if password != confirm:
            errors.append('Mật khẩu xác nhận không khớp.')
        if User.query.filter_by(username=username).first():
            errors.append('Tên đăng nhập đã được sử dụng.')
        if User.query.filter_by(email=email).first():
            errors.append('Email đã được đăng ký.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('auth/register.html',
                                   username=username, email=email, full_name=full_name)

        user = User(username=username, email=email, full_name=full_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('10 per minute', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.', 'danger')
                return render_template('auth/login.html', email=email)
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get('next')
            flash(f'Chào mừng, {user.full_name or user.username}!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Email hoặc mật khẩu không đúng.', 'danger')
            return render_template('auth/login.html', email=email)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('auth.login'))
