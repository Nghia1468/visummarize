from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
from app import db, limiter
from app.models.summary import Summary
from app.nlp.nlp_service import summarize, METHODS, DEFAULT_METHOD
from app.nlp.rouge_evaluator import evaluate_rouge

summarize_bp = Blueprint('summarize', __name__)

ALLOWED_EXTENSIONS = {'txt'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@summarize_bp.route('/summarize')
@login_required
def summarize_page():
    return render_template('main/summarize.html', methods=list(METHODS.keys()),
                            default_method=DEFAULT_METHOD)


@summarize_bp.route('/api/summarize', methods=['POST'])
@login_required
@limiter.limit('20 per minute')
def api_summarize():
    """API tóm tắt văn bản."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dữ liệu không hợp lệ.'}), 400

    text = data.get('text', '').strip()
    method = data.get('method', DEFAULT_METHOD)
    if method not in METHODS:
        method = DEFAULT_METHOD
    ratio = data.get('ratio', 0.3)
    use_mmr = bool(data.get('use_mmr', True))

    try:
        ratio = float(ratio)
    except (TypeError, ValueError):
        return jsonify({'error': 'Tỷ lệ tóm tắt không hợp lệ.'}), 400

    # Gọi NLP service
    result = summarize(text, method=method, ratio=ratio, use_mmr=use_mmr)

    if result.get('error'):
        return jsonify({'error': result['error']}), 400

    keywords_str = ', '.join(result['keywords']) if result.get('keywords') else None

    # Lưu vào database
    record = Summary(
        user_id=current_user.id,
        original_text=text,
        summary_text=result['summary'],
        method=result['method'],
        ratio=ratio,
        original_length=result['original_length'],
        summary_length=result['summary_length'],
        processing_time=result['processing_time'],
        keywords=keywords_str
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        'summary': result['summary'],
        'keywords': result.get('keywords', []),
        'method': result['method'],
        'original_length': result['original_length'],
        'summary_length': result['summary_length'],
        'sentence_count': result['sentence_count'],
        'selected_count': result['selected_count'],
        'processing_time': result['processing_time'],
        'summary_id': record.id,
        'sentences': result['sentences'],
        'selected_indices': result['selected_indices'],
        'compression': round((1 - result['summary_length'] / result['original_length']) * 100, 1)
    })


@summarize_bp.route('/api/upload', methods=['POST'])
@login_required
@limiter.limit('20 per minute')
def api_upload():
    """Upload file .txt và trả về nội dung."""
    if 'file' not in request.files:
        return jsonify({'error': 'Không tìm thấy file.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Chưa chọn file.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Chỉ hỗ trợ file .txt.'}), 400

    try:
        content = file.read().decode('utf-8')
    except UnicodeDecodeError:
        try:
            file.seek(0)
            content = file.read().decode('latin-1')
        except Exception:
            return jsonify({'error': 'Không thể đọc file. Hãy đảm bảo file được mã hóa UTF-8.'}), 400

    if len(content.strip()) == 0:
        return jsonify({'error': 'File trống.'}), 400

    return jsonify({'text': content, 'filename': secure_filename(file.filename)})


@summarize_bp.route('/api/evaluate/<int:sid>', methods=['POST'])
@login_required
@limiter.limit('20 per minute')
def api_evaluate(sid):
    """Đánh giá 1 bản tóm tắt đã lưu bằng ROUGE, so với bản tham chiếu
    do người dùng tự nhập (thường là bản tóm tắt do con người viết)."""
    record = Summary.query.filter_by(id=sid, user_id=current_user.id).first_or_404()

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dữ liệu không hợp lệ.'}), 400

    reference = data.get('reference', '').strip()
    if len(reference) < 20:
        return jsonify({'error': 'Bản tóm tắt tham chiếu quá ngắn (tối thiểu 20 ký tự).'}), 400

    scores = evaluate_rouge(record.summary_text, reference)

    # Lưu lại để xem trong lịch sử mà không cần đánh giá lại
    record.reference_summary = reference
    record.rouge_scores = json.dumps(scores, ensure_ascii=False)
    db.session.commit()

    return jsonify({'rouge_scores': scores, 'summary_id': record.id})
