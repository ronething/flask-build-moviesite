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
import json

from . import home
from flask import render_template, redirect, url_for, flash, session, request, Response
from app.home.forms import RegisterForm, LoginForm, UserDetailForm, PwdForm, CommentForm
from app.models import User, Userlog, Preview, Tag, Movie, Comment, Moviecol
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from pypinyin import lazy_pinyin
from app import db, app, rd
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
    page_data = page_data.paginate(page=page, per_page=12)

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
            return redirect(url_for("home.login", next=request.args.get("next", "")))
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
        flash("注册成功，请登录！", "ok")
        return redirect(url_for("home.login"))
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
@home.route("/comments/", methods=["GET"])
@home.route("/comments/<int:page>/", methods=["GET"])
@user_login_req
def comments(page=None):
    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == session["user_id"]
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=5)
    return render_template("home/comments.html", page_data=page_data)


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


# 电影收藏添加 ajax 返回 json
@home.route("/moviecol/add/", methods=["GET"])
@user_login_req
def moviecol_add():
    mid = request.args.get("mid", "")
    moviecol_count = Moviecol.query.filter_by(
        user_id=session["user_id"],
        movie_id=int(mid),
    ).count()
    if moviecol_count == 1:
        data = dict(
            ok=0,
            message="不可重复收藏"
        )

        return json.dumps(data)

    if moviecol_count == 0:
        movie_col = Moviecol(
            user_id=session["user_id"],
            movie_id=int(mid)
        )
        db.session.add(movie_col)
        db.session.commit()
        data = dict(
            ok=1,
            message="收藏电影成功"
        )

    return json.dumps(data)


# 电影收藏
@home.route("/moviecol/", methods=["GET"])
@home.route("/moviecol/<int:page>/", methods=["GET"])
@user_login_req
def moviecol(page=None):
    if page is None:
        page = 1
    page_data = Moviecol.query.join(
        Movie
    ).filter(
        Movie.id == Moviecol.movie_id,
        Moviecol.user_id == session["user_id"],
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=5)
    return render_template("home/moviecol.html", page_data=page_data)


# 上映预告轮播
@home.route("/animation/")
def animation():
    data = Preview.query.order_by(
        Preview.addtime.desc()
    ).paginate(page=1, per_page=5)
    return render_template("home/animation_bootstrap.html", data=data)


# 搜索
@home.route("/search/", methods=["GET"])
@home.route("/search/<int:page>/", methods=["GET"])
def search(page=None):
    key = request.args.get("s", "")
    if not key:
        return redirect(url_for("home.index"))
    if page is None:
        page = 1
    count = Movie.query.filter(
        # ilike 和 like 类似 不过 ilike 忽略大小写
        Movie.title.ilike('%' + key + '%')
    ).count()
    page_data = Movie.query.filter(
        Movie.title.ilike('%' + key + '%')
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=5)
    return render_template("home/search.html", page_data=page_data, key=key, count=count)


# 电影详情
@home.route("/play/<int:id>/", methods=["GET", "POST"])
@home.route("/play/<int:id>/<int:page>/", methods=["GET", "POST"])
def play(id=None, page=None):
    movie = Movie.query.join(
        Tag
    ).filter(
        Movie.id == id,
        Movie.tag_id == Tag.id
    ).first_or_404()
    form = CommentForm()

    # 评论列表
    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == movie.id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.asc()
    ).paginate(page=page, per_page=10)

    # comment_count = Comment.query.join(
    #     Movie
    # ).join(
    #     User
    # ).filter(
    #     Movie.id == movie.id,
    #     User.id == Comment.user_id
    # ).count()

    movie.playnum = movie.playnum + 1
    if "user_id" in session and form.validate_on_submit():
        data = form.data
        # TODO content 插入的时候需要过滤一些特殊字符 防止注入攻击之类的
        comment = Comment(
            content=data["content"],
            movie_id=movie.id,
            user_id=session["user_id"]
        )
        db.session.add(comment)
        movie.commentnum = movie.commentnum + 1
        db.session.add(movie)
        db.session.commit()
        flash("评论成功", "ok")
        return redirect(url_for("home.play", id=movie.id))
    db.session.add(movie)
    db.session.commit()
    return render_template("home/play.html", movie=movie, form=form, page_data=page_data)


# 电影详情 使用 dplayer 弹幕播放器
@home.route("/video/<int:id>/", methods=["GET", "POST"])
@home.route("/video/<int:id>/<int:page>/", methods=["GET", "POST"])
def video(id=None, page=None):
    movie = Movie.query.join(
        Tag
    ).filter(
        Movie.id == id,
        Movie.tag_id == Tag.id
    ).first_or_404()
    form = CommentForm()

    # 评论列表
    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == movie.id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.asc()
    ).paginate(page=page, per_page=10)

    movie.playnum = movie.playnum + 1
    if "user_id" in session and form.validate_on_submit():
        data = form.data
        # TODO content 插入的时候需要过滤一些特殊字符 防止注入攻击之类的
        comment = Comment(
            content=data["content"],
            movie_id=movie.id,
            user_id=session["user_id"]
        )
        db.session.add(comment)
        movie.commentnum = movie.commentnum + 1
        db.session.add(movie)
        db.session.commit()
        flash("评论成功", "ok")
        return redirect(url_for("home.video", id=movie.id))
    db.session.add(movie)
    db.session.commit()
    return render_template("home/video.html", movie=movie, form=form, page_data=page_data)


# 发送弹幕
@home.route("/danmu/v3/", methods=["GET", "POST"])
def danmu():
    if request.method == "GET":
        id = request.args.get("id")
        key = "movie" + str(id)
        """
        弹幕格式
        {
            "code": 0,
            "data": [
                [
                time,
                type,
                color,
                author,
                text
                ]
            ]
        }
        """

        if rd.llen(key):
            msgs = rd.lrange(key, 0, 2999)
            res = {
                "code": 0,
                "data": [[json.loads(i)["time"], json.loads(i)["type"],
                          json.loads(i)["color"], json.loads(i)["author"],
                          json.loads(i)["text"]] for i
                         in msgs]
            }
        else:
            res = {
                "code": 0,
                "data": []
            }

        res_json = json.dumps(res)

    if request.method == "POST":
        data = json.loads(request.get_data())
        msg = {
            "id": data["id"],
            "author": data["author"],
            "time": data["time"],
            "text": data["text"],
            "color": data["color"],
            "type": data["type"]
        }
        res = {
            "code": 1,
            "data": msg
        }

        res_json = json.dumps(res)

        rd.lpush("movie" + str(data["id"]), json.dumps(msg))

    return Response(res_json, mimetype="application/json")
