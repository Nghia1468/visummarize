import os
import secrets
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# SECRET_KEY: bắt buộc đặt qua biến môi trường khi triển khai thật, để phiên
# đăng nhập không bị mất mỗi lần restart và để không ai đoán được key.
# Nếu không đặt (ví dụ khi chạy local để dev), tự sinh 1 key ngẫu nhiên cho
# lần chạy này thay vì dùng một chuỗi cố định — key cố định trong mã nguồn
# là rủi ro bảo mật (bất kỳ ai đọc được mã nguồn cũng giả mạo được session).
_env_secret = os.environ.get('SECRET_KEY')
if not _env_secret:
    print("⚠️  Chưa đặt biến môi trường SECRET_KEY — đang dùng key ngẫu nhiên "
          "chỉ tồn tại trong phiên chạy này (session sẽ mất khi restart app). "
          "Đặt SECRET_KEY trong .env trước khi triển khai thật.")


class Config:
    SECRET_KEY = _env_secret or secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'database', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB max upload
    ALLOWED_EXTENSIONS = {'txt'}

    # Bảo mật form/API
    WTF_CSRF_TIME_LIMIT = None  # token CSRF không hết hạn theo thời gian (chỉ theo session)
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')

    # Tài khoản admin khởi tạo lần đầu — nên đặt qua biến môi trường,
    # tránh hardcode mật khẩu mặc định trong mã nguồn.
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')  # None => tự sinh ngẫu nhiên

    # Bật debug mode CHỈ khi chạy local dev, tuyệt đối không bật ở production
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
