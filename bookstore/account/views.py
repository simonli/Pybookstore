# -*- coding:utf-8 -*-
import cStringIO

from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from flask import Response, session
from flask_login import login_user, logout_user, login_required, current_user

from bookstore.extensions import db
from bookstore.models.user import User, Role
from bookstore.utils import generate_verification_code
from bookstore.utils import unique_id
from .forms import RegisterForm, LoginForm, ChangePasswordForm

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
        user.id = unique_id()
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
    pass


@mod.route('/settings/username')
@login_required
def settings_username():
    error = None
    if request.method == 'POST':
        username_new = request.form['username']
        if username_new:
            user = User.query.filter_by(username=username_new.strip()).first()
            if not user:
                user = current_user
                user.username = username_new
                current_user.username = username_new
                db.session.add(user)
                db.session.commit()
                flash(u'用户名修改完成, 您新的用户名是:%s' % username_new)
                return redirect(url_for('.settings_username'))
            else:
                error = u'该用户名: %s 已经存在, 请您换一个.' % username_new
                return render_template('account/settings_username.html', error=error)
        else:
            error = u'用户名不能为空.'
            return render_template('account/settings_username.html', error=error)
    else:
        return render_template('account/settings_username.html', error=error)


@mod.route('/settings/email')
@login_required
def settings_email():
    error = None
    if request.method == 'POST':
        email_new = request.form['email']
        if email_new:
            user = User.query.filter_by(email=email_new.strip()).first()
            if not user:
                user = current_user
                user.email = email_new
                current_user.email = email_new
                db.session.add(user)
                db.session.commit()
                flash(u'登录邮箱修改完成, 您新的登录邮箱是:%s' % email_new)
                return redirect(url_for('.settings_email'))
            else:
                error = u'该邮箱: %s 已经存在, 请您换一个.' % email_new
                return render_template('account/settings_email.html', error=error)
        else:
            error = u'登录邮箱不能为空.'
            return render_template('account/settings_email.html', error=error)
    else:
        return render_template('account/settings_email.html', error=error)


@mod.route('/settings/avatar')
@login_required
def settings_avatar():
    pass


@mod.route('/settings/change_password')
@login_required
def settings_change_password():
    form = ChangePasswordForm()
    error = None
    if form.validate_on_submit():
        user = current_user
        if user.verify_password(form.old_password.data):
            user.password = form.new_password.data
            db.session.add(user)
            db.session.commit()
            flash(u'密码修改成功.')
            return redirect('.settings_change_password')
        else:
            error = u'旧密码不正确.'
            return render_template('account/change_password.html', error=error)
    else:
        return render_template('account/change_password.html', error=error)


@mod.route('/settings/upgrade')
@login_required
def settings_upgrade():
    pass
