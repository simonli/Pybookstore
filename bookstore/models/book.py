# -*- coding:utf-8 -*-
from datetime import datetime

from bookstore.extensions import db

books_tags = db.Table('book_tag',
                      db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
                      db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
                      )

books_categories = db.Table('book_category',
                            db.Column('category_id', db.Integer, db.ForeignKey('categories.id')),
                            db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
                            )


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)  # 书名
    author = db.Column(db.String(255))  # 作者
    logo = db.Column(db.String(255))  # 书的封面
    translator = db.Column(db.String(255))  # 译者
    publisher = db.Column(db.String(255))  # 出版社
    isbn = db.Column(db.String(100))  # ISBN号
    douban_id = db.Column(db.Integer, unique=True, index=True)  # 豆瓣ID
    douban_url = db.Column(db.String(255))
    douban_rating_score = db.Column(db.Integer, default=0)  # 豆瓣得分
    douban_rating_people = db.Column(db.Integer, default=0)  # 豆瓣评论人数
    catalog = db.Column(db.Text)  # 图书目录
    book_intro = db.Column(db.Text)  # 内容简介
    author_intro = db.Column(db.Text)  # 作者简介
    create_time = db.Column(db.DateTime, default=datetime.now)
    is_from = db.Column(db.String(255), default=u'douban')  # douban or diy
    tags = db.relationship('Tag', secondary=books_tags,
                           backref=db.backref('books', lazy='dynamic'))
    categories = db.relationship('Category', secondary=books_categories,
                                 backref=db.backref('books', lazy='dynamic'))

    book_edtions = db.relationship('BookEdition', backref='book', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Book, self).__init__(*args, **kwargs)


class BookEdition(db.Model):
    __tablename__ = 'book_editions'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 上传者
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    size = db.Column(db.Integer)  # byte字节
    push_count = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    checksum = db.Column(db.String(255))
    create_time = db.Column(db.DateTime, default=datetime.now)
    book_edition_comments = db.relationship('BookEditionComment', backref='book_edition', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(BookEdition, self).__init__(*args, **kwargs)


class BookEditionComment(db.Model):
    __tablename__ = 'book_edition_comments'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_edition_id = db.Column(db.Integer, db.ForeignKey('book_editions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 评价人
    at_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 评价哪个用户
    comment = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, *args, **kwargs):
        super(BookEditionComment, self).__init__(*args, **kwargs)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)


class BookPushRecord(db.Model):
    __tablename__ = 'book_push_records'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_edition_id = db.Column(db.Integer, db.ForeignKey('book_editions.id'))
    from_platform = db.Column(db.String(255))
    create_time = db.Column(db.DateTime, default=datetime.now)
    use_time = db.Column(db.Integer, default=0)
    delivery_status = db.Column(db.Integer, default=1)  # 0-失败 1-成功 3-未知
    destination_email = db.Column(db.String(255), nullable=False)

    def __init__(self, *args, **kwargs):
        super(BookPushRecord, self).__init__(*args, **kwargs)


class BookUploadRecord(db.Model):
    __tablename__ = 'book_upload_records'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_edition_id = db.Column(db.Integer, db.ForeignKey('book_editions.id'))
    create_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, *args, **kwargs):
        super(BookUploadRecord, self).__init__(*args, **kwargs)


class BookDownloadRecord(db.Model):
    __tablename__ = 'book_download_records'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_edition_id = db.Column(db.Integer, db.ForeignKey('book_editions.id'))
    user_agent = db.Column(db.String())
    create_time = db.Column(db.DateTime, default=datetime.now)  # 下载时间

    def __init__(self, *args, **kwargs):
        super(BookDownloadRecord, self).__init__(*args, **kwargs)
