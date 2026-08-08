from flask import Blueprint, render_template, jsonify, abort, make_response, request
from flask_login import login_required, current_user
from app import db
from app.models.summary import Summary

history_bp = Blueprint('history', __name__)

PER_PAGE = 10


@history_bp.route('/history')
@login_required
def history_page():
    page = request.args.get('page', 1, type=int)
    pagination = (current_user.summaries
                  .order_by(Summary.created_at.desc())
                  .paginate(page=page, per_page=PER_PAGE, error_out=False))
    return render_template('main/history.html', summaries=pagination.items,
                            pagination=pagination)


@history_bp.route('/api/history/<int:sid>')
@login_required
def api_get(sid):
    s = Summary.query.filter_by(id=sid, user_id=current_user.id).first_or_404()
    return jsonify(s.to_dict())


@history_bp.route('/api/history/<int:sid>', methods=['DELETE'])
@login_required
def api_delete(sid):
    s = Summary.query.filter_by(id=sid, user_id=current_user.id).first_or_404()
    db.session.delete(s)
    db.session.commit()
    return jsonify({'message': 'Đã xóa thành công.'})


@history_bp.route('/api/history/download/<int:sid>')
@login_required
def api_download(sid):
    s = Summary.query.filter_by(id=sid, user_id=current_user.id).first_or_404()
    content = f"BẢN TÓM TẮT\n{'='*50}\n\n{s.summary_text}\n\n{'='*50}\nVĂN BẢN GỐC\n{'='*50}\n\n{s.original_text}"
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=tomtat_{sid}.txt'
    return response
