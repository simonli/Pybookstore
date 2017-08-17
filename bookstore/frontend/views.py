# -*- coding:utf-8 -*-
import os

from flask import current_app, Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import current_user
from flask_login import login_required

from bookstore.extensions import db
from bookstore.helper import utils, douban
from bookstore.models.book import Book, BookEdition, BookEditionComment, Tag
from .forms import UploadForm, UploadFormExt

mod = Blueprint('frontend', __name__)


@mod.route('/')
@mod.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Book.query.order_by(Book.douban_rating_score.desc(), Book.douban_rating_people.desc()) \
        .paginate(page, per_page=current_app.config.get('ITEMS_PER_PAGE'), error_out=False)
    books = pagination.items
    return render_template('frontend/index.html', books=books, pagination=pagination, endpoint='.index')


@mod.route('/upload/', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        douban_url = form.douban_url.data
        douban_id = douban_url[douban_url.find('subject') + 8:douban_url.rfind('/')]
        b = Book.query.filter_by(douban_id=douban_id).first()
        if b:
            form.book_file.errors.append(u'该书已经存在:%s' % url_for('book.detail', id=b.id))
            return render_template('frontend/upload.html', form=form)
        # 上传文件
        if 'book_file' in request.files:
            upfile = form.book_file.data
            file_ext = utils.get_file_ext(upfile.filename)
            upload_folder = current_app.config.get('UPLOAD_BOOK_FOLDER')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            dest_filename = utils.unique_id() + '.' + file_ext
            dest_filepath = os.path.join(upload_folder, dest_filename)
            upfile.seek(0)
            size = len(upfile.read())
            upfile.seek(0)
            upfile.save(dest_filepath)  # 保存文件
            file_checksum = utils.get_checksum(dest_filepath)
            be_obj = BookEdition.query.filter_by(checksum=file_checksum).first()
            if be_obj:
                os.remove(dest_filepath)
                form.book_file.errors.append(u'图书已经存在,<a href="%s">' % url_for('book.edition', id=be_obj.id))
                return render_template('frontend/upload.html', form=form)
            # Book Object
            book = Book()
            book.douban_id = request.form['douban_id']
            book.douban_url = form.douban_url.data
            book.name = dest_filename
            tag_list = ''
            if book.douban_url is not None:  # 如果douban_url存在，则从豆瓣抓取相关信息
                book_info = douban.get_book_info(book.douban_url)
                book.title = book_info.get('title')
                book.author = book_info.get('author')
                book.author_intro = book_info.get('author_intro')
                book.book_intro = book_info.get('book_intro')
                book.catalog = book_info.get('catalog')
                book.isbn = book_info.get('isbn')
                book.publisher = book_info.get('publisher')
                book.translator = book_info.get('translator')
                book.douban_rating_score = book_info['rating_score']
                book.douban_rating_people = book_info['rating_people']
                book.douban_id = book_info['subject_id']
                book.logo = book_info['logo']
                tag_list = book_info['tags']

            # Tags
            db_tag_obj_list = Tag.query.filter(Tag.name.in_(tag_list)).all()
            db_tag_list = [x.name for x in db_tag_obj_list]
            # insert new tag and bind to book
            for book_tag in tag_list:
                if book_tag not in db_tag_list:
                    book.tags.append(Tag(name=book_tag))
            # bind exist tag
            for book_tag_obj in db_tag_obj_list:
                book.tags.append(book_tag_obj)

            # BookFile Object
            be = BookEdition()
            be.filename = dest_filename
            be.original_filename = upfile.filename
            be.size = size
            be.book = book
            be.user_id = current_user.id
            be.checksum = utils.get_checksum(dest_filepath)

            # BookEditionComment Object
            bec = BookEditionComment()
            bec.book_edition = be
            bec.comment = form.book_edition_commnet.data
            bec.user_id = current_user.id

            db.session.add(book)
            db.session.add(be)
            db.session.add(bec)
            db.session.commit()
        flash(u'图书上传成功.')
        return redirect(url_for('frontend.index'))
    return render_template('frontend/upload.html', form=form)


@mod.route('/upload/ext/', methods=['GET', 'POST'])
def upload_ext():
    form = UploadFormExt()
    if form.validate_on_submit():
        douban_url = form.douban_url.data
        douban_id = douban_url[douban_url.find('subject') + 8:douban_url.rfind('/')]
        b = Book.query.filter_by(douban_id=douban_id).first()
        if b:
            form.book_file.errors.append(u'该书已经存在.%s' % url_for('.book,id=' + b.id))
            return render_template('frontend/upload_ext.html', form=form)

        # 上传文件
        if 'book_file' in request.files:
            upfile = form.book_file.data
            print 'W' * 100
            file_ext = utils.get_file_ext(upfile.filename)
            upload_folder = current_app.config.get('UPLOAD_BOOK_FOLDER')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            dest_filename = utils.unique_id() + '.' + file_ext
            dest_filepath = os.path.join(upload_folder, dest_filename)
            upfile.seek(0)
            size = len(upfile.read())

            upfile.seek(0)
            upfile.save(dest_filepath)  # 保存文件
            file_checksum = utils.get_checksum(dest_filepath)
            be_obj = BookEdition.query.filter_by(checksum=file_checksum).first()
            if be_obj:
                form.book_file.errors.append(u'图书已经存在,<a href="%s">' % url_for('.book_editon,id=' % be_obj.id))
                os.remove(dest_filepath)
                return render_template('frontend/upload_ext.html', form=form)

            if 'logo' in request.files:
                logofile = form.logo.data
                logofile_ext = utils.get_file_ext(logofile.filename)
                upload_logo_folder = current_app.config.get('UPLOAD_LOGO_FOLDER')
                if not os.path.exists(upload_logo_folder):
                    os.makedirs(upload_logo_folder)
                dest_logo_filename = utils.get_namebasetime() + '.' + logofile_ext
                dest_logo_filepath = os.path.join(upload_logo_folder, dest_logo_filename)

                logofile.seek(0)
                logofile.save(dest_logo_filepath)  # 保存文件

            # Book Object
            book = Book()
            book.name = upfile.filename
            book.author = form.author.data
            book.translator = form.translator.data
            book.book_intro = form.book_intro.data
            book.isbn = form.isbn.data
            book.publisher = form.publisher.data
            book.logo = dest_logo_filename
            book.is_from = 'diy'

            # 处理标签
            tags = form.tags.data
            tags_temp = tags.replace(u'，', ',')
            tag_list = tags_temp.split(',')

            db_tag_obj_list = Tag.query.filter(Tag.name.in_(tag_list)).all()
            db_tag_list = [x.name for x in db_tag_obj_list]
            # insert new tag and bind to book
            for book_tag in tag_list:
                if book_tag not in db_tag_list:
                    book.tags.append(Tag(name=book_tag))
            # bind exist tag
            for book_tag_obj in db_tag_obj_list:
                book.tags.append(book_tag_obj)

            # BookFile Object
            be = BookEdition()
            be.filename = dest_filename
            be.original_filename = upfile.filename
            be.size = size
            be.book = book
            be.user_id = current_user.id
            be.md5sum = utils.get_checksum(dest_filepath)

            # BookEditionComment Object
            bec = BookEditionComment()
            bec.book_edition = be
            bec.comment = form.book_edition_commnet.data
            bec.user_id = current_user.id

            db.session.add(book)
            db.session.add(be)
            db.session.add(bec)
            db.session.commit()
        flash(u'图书上传成功.')
        return redirect(url_for('frontend.index'))
    return render_template('frontend/upload_ext.html', form=form)


@mod.route('/search/douban/')
@login_required
def search_douban():
    q = request.args.get('q', '')
    if q is None or q == '':
        return jsonify([])
    return jsonify(douban.get_search_book_list(q))
