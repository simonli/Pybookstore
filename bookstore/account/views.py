# -*- coding:utf-8 -*-
from flask import current_app, Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask import Response, session
from datetime import datetime
from flask_login import current_user
from bookstore.extensions import db
from bookstore.utils import unique_id
from flask_login import login_required
from bookstore.models.user import User, Role
from .forms import RegisterForm, LoginForm
import cStringIO
from bookstore.utils import generate_verification_code
from flask_login import login_user, logout_user, login_required, current_user


mod = Blueprint('account', __name__)


@mod.route('/')
@mod.route('/index')
def index():
    return render_template('main/index.html')


@mod.route('/register', methods=['GET', 'POST'])
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


@mod.route('/login', methods=['GET', 'POST'])
def login():
    return_url = request.args.get("next") or request.form.get("next")
    print "8"*100
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


@mod.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已退出登陆。', 'success')
    return redirect(url_for('frontend.index'))


@mod.route('/verifycode')
def verifycode():
    tmps = cStringIO.StringIO()
    code, image = generate_verification_code()
    print code
    session['verifycode'] =  code
    image.save(tmps, "jpeg")
    res = Response()
    res.headers["Content-Type"] = "image/JPEG;charset=UTF-8"
    res.set_data(tmps.getvalue())
    return res
