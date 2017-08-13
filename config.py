# -*- coding:utf-8 -*-

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    DEBUG = True
    SECRET_KEY = '\xb33]\xdbO\xb4k\x8fU\x00ZQ\xac\x83\x89Y)\x01\x10\xfa\x06\xa8\x80\x8e'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bookstore.db'
    # SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://postgres:cncode@localhost:5432/putidms"
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    WTF_CSRF_ENABLED = True
    ITEMS_PER_PAGE = 10

    MAX_CONTENT_LENGTH = 60 * 1024 * 1024  # 全站禁止上传附件限制60MB以下

    UPLOAD_FOLDER = basedir + os.sep + 'uploads'

    UPLOAD_BOOK_FOLDER = UPLOAD_FOLDER + os.sep + 'books'
    ALLOWED_EXTENSIONS = set(['mobi', 'epub', 'txt', 'pdf'])
    ALLOWED_BOOK_SIZE = 50 * 1024 * 1024  # 上传图书大小50MB

    UPLOAD_LOGO_FOLDER = UPLOAD_FOLDER + os.sep + 'logos'
    ALLOWED_LOGO_SIZE = 2 * 1024 * 1024


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    pass


configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
