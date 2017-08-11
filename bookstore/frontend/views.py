# -*- coding:utf-8 -*-
from flask import current_app, Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import current_user
from bookstore.extensions import db
from bookstore.utils import get_book_info, get_md5sum, unique_id, get_extension,get_namebasetime
from flask_login import login_required
from .forms import UploadForm, UploadFormExt
from bookstore.models.book import Book, BookEdition, BookEditionComment, Category, Tag
from bs4 import BeautifulSoup
import requests
import os
import StringIO

mod = Blueprint('frontend', __name__)


@mod.route('/')
@mod.route('/index')
def index():
    return render_template('frontend/index.html')


@mod.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    errors = []
    if form.validate_on_submit():
        # 上传文件
        if 'book_file' in request.files:
            upfile = form.book_file.data
            print 'W' * 100
            file_ext = get_extension(upfile.filename)
            upload_folder = current_app.config.get('UPLOAD_BOOK_FOLDER')
            dest_filename = unique_id() + '.' + file_ext
            dest_filepath = os.path.join(upload_folder + os.sep, unique_id() + '.' + get_extension(upfile.filename))
            upfile.seek(0)
            data = upfile.read()
            size = len(data)
            if file_ext not in current_app.config.get('ALLOWED_EXTENSIONS'):
                errors.append(u'不支持的图书格式,请上传mobi,epub,pdf,txt格式的图书.')
            if size > current_app.config.get('ALLOWED_BOOK_SIZE'):
                errors.append(u'图书大小不能超过50MB.')
            if errors:
                return render_template('frontend/upload.html', form=form, errors=errors)

            upfile.seek(0)
            upfile.save(dest_filepath) #保存文件
            file_md5sum = get_md5sum(dest_filepath)
            be_obj = BookEdition.query.filter_by(md5sum=file_md5sum).first()
            if be_obj:
                errors.append(u'图书已经存在,<a href="%s">' % be_obj.id)
                return render_template('frontend/upload.html', form=form, errors=errors)
            # Book Object
            book = Book()
            book.id = unique_id()
            book.douban_id = request.form['douban_id']
            book.douban_url = form.douban_url.data
            book.name = dest_filename
            if book.douban_url is not None:  # 如果douban_url存在，则从豆瓣抓取相关信息
                book_info = get_book_info(book.douban_url)
                book.name = book_info.get('name')
                book.author = book_info.get('author')
                book.author_intro = book_info.get('author_intro')
                book.book_intro = book_info.get('book_intro')
                book.book_catalog = book_info.get('book_catalog')
                book.isbn = book_info.get('isbn')
                book.publisher = book_info.get('publisher')
                book.translator = book_info.get('translator')
                book.douban_rating_score = book_info['rating_score']
                book.douban_rating_people = book_info['rating_people']
                book.douban_id = book_info['subject_id']

            # BookFile Object
            be = BookEdition()
            be.id = unique_id()
            be.filename = dest_filename
            be.original_filename = upfile.filename
            be.book = book
            be.user_id = current_user.id
            be.md5sum = get_md5sum(dest_filepath)

            # BookEditionComment Object
            bec = BookEditionComment()
            bec.id = unique_id()
            bec.book_edition = be
            bec.comment = form.book_edition_commnet.data
            bec.user_id = current_user.id

            db.session.add(book)
            db.session.add(be)
            db.session.add(bec)
            db.session.commit()

        return redirect(url_for('frontend.index'))
    return render_template('frontend/upload.html', form=form,errors=errors)

