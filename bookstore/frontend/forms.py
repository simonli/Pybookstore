# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField
from wtforms.validators import input_required as ir


class UploadForm(FlaskForm):
    book_file = FileField(u'文件', validators=[
        FileRequired(u'请选择您要上传的图书文件.'),
        FileAllowed(['mobi', 'epub', 'pdf', 'txt'], u'不支持的图书格式,请上传mobi,epub,pdf,txt格式的图书.')
    ])
    douban_url = StringField(u'豆瓣链接', validators=[
        ir(u'豆瓣链接不能为空,请先在右侧搜索图书，然后点击图书的“复制链接”.')])
    book_edition_commnet = TextAreaField(u'版本简介')

    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)


class UploadFormExt(FlaskForm):
    name = StringField(u'书名:', validators=[ir(u'书名不能为空.')])
    author = StringField(u'作者:', validators=[ir(u'作者不能为空.')])
    book_intro = TextAreaField(u'内容简介:', validators=[ir(u'内容简介不能为空.')])
    logo = FileField(u'图书封面', validators=[
        FileAllowed(['jpg', 'png', 'gif', 'jpeg'], u'请上传jpg,jpeg,png,gif格式的图书封面.')
    ])
    translator = StringField(u'译者:')
    publisher = StringField(u'出版社:')
    isbn = StringField(u'ISBN:')
    book_file = FileField(u'文件', validators=[
        FileRequired(u'请选择您要上传的图书文件.'),
        FileAllowed(['mobi', 'epub', 'pdf', 'txt'], u'不支持的图书格式,请上传mobi,epub,pdf,txt格式的图书.')
    ])
    book_edition_commnet = TextAreaField(u'版本简介')
    tags = StringField(u'标签')

    def __init__(self, *args, **kwargs):
        super(UploadFormExt, self).__init__(*args, **kwargs)
