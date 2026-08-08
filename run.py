import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Chỉ bật debug mode khi FLASK_DEBUG=1 trong biến môi trường.
    # Debug mode của Flask cho phép thực thi mã tùy ý qua trình debug trên
    # trình duyệt nếu lộ ra ngoài — tuyệt đối không bật ở production.
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug, host='0.0.0.0', port=5000)
