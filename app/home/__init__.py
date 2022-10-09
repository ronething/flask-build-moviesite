# -*- coding:utf-8 _*-  
""" 
@author: ronething 
@file: __init__.py.py 
@time: 2018/10/21
@github: github.com/ronething 

Less is more.
"""

from flask import Blueprint


home = Blueprint("home", __name__)

# views 不能放在 home blueprint 前面 否则会报错
import app.home.views

