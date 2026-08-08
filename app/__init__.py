import os
import secrets
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục.'
login_manager.login_message_category = 'warning'

csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=['200 per hour'])


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Tạo thư mục upload nếu chưa có
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'database'), exist_ok=True)

    # Đăng ký blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.summarize import summarize_bp
    from app.routes.history import history_bp
    from app.routes.profile import profile_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(summarize_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        _create_admin(app)

    return app


def _create_admin(app):
    """Tạo tài khoản admin mặc định nếu chưa có.

    Ưu tiên lấy mật khẩu từ biến môi trường ADMIN_PASSWORD. Nếu không có,
    tự sinh một mật khẩu ngẫu nhiên và in ra console — tránh hardcode
    mật khẩu mặc định cố định trong mã nguồn (ai đọc được code cũng biết
    được mật khẩu admin của mọi lần cài đặt).
    """
    from app.models.user import User
    if not User.query.filter_by(role='admin').first():
        password = app.config.get('ADMIN_PASSWORD') or secrets.token_urlsafe(12)
        admin = User(
            username='admin',
            email=app.config.get('ADMIN_EMAIL', 'admin@example.com'),
            full_name='Quản trị viên',
            role='admin'
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print("=" * 60)
        print("✅ Đã tạo tài khoản admin mặc định:")
        print(f"   Email:    {admin.email}")
        print(f"   Mật khẩu: {password}")
        print("   -> Hãy đăng nhập và đổi mật khẩu ngay, hoặc đặt biến môi")
        print("      trường ADMIN_PASSWORD trước khi chạy lần đầu.")
        print("=" * 60)
