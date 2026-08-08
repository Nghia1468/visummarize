from flask import Blueprint, render_template, jsonify, abort
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.summary import Summary
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@admin_required
def dashboard():
    total_users = User.query.filter_by(role='user').count()
    total_summaries = Summary.query.count()
    active_users = User.query.filter_by(is_active=True, role='user').count()

    # Thống kê 7 ngày gần nhất
    stats = []
    for i in range(6, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        count = Summary.query.filter(
            func.date(Summary.created_at) == day
        ).count()
        stats.append({'date': day.strftime('%d/%m'), 'count': count})

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_summaries=total_summaries,
                           active_users=active_users,
                           stats=stats)


@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.filter_by(role='user').order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/api/users/<int:uid>/toggle', methods=['POST'])
@admin_required
def toggle_user(uid):
    user = db.session.get(User, uid)
    if not user or user.is_admin():
        abort(404)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'kích hoạt' if user.is_active else 'khóa'
    return jsonify({'message': f'Tài khoản đã được {status}.', 'is_active': user.is_active})


@admin_bp.route('/history')
@admin_required
def history():
    summaries = Summary.query.order_by(Summary.created_at.desc()).limit(200).all()
    return render_template('admin/history.html', summaries=summaries)


@admin_bp.route('/api/history/<int:sid>', methods=['DELETE'])
@admin_required
def delete_summary(sid):
    s = db.session.get(Summary, sid)
    if not s:
        abort(404)
    db.session.delete(s)
    db.session.commit()
    return jsonify({'message': 'Đã xóa.'})
