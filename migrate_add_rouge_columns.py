"""
Migration thủ công: thêm 2 cột reference_summary, rouge_scores vào bảng
summaries cho database ĐÃ TỒN TẠI TỪ TRƯỚC (trước khi có tính năng ROUGE).

Vì dự án chưa dùng công cụ migration (như Flask-Migrate/Alembic), db.create_all()
chỉ tạo bảng khi CHƯA tồn tại — không tự thêm cột mới vào bảng đã có sẵn.
Script này bổ sung 2 cột đó bằng ALTER TABLE, giữ nguyên toàn bộ dữ liệu cũ.

Cách chạy (1 lần duy nhất, sau khi đã dừng server Flask):
    python migrate_add_rouge_columns.py

An toàn khi chạy nhiều lần: nếu cột đã tồn tại, script tự bỏ qua, không báo lỗi.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'app.db')

NEW_COLUMNS = [
    ('reference_summary', 'TEXT'),
    ('rouge_scores', 'TEXT'),
]


def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def main():
    if not os.path.exists(DB_PATH):
        print(f"Không tìm thấy database tại {DB_PATH} — có thể bạn chưa từng chạy app.")
        print("Không cần chạy migration này, cứ chạy 'python run.py' như bình thường.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    added = []
    skipped = []

    for col_name, col_type in NEW_COLUMNS:
        if column_exists(cursor, 'summaries', col_name):
            skipped.append(col_name)
            continue
        cursor.execute(f"ALTER TABLE summaries ADD COLUMN {col_name} {col_type}")
        added.append(col_name)

    conn.commit()
    conn.close()

    if added:
        print(f"✅ Đã thêm cột: {', '.join(added)}")
    if skipped:
        print(f"ℹ️  Đã có sẵn, bỏ qua: {', '.join(skipped)}")
    if not added and not skipped:
        print("Không có gì để làm.")

    print("\nXong. Toàn bộ dữ liệu cũ (tài khoản, lịch sử) được giữ nguyên.")
    print("Giờ có thể chạy lại: python run.py")


if __name__ == '__main__':
    main()
