# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, ValidationError, FileField
from wtforms.validators import equal_to, email, input_required as ir
from bookstore.models.user import User, PushSetting
from bookstore.extensions import FileSizeAllowed


class RegisterForm(FlaskForm):
    username = StringField(u'用户名', validators=[ir(u'用户名不能为空.')])
    email = StringField(u'邮箱', validators=[
        ir(u'邮件地址不能为空.'),
        email(u'不是有效的Email地址')
    ])
    password = PasswordField(u'密码', validators=[ir(u'密码不能为空.')])
    password_confirm = PasswordField(u'重复密码', validators=[
        ir(u'重复密码不能为空.'),
        equal_to('password', u'两次输入的密码不一致, 请重新输入.')
    ])
    submit = SubmitField(u'注册')


class LoginForm(FlaskForm):
    username = StringField(u'用户名', validators=[ir(u'用户名不能为空.')])
    password = PasswordField(u'密码', validators=[ir(u'密码不能为空.')])
    verifycode = StringField(u'验证码', validators=[ir(u'请输入验证码.')])
    submit = SubmitField(u'登录')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'旧密码', validators=[ir(u'旧密码不能为空.')])
    new_password = PasswordField(u'新密码', validators=[ir(u'新密码不能为空.')])
    new_password_confirm = PasswordField(u'重复新密码', validators=[
        ir(u'重复新密码不能为空.'),
        equal_to('new_password', u'两次输入的密码不一致, 请重新输入.')
    ])

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.user = kwargs.get('obj')

    def validate_old_password(self, field):
        if not self.user.verify_password(field.data):
            raise ValidationError(u'旧密码不正确.')


class SettingsUsernameForm(FlaskForm):
    username = StringField(u'用户名', validators=[ir(u'用户名不能为空.')])

    def __init__(self, *args, **kwargs):
        super(SettingsUsernameForm, self).__init__(*args, **kwargs)
        self.user = kwargs.get('obj')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError(u'该用户名: %s 已经存在, 请您换一个.' % field.data)


class SettingsEmailForm(FlaskForm):
    email = StringField(u'登录邮箱', validators=[
        ir(u'登录邮箱不能为空.'),
        email(message=u'无效的邮箱地址.')
    ])

    def __init__(self, *args, **kwargs):
        super(SettingsEmailForm, self).__init__(*args, **kwargs)
        self.user = kwargs.get('obj')

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError(u'该邮箱: %s 已经存在, 请您换一个.' % field.data)


class SettingsPushForm(FlaskForm):
    email = StringField(u'邮箱', validators=[
        ir(u'邮箱不能为空.'),
        email(message=u'无效的邮箱地址.')
    ])

    def __init__(self, *args, **kwargs):
        super(SettingsPushForm, self).__init__(*args, **kwargs)
        self.user = kwargs.get('obj')

    def validate_email(self, field):
        if field.data == PushSetting.query.filter_by(user_id=self.user.id).filter_by(email=field.data).first():
            raise ValidationError(u'箱邮箱已存在,请勿重复添加.')


class SettingsAvatarForm(FlaskForm):
    avatar = FileField(u'头像', validators=[
        FileRequired(u'请选择要上传的头像文件.'),
        FileAllowed(['jpg', 'png', 'gif', 'jpeg'], u'请上传jpg,jpeg,png,gif格式的头像.'),
        FileSizeAllowed(2 * 1024 * 1024, u'头像不能超过2MB.')
    ])
