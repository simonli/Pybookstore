# -*- coding:utf-8 -*-
from flask import current_app, Blueprint, request, render_template, flash
from flask_login import login_required

from bookstore.extensions import db
from bookstore.models.book import Book

mod = Blueprint('book', __name__)


@mod.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    page = request.args.get('page', 1, type=int)
    keyword = request.form.get('keyword', '')
    query_str = '%' + keyword + '%'
    rule = db.or_(Book.name.like(query_str), Book.author.like(query_str),
                  Book.isbn.like(query_str), Book.publisher.like(query_str))
    pagination = Book.query.filter(rule).order_by(Book.douban_rating_score.desc(), Book.douban_rating_people.desc()) \
        .paginate(page, per_page=current_app.config.get('ITEMS_PER_PAGE'), error_out=False)
    books = pagination.items
    return render_template('book/search.html', books=books, keyword=keyword, pagination=pagination,
                           endpoint='.search')


@mod.route('/detail/<int:id>/')
@login_required
def detail(id):
    book = Book.query.get(id)
    related_books = set()
    if book:
        for tag in book.tags:
            for book_obj in tag.books:
                if not book_obj is book:
                    related_books.add(book_obj)
    else:
        flash(u'书籍不存在.')
    return render_template('book/detail.html', book=book, related_books=list(related_books))


@mod.route('/edition/<int:id>')
@login_required
def edition(id):
    pass
