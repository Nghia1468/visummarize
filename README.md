# ViSummarize – Hệ thống Tóm tắt Văn bản Tiếng Việt

Đồ án môn học: Xử lý Ngôn ngữ Tự nhiên
Stack: Python Flask + SQLite + Bootstrap 5

> Bản này đã được nâng cấp thuật toán tóm tắt (TextRank + MMR + trích xuất từ
> khóa), bổ sung phân trang lịch sử, và vá các lỗ hổng bảo mật quan trọng
> (CSRF, debug mode, rate limiting, tài khoản admin mặc định). Xem chi tiết ở
> mục "Những gì đã thay đổi" bên dưới.

---

## Cài đặt

### 1. Tạo môi trường ảo
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Cài thư viện
```bash
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường
```bash
cp .env.example .env
# Mở .env và điền SECRET_KEY (bắt buộc khi deploy thật)
```

### 4. Chạy ứng dụng
```bash
python run.py
```

Mở trình duyệt: **http://localhost:5000**

---

## Tài khoản admin mặc định

Ở lần chạy đầu tiên, nếu chưa có admin nào trong hệ thống, app sẽ:
- Dùng `ADMIN_EMAIL` / `ADMIN_PASSWORD` trong `.env` nếu bạn đã đặt, **hoặc**
- Tự sinh một mật khẩu ngẫu nhiên và **in ra console** — hãy đăng nhập và đổi
  mật khẩu ngay sau đó.

(Không còn mật khẩu admin cố định hardcode trong mã nguồn như bản trước.)

---

## Cấu trúc thư mục

```
project/
├── app/
│   ├── __init__.py          # Flask app factory (CSRF, rate limiter, DB, admin bootstrap)
│   ├── models/               # SQLAlchemy models (User, Summary)
│   ├── routes/                # Flask blueprints (auth, main, summarize, history, profile, admin)
│   ├── nlp/                   # Module NLP
│   │   ├── preprocessor.py         # Chuẩn hóa, tách câu, tách từ, loại stopword
│   │   ├── vectorizer.py           # TF-IDF + ma trận tương đồng cosine (dùng chung)
│   │   ├── tfidf_summarizer.py     # Tóm tắt theo điểm TF-IDF
│   │   ├── textrank_summarizer.py  # Tóm tắt bằng đồ thị TextRank (PageRank)
│   │   ├── mmr.py                  # Giảm trùng lặp câu (Maximal Marginal Relevance)
│   │   ├── keyword_extractor.py    # Trích xuất từ khóa chính
│   │   └── nlp_service.py          # Điểm vào chính, chọn phương pháp
│   ├── templates/              # Jinja2 HTML templates
│   └── static/                 # CSS, JS, uploads
├── database/                   # SQLite DB (tự tạo khi chạy lần đầu)
├── config.py
├── run.py
├── .env.example
└── requirements.txt
```

---

## Tính năng

- ✅ Đăng ký / Đăng nhập / Đăng xuất (có rate limiting chống dò mật khẩu)
- ✅ Tóm tắt văn bản: chọn giữa **TextRank** (mặc định, xét quan hệ giữa các
  câu) và **TF-IDF** (nhanh, chấm điểm từng câu độc lập)
- ✅ Tùy chọn giảm trùng lặp câu (MMR) — tránh 2 câu ý gần giống nhau cùng lọt
  vào bản tóm tắt
- ✅ Trích xuất từ khóa chính của văn bản
- ✅ Upload file .TXT
- ✅ Chọn tỷ lệ tóm tắt (10% – 50%)
- ✅ Sao chép & tải kết quả
- ✅ Lịch sử tóm tắt cá nhân (có phân trang)
- ✅ Hồ sơ cá nhân & đổi mật khẩu
- ✅ Trang Admin: quản lý user, thống kê, lịch sử
- ✅ Bảo vệ CSRF trên toàn bộ form và API POST/PUT/DELETE

---

## Những gì đã thay đổi so với bản gốc

**Thuật toán:**
- Thêm **TextRank** (`textrank_summarizer.py`) dùng `networkx` — xây đồ thị
  tương đồng giữa các câu và chạy PageRank, cho kết quả mạch lạc hơn so với
  chỉ cộng dồn điểm TF-IDF từng câu độc lập.
- Thêm **MMR** (`mmr.py`) để giảm trùng lặp nội dung giữa các câu được chọn,
  áp dụng cho cả 2 phương pháp.
- Thêm **trích xuất từ khóa** (`keyword_extractor.py`), tận dụng lại ma trận
  TF-IDF đã tính, không tốn thêm chi phí xử lý đáng kể.
- Tách `vectorizer.py` dùng chung để tránh tính TF-IDF lặp lại nhiều lần.
- Người dùng có thể chọn phương pháp và bật/tắt MMR ngay trên giao diện.

**Tính năng:**
- Lịch sử tóm tắt giờ có phân trang (`Summary.query...paginate()`), tránh
  tải toàn bộ bản ghi cùng lúc khi user có nhiều lịch sử.
- Kết quả tóm tắt hiển thị kèm từ khóa chính.

**Bảo mật (đã vá):**
- Bật `CSRFProtect` (flask-wtf) cho toàn bộ form và request POST/PUT/DELETE;
  các lệnh `fetch()` trong JS tự động đính kèm token qua header
  `X-CSRFToken`.
- `SECRET_KEY` không còn hardcode cố định — bắt buộc đặt qua `.env` khi
  deploy thật, có cảnh báo rõ ràng nếu thiếu.
- `debug=True` không còn bật cứng trong `run.py` — chỉ bật khi
  `FLASK_DEBUG=1`.
- Tài khoản admin mặc định không còn mật khẩu cố định trong mã nguồn — đọc
  từ `.env` hoặc tự sinh ngẫu nhiên, in ra console.
- Thêm rate limiting (`flask-limiter`) cho `/login`, `/register`,
  `/api/summarize`, `/api/upload` để chống brute-force và spam.

---

## Ghi chú

- Phím tắt: `Ctrl + Enter` để tóm tắt nhanh
- File upload tối đa 2MB, chỉ hỗ trợ `.txt`
- Database SQLite tự động tạo khi chạy lần đầu — phù hợp demo/đồ án, nếu
  triển khai thật với nhiều người dùng đồng thời nên chuyển sang
  PostgreSQL/MySQL qua biến môi trường `DATABASE_URL`.
