# -*- coding:utf-8 _*-  
""" 
@author: ronething 
@file: views.py 
@time: 2018/10/21
@github: github.com/ronething 

Less is more.
"""

import uuid
import os
import datetime

from . import home
from flask import render_template, redirect, url_for, flash, session, request
from app.home.forms import RegisterForm, LoginForm, UserDetailForm, PwdForm
from app.models import User, Userlog, Preview, Tag, Movie
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from pypinyin import lazy_pinyin
from app import db, app
from functools import wraps


# 登陆控制装饰器
def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_name") is None:
            return redirect(url_for("home.login", next=request.url))  # 和 第 410 行 request.args.get("next") 联动
        return f(*args, **kwargs)

    return decorated_function


# 修改文件名称
def rename_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") \
               + uuid.uuid4().hex \
               + fileinfo[-1]

    return filename


# 前台首页
@home.route("/", methods=["GET"])
@home.route("/<int:page>/", methods=["GET"])
def index(page=None):
    tags = Tag.query.all()
    star_list = ["一", "二", "三", "四", "五"]
    page_data = Movie.query

    tag_id = request.args.get("tid", 0)
    if int(tag_id) != 0:
        page_data = page_data.filter_by(tag_id=int(tag_id))
    star = request.args.get("star", 0)
    if int(star) != 0:
        page_data = page_data.filter_by(star=int(star))
    time = request.args.get("time", 0)
    if int(time) == 0:
        page_data = page_data.order_by(
            Movie.addtime.desc()
        )
    else:
        page_data = page_data.order_by(
            Movie.addtime.asc()
        )
    pm = request.args.get("pm", 0)
    if int(pm) == 0:
        page_data = page_data.order_by(
            Movie.playnum.desc()
        )
    else:
        page_data = page_data.order_by(
            Movie.playnum.asc()
        )
    cm = request.args.get("cm", 0)
    if int(cm) == 0:
        page_data = page_data.order_by(
            Movie.commentnum.desc()
        )
    else:
        page_data = page_data.order_by(
            Movie.commentnum.asc()
        )

    param = dict(
        tid=tag_id,
        star=star,
        time=time,
        pm=pm,
        cm=cm,
    )

    if page is None:
        page = 1
    page_data = page_data.paginate(page=page, per_page=10)

    return render_template("home/index.html", tags=tags, param=param, star_list=star_list, page_data=page_data)


# 会员登陆
@home.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data["name"]).first()
        if not user.check_pwd(data["pwd"]):
            flash("密码错误！", "err")
            return redirect(url_for("home.login"))
        session["user_name"] = data["name"]
        session["user_id"] = user.id
        userlog = Userlog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        return redirect(request.args.get("next") or url_for("home.user"))
    return render_template("home/login.html", form=form)


# 会员注销
@home.route("/logout/")
def logout():
    session.pop("user_name", None)
    session.pop("user_id", None)
    flash("注销成功", "ok")
    return redirect(url_for("home.login"))


# 会员注册
# TODO 需要把 "这个人很懒，什么都没有留下" 这些类似的字符串 放在一个单独的文件里面当常量咯
@home.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            pwd=generate_password_hash(data["pwd"]),
            info="这个人很懒，什么都没有留下",
            face="face.jpg",
            uuid=uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()
        flash("注册成功", "ok")
        return redirect(url_for("home.register"))
    return render_template("home/register.html", form=form)


# 会员中心
@home.route("/user/", methods=["GET", "POST"])
@user_login_req
def user():
    form = UserDetailForm()
    form.logo.validators = []
    user = User.query.filter_by(id=session["user_id"]).first()
    if request.method == "GET":
        form.info.data = user.info
    if form.validate_on_submit():
        data = form.data
        if not os.path.exists(app.config["LOGO_DIR"]):
            os.makedirs(app.config["LOGO_DIR"])
            os.chmod(app.config["LOGO_DIR"], "rw")
        if form.logo.data:
            file_logo = secure_filename("".join(lazy_pinyin(form.logo.data.filename)))
            user.face = rename_filename(file_logo)
            form.logo.data.save(app.config["LOGO_DIR"] + user.face)
        user.info = data["info"]
        db.session.add(user)
        db.session.commit()
        flash("修改资料成功", "ok")
        return redirect(url_for("home.user"))
    return render_template("home/user.html", form=form, user=user)


# 修改密码
@home.route("/pwd/", methods=["GET", "POST"])
@user_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        user.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(user)
        db.session.commit()
        flash("修改密码成功，请重新登陆！", "ok")
        return redirect(url_for("home.logout"))
    return render_template("home/pwd.html", form=form)


# 评论记录
@home.route("/comments/")
@user_login_req
def comments():
    return render_template("home/comments.html")


# 登陆日志
@home.route("/loginlog/", methods=["GET"])
@home.route("/loginlog/<int:page>/", methods=["GET"])
@user_login_req
def loginlog(page=None):
    if page is None:
        page = 1
    page_data = Userlog.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/loginlog.html", page_data=page_data)


# 电影收藏
@home.route("/moviecol/")
@user_login_req
def moviecol():
    return render_template("home/moviecol.html")


# 上映预告轮播
@home.route("/animation/")
def animation():
    data = Preview.query.order_by(
        Preview.addtime.desc()
    ).paginate(page=1, per_page=5)
    return render_template("home/animation.html", data=data)


# 搜索
@home.route("/search/")
def search():
    return render_template("home/search.html")


# 电影详情
@home.route("/play/")
def play():
    return render_template("home/play.html")