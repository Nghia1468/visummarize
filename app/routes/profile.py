from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_info':
            full_name = request.form.get('full_name', '').strip()
            current_user.full_name = full_name
            db.session.commit()
            flash('Cập nhật thông tin thành công.', 'success')

        elif action == 'change_password':
            old_pw = request.form.get('old_password', '')
            new_pw = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')

            if not current_user.check_password(old_pw):
                flash('Mật khẩu cũ không đúng.', 'danger')
            elif len(new_pw) < 6:
                flash('Mật khẩu mới phải có ít nhất 6 ký tự.', 'danger')
            elif new_pw != confirm_pw:
                flash('Mật khẩu xác nhận không khớp.', 'danger')
            else:
                current_user.set_password(new_pw)
                db.session.commit()
                flash('Đổi mật khẩu thành công.', 'success')

        return redirect(url_for('profile.profile_page'))

    return render_template('main/profile.html')
