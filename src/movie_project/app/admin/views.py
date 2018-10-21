# -*- coding:utf-8 _*-  
""" 
@author: ronething 
@file: views.py 
@time: 2018/10/21
@github: github.com/ronething 

Less is more.
"""

from . import admin
from flask import render_template, url_for, redirect


@admin.route("/")
def index():
    return render_template("admin/index.html")


@admin.route("/login/")
def login():
    return render_template("admin/login.html")


@admin.route("/logout/")
def logout():
    return redirect(url_for("admin.login"))