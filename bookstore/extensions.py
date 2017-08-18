# -*- coding:utf-8 -*-
import re

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from wtforms import SelectField
from wtforms.validators import Regexp, HostnameValidation, ValidationError, StopValidation

bcrypt = Bcrypt()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'account.login'
login_manager.login_message = u'请登录后访问该页面！'
login_manager.login_message_category = "warning"


class MySelectField(SelectField):
    def iter_choices(self):
        for value, label in self.choices:
            if self.default:
                yield (value, label, self.coerce(value) == self.coerce(self.default))
            else:
                yield (value, label, self.coerce(value) == self.data)


class NewURL(Regexp):
    def __init__(self, require_tld=True, message=None):
        regex = r'^(http|https)+://(?P<host>[^/:]+)(?P<port>:[0-9]+)?(?P<path>\/.*)?$'
        super(NewURL, self).__init__(regex, re.IGNORECASE, message)
        self.validate_hostname = HostnameValidation(
            require_tld=require_tld,
            allow_ip=True,
        )

    def __call__(self, form, field):
        message = self.message
        if message is None:
            message = field.gettext('Invalid URL.')

        match = super(NewURL, self).__call__(form, field, message)
        if not self.validate_hostname(match.group('host')):
            raise ValidationError(message)


class FileSizeAllowed(object):
    """
    检查上传文件的大小,默认2MB
    """

    def __init__(self, allowed_size=2 * 1024 * 1024, message=None):
        self.allowed_size = allowed_size
        self.message = message

    def __call__(self, form, field):
        field.data.seek(0)
        size = len(field.data.read())
        field.data.seek(0)
        if size > self.allowed_size:
            if self.message is None:
                message = field.gettext('File size exceeded.')
            else:
                message = self.message
            raise StopValidation(message)
