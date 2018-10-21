# -*- coding:utf-8 _*-  
""" 
@author: ronething 
@file: __init__.py.py 
@time: 2018/10/21
@github: github.com/ronething 

Less is more.
"""

from flask import Flask, render_template

app = Flask(__name__)

app.debug = True

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")

# 404 页面
@app.errorhandler(404)
def page_not_found(error):
    return render_template("common/404.html"), 404