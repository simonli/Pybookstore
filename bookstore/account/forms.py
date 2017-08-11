# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import input_required as ir

from bookstore.extensions import MySelectField
from bookstore.models.user import User, Role

class RegisterForm(FlaskForm):
    username = StringField(u'用户名', validators=[ir(u'用户名不能为空。')])
    email = StringField(u'邮箱', validators=[ir(u'邮件地址不能为空。')])
    password = PasswordField(u'密码', validators=[ir(u'密码不能为空。')])
    password_confirm = PasswordField(u'重复密码', validators=[ir(u'重复密码不能为空。')])
    submit = SubmitField(u'注册')

class LoginForm(FlaskForm):
    username = StringField(u'用户名', validators=[ir(u'用户名不能为空。')])
    password = PasswordField(u'密码', validators=[ir(u'密码不能为空。')])
    verifycode = StringField(u'验证码',validators=[ir(u'请输入验证码。')])
    submit = SubmitField(u'登录')
