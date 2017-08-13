# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import equal_to
from wtforms.validators import input_required as ir


class RegisterForm(FlaskForm):
    username = StringField(u'用户名', validators=[ir(u'用户名不能为空.')])
    email = StringField(u'邮箱', validators=[ir(u'邮件地址不能为空.')])
    password = PasswordField(u'密码', validators=[
        ir(u'密码不能为空.'),
        equal_to('password_confirm', u'两次输入的密码不一致, 请重新输入.')
    ])
    password_confirm = PasswordField(u'重复密码', validators=[ir(u'重复密码不能为空.')])
    submit = SubmitField(u'注册')


class LoginForm(FlaskForm):
    username = StringField(u'用户名', validators=[ir(u'用户名不能为空.')])
    password = PasswordField(u'密码', validators=[ir(u'密码不能为空.')])
    verifycode = StringField(u'验证码', validators=[ir(u'请输入验证码.')])
    submit = SubmitField(u'登录')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'旧密码', validators=[ir(u'旧密码不能为空.')])
    new_password = PasswordField(u'新密码', validators=[
        ir(u'新密码不能为空.'),
        equal_to('new_password_confirm', u'两次输入的密码不一致, 请重新输入.')
    ])
    new_password_confirm = PasswordField(u'重复新密码', validators=[ir(u'重复新密码不能为空.')])
