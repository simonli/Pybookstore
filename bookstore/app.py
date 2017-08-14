# -*- coding:utf-8 -*-
from flask import Flask, request, redirect, jsonify, flash, url_for, render_template

from bookstore.account import account
from bookstore.extensions import db, login_manager, bcrypt
from bookstore.frontend import frontend
from config import configs

DEFAULT_APP_NAME = 'bookstore'
DEFAULT_BLUEPRINTS = (
    (frontend, ''),
    (account, '/account')
)


def create_app(config_name=None, blueprints=None):
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(DEFAULT_APP_NAME)
    app.config.from_object(configs[config_name])

    configure_extensions(app)
    configure_errorhandlers(app)
    # configure_before_handlers(app)
    configure_blueprints(app, blueprints)

    return app


def configure_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)


def configure_before_handlers(app):
    @app.before_request
    def f():
        pass


def configure_errorhandlers(app):
    @app.errorhandler(401)
    def unauthorized(error):
        if request.is_xhr:
            return jsonify(error="Login required")
        flash("Please login to see this page")
        return redirect(url_for("account.login", next=request.path))

    @app.errorhandler(403)
    def forbidden(error):
        if request.is_xhr:
            return jsonify(error='Sorry, page not allowed')
        return render_template("errors/403.html", error=error)

    @app.errorhandler(404)
    def page_not_found(error):
        if request.is_xhr:
            return jsonify(error='Sorry, page not found')
        return render_template("errors/404.html", error=error)

    @app.errorhandler(500)
    def server_error(error):
        if request.is_xhr:
            return jsonify(error='Sorry, an error has occurred')
        return render_template("errors/500.html", error=error)


def configure_blueprints(app, blueprints):
    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