@mod.route('/upload_ext',methods=['GET','POST'])
def upload_ext():
    form = UploadFormExt()
    errors = []
    if form.validate_on_submit():
        # 上传文件
        if 'book_file' in request.files:
            upfile = form.book_file.data
            print 'W' * 100
            file_ext = get_extension(upfile.filename)
            upload_folder = current_app.config.get('UPLOAD_BOOK_FOLDER')
            dest_filename = unique_id() + '.' + file_ext
            dest_filepath = os.path.join(upload_folder + os.sep, unique_id() + '.' + get_extension(upfile.filename))
            upfile.seek(0)
            data = upfile.read()
            size = len(data)
            if file_ext not in current_app.config.get('ALLOWED_EXTENSIONS'):
                errors.append(u'不支持的图书格式,请上传mobi,epub,pdf,txt格式的图书.')
            if size > current_app.config.get('ALLOWED_BOOK_SIZE'):
                errors.append(u'图书大小不能超过50MB.')
            if errors:
                return render_template('frontend/upload_ext.html', form=form, errors=errors)

            upfile.seek(0)
            upfile.save(dest_filepath) #保存文件
            file_md5sum = get_md5sum(dest_filepath)
            be_obj = BookEdition.query.filter_by(md5sum=file_md5sum).first()
            if be_obj:
                errors.append(u'图书已经存在,<a href="%s">' % be_obj.id)
                return render_template('frontend/upload_ext.html', form=form, errors=errors)

            if'cover' in request.files:
                upcover = form.cover.data
                cover_ext = get_extension(upcover.filename)
                upload_folder = current_app.config.get('UPLOAD_BOOK_FOLDER')
                dest_filename = unique_id() + '.' + file_ext
                dest_filepath = os.path.join(upload_folder + os.sep, unique_id() + '.' + get_extension(upfile.filename))
                upfile.seek(0)
                data = upfile.read()
                size = len(data)
                if file_ext not in current_app.config.get('ALLOWED_EXTENSIONS'):
                    errors.append(u'不支持的图书格式,请上传mobi,epub,pdf,txt格式的图书.')
                if size > current_app.config.get('ALLOWED_BOOK_SIZE'):
                    errors.append(u'图书大小不能超过50MB.')
                if errors:
                    return render_template('frontend/upload.html', form=form, errors=errors)

                upfile.seek(0)
                upfile.save(dest_filepath)  # 保存文件


            # Book Object
            book = Book()
            book.id = unique_id()
            book.douban_id = request.form['douban_id']
            book.douban_url = form.douban_url.data
            book.name = dest_filename
            if book.douban_url is not None:  # 如果douban_url存在，则从豆瓣抓取相关信息
                book_info = get_book_info(book.douban_url)
                book.name = book_info.get('name')
                book.author = book_info.get('author')
                book.author_intro = book_info.get('author_intro')
                book.book_intro = book_info.get('book_intro')
                book.book_catalog = book_info.get('book_catalog')
                book.isbn = book_info.get('isbn')
                book.publisher = book_info.get('publisher')
                book.translator = book_info.get('translator')
                book.douban_rating_score = book_info['rating_score']
                book.douban_rating_people = book_info['rating_people']
                book.douban_id = book_info['subject_id']

            # BookFile Object
            be = BookEdition()
            be.id = unique_id()
            be.filename = dest_filename
            be.original_filename = upfile.filename
            be.book = book
            be.user_id = current_user.id
            be.md5sum = get_md5sum(dest_filepath)

            # BookEditionComment Object
            bec = BookEditionComment()
            bec.id = unique_id()
            bec.book_edition = be
            bec.comment = form.book_edition_commnet.data
            bec.user_id = current_user.id

            db.session.add(book)
            db.session.add(be)
            db.session.add(bec)
            db.session.commit()

        return redirect(url_for('frontend.index'))
    return render_template('frontend/upload.html', form=form,errors=errors)


@mod.route('/search/douban/')
@login_required
def search_douban():
    q = request.args.get('q', '')
    book_list = []
    if q is None or q == '':
        return jsonify(book_list)

    douban_url = "https://book.douban.com/subject_search?search_text=" + q
    r = requests.get(douban_url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'lxml')
        item_list = soup.find_all(class_='subject-item')
        print item_list
        for item in item_list:
            book = {}
            book['pic'] = item.img.attrs.get('src')
            onclick_attr = item.a.attrs.get("onclick")
            subject_id = onclick_attr[onclick_attr.find("subject_id:") + 12:onclick_attr.find(",from") - 1]
            book['subject_id'] = subject_id
            book_url = item.h2.a.attrs.get('href')
            if book_url.find('book.douban.com/subject/') == -1:
                break
            book['url'] = book_url
            book_name = ''
            name_list = item.h2.a.contents
            for x in name_list:
                book_name = book_name + repr(x).strip()
            book['name'] = item.h2.a.get_text().strip().replace(' ', '').replace("\n", "")
            book['pub'] = item.find(class_='pub').get_text().strip()
            if item.find(class_='rating_nums') is not None:
                book['rating_nums'] = item.find(class_='rating_nums').get_text().strip() + u'分'
            else:
                book['rating_nums'] = ''
            if item.find(class_='pl') is not None:
                book['rating_peoples'] = item.find(class_='pl').get_text().strip()
            else:
                book['rating_peoples'] = ''
            book_list.append(book)
    return jsonify(book_list)
