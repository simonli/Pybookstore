# -*- coding:utf-8 -*-
from flask import current_app, Blueprint, request, render_template, redirect, url_for, flash, jsonify
from datetime import datetime
from flask_login import current_user
from flask_login import login_required

mod = Blueprint('book', __name__)