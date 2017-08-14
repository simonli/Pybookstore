# -*- coding:utf-8 -*-
import cStringIO

import os
from flask import Blueprint, request, render_template, redirect, url_for, flash, abort, current_app
from flask import Response, session
from flask_login import login_user, logout_user, login_required, current_user

from bookstore.extensions import db
from bookstore.models.user import User, Role, PushSetting
from bookstore.utils import generate_verification_code, get_extension, get_namebasetime
from .forms import RegisterForm, LoginForm, ChangePasswordForm, SettingsUsernameForm, SettingsEmailForm, \
    SettingsPushForm, SettingsAvatarForm

mod = Blueprint('account', __name__)


@mod.route('/')
@mod.route('/index')
def index():
    return render_template('main/index.html')


@mod.route('/register/', methods=['GET', 'POST'])
def register():
    user = User()
    form = RegisterForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.password = form.password.data
        user.email = form.email.data
        role = Role.query.filter_by(name='Free').first()
        user.role_id = role.id
        db.session.add(user)
        db.session.commit()
        flash(u'欢迎您，注册成功！', 'success')
        return redirect(url_for('frontend.index'))
    return render_template('account/register.html', form=form)


@mod.route('/login/', methods=['GET', 'POST'])
def login():
    return_url = request.args.get("next") or request.form.get("next")
    print "8" * 100
    print return_url
    form = LoginForm()
    if form.validate_on_submit():
        if session['verifycode'].lower() != form.verifycode.data.lower():
            flash(u'验证码不正确', 'danger')
            return render_template('account/login.html', form=form)
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.verify_password(form.password.data):
                login_user(user)
                flash(u'登陆成功！欢迎回来，%s!' % user.username, 'success')
                del session['verifycode']

                return redirect(return_url)
            else:
                flash(u'密码不正确。', 'danger')
        else:
            flash(u'用户不存在。', 'danger')
    # if form.errors:
    #     flash(u'登陆失败，请尝试重新登陆.', 'danger')
    return render_template('account/login.html', form=form, next=return_url)


@mod.route('/logout/')
@login_required
def logout():
    logout_user()
    flash(u'您已退出登陆。', 'success')
    return redirect(url_for('frontend.index'))


@mod.route('/verifycode/')
def verifycode():
    tmps = cStringIO.StringIO()
    code, image = generate_verification_code()
    print code
    session['verifycode'] = code
    image.save(tmps, "jpeg")
    res = Response()
    res.headers["Content-Type"] = "image/JPEG;charset=UTF-8"
    res.set_data(tmps.getvalue())
    return res


@mod.route('/profile/<string:username>/')
@login_required
def profile(username):
    if current_user.username != username:
        abort(403)
    checkin_records = []
    # CheckinRecord.query.filter_by(user_id= current_user.id).order_by(
    # CheckinRecord.create_time.desc()).all()



    total_score = 0
    for c in checkin_records:
        total_score = total_score + c.score
    return render_template('account/profile.html')


@mod.route('/settings/push')
@login_required
def settings_push():
    form = SettingsPushForm(obj=current_user)
    if form.validate_on_submit():
        push_setting = PushSetting()
        push_setting.user = current_user
        push_setting.email = form.email.data
        db.session.add(push_setting)
        db.session.commit()
        flash(u'推送邮箱添加成功.')
        return redirect(url_for('.settings_push'))
    else:
        push_records = PushSetting.query.filter_by(user_id=current_user.id).order_by(
            PushSetting.create_time.desc()).all()
        return render_template('account/settings_push.html', push_records=push_records)


@mod.route('/settings/username')
@login_required
def settings_username():
    form = SettingsUsernameForm(obj=current_user)
    if form.validate_on_submit():
        user = current_user
        user.username = form.username.data
        current_user.username = form.username.data
        db.session.add(user)
        db.session.commit()
        flash(u'用户名修改完成, 新的用户名是:%s' % form.username.data)
        return redirect(url_for('.settings_username'))
    else:
        return render_template('account/settings_username.html')


@mod.route('/settings/email')
@login_required
def settings_email():
    form = SettingsEmailForm(obj=current_user)
    if form.validate_on_submit():
        user = current_user
        user.email = form.email.data
        current_user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash(u'登陆邮箱修改完成, 新的登录邮箱是:%s' % form.email.data)
        return redirect(url_for('.settings_email'))
    else:
        return render_template('account/settings_email.html')


@mod.route('/settings/avatar')
@login_required
def settings_avatar():
    form = SettingsAvatarForm()
    if form.validate_on_submit():
        if 'avatar' in request.files:
            file = form.avatar.data
            ext = get_extension(file.filename)
            upload_folder = current_app.config.get('UPLOAD_AVATAR_FOLDER')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            dest_filename = get_namebasetime() + '.' + ext
            dest_filepath = os.path.join(upload_folder, dest_filename)
            file.seek(0)
            file.save(dest_filepath)  # 保存文件
            flash(u'头像上传成功.')
            return redirect(url_for(".settings_avatar"))
    else:
        u = User.query.get(current_user.id)
        return render_template('account/settings_avatar.html', user=u)


@mod.route('/settings/change_password')
@login_required
def settings_change_password():
    form = ChangePasswordForm(obj=current_user)
    error = None
    if form.validate_on_submit():
        user = current_user
        user.password = form.new_password.data
        db.session.add(user)
        db.session.commit()
        flash(u'密码修改成功.')
        return redirect('.settings_change_password')
    else:
        return render_template('account/change_password.html', error=error)


@mod.route('/settings/upgrade')
@login_required
def settings_upgrade():
    pass
