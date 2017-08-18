# -*- coding:utf-8 -*-
from flask_script import Manager, Server, Shell

from bookstore.extensions import db
from bookstore.models.book import Book, BookEdition, BookEditionComment, Tag
from bookstore.models.user import User, Role
from bookstore.startup import create_app

app = create_app('default')

manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Book=Book, BookEdition=BookEdition,
                BookEditionComment=BookEditionComment, Tag=Tag)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command("runserver", Server('localhost', port=5000))

if __name__ == "__main__":
    manager.run()
