import re, string
from flask import render_template, abort, request, current_app, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from . import main

from tools.decorators import admin_required

@main.route('/', methods=['GET'])
def index():
    return render_template(
        'base.html',
    )