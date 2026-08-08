from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.summary import Summary
from sqlalchemy import func
from app import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Thống kê cá nhân
    total = current_user.summaries.count()
    recent = current_user.summaries.order_by(Summary.created_at.desc()).limit(5).all()

    # Tổng ký tự đã tóm tắt
    total_chars = db.session.query(
        func.sum(Summary.original_length)
    ).filter_by(user_id=current_user.id).scalar() or 0

    # Tổng ký tự đã tiết kiệm
    saved_chars = db.session.query(
        func.sum(Summary.original_length - Summary.summary_length)
    ).filter_by(user_id=current_user.id).scalar() or 0

    return render_template('main/dashboard.html',
                           total=total,
                           recent=recent,
                           total_chars=total_chars,
                           saved_chars=saved_chars)
