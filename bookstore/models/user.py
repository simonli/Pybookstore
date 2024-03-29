# -*- coding:utf-8 -*-
from datetime import datetime

from flask_login import UserMixin

from bookstore.extensions import db, login_manager, bcrypt
from bookstore.helper import utils


class Permission:
    FREE = 0x01
    PRO = 0x02
    ULTRA = 0x03
    ADMIN = 0xff


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    show_name = db.Column(db.String(100))
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Role, self).__init__(*args, **kwargs)

    @staticmethod
    def initial_roles():
        roles = {
            'Free': (Permission.FREE, True, u'免费用户'),
            'Pro': (Permission.PRO, False, u'Pro用户'),
            'Ultra': (Permission.ULTRA, False, u'超级用户'),
            'Admin': (Permission.ADMIN, False, u'管理员')
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            role.show_name = roles[r][2]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class PushSetting(db.Model):
    __tablename__ = 'push_settings'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    email = db.Column(db.String(255))
    create_time = db.Column(db.DateTime, default=datetime.now)
    is_default = db.Column(db.Integer, default=0)  # 1 is default

    def __init__(self, *args, **kwargs):
        super(PushSetting, self).__init__(*args, **kwargs)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True, index=True)
    _password_hash = db.Column('password', db.String(255), nullable=False, server_default=u'')
    email = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255))
    last_login_time = db.Column(db.DateTime, default=datetime.now)
    last_login_ip = db.Column(db.String(50), default='')
    login_count = db.Column(db.Integer, nullable=False, default=0)
    is_delete = db.Column(db.Integer, default=0)  # o-OK, 1-deleted
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    create_time = db.Column(db.DateTime, default=datetime.now())
    push_settings = db.relationship(PushSetting, backref='user', lazy='dynamic')
    point_count = db.Column(db.Integer, default=0)  # 总积分


    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password)

    @property
    def is_admin(self):
        return self.can(Permission.ADMIN)

    @property
    def is_pro(self):
        return self.can(Permission.PRO)

    def verify_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions | permissions) == permissions

    @staticmethod
    def initial_admin():
        u = User()
        u.username = 'admin'
        u.password = 'admin'
        u.email = 'admin@localhost'
        u.role = Role.query.filter_by(name='Admin').first()

        u1 = User()
        u1.username = 'simon'
        u1.password = 'cncode'
        u1.email = 'simonli@live.com'
        u1.role = Role.query.filter_by(name='Admin').first()

        db.session.add(u)
        db.session.add(u1)
        db.session.commit()


# callback function for flask-login extentsion
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(is_delete=0).filter_by(id=user_id).first()


class UserCheckinRecord(db.Model):
    __tablename__ = 'user_checkin_records'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    score = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, default=datetime.now)  # 下载时间

    def __init__(self, *args, **kwargs):
        super(UserCheckinRecord, self).__init__(*args, **kwargs)


POINT_SOURCE = utils.enum(PUSH='Push', DOWNLOAD='Download', UPLOAD='Upload')


class UserPoint(db.Model):
    __tablename__ = 'user_points'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    point = db.Column(db.Integer, default=0)
    point_source = db.Column(db.String(30))
    source_id = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, *args, **kwargs):
        super(UserPoint, self).__init__(*args, **kwargs)
