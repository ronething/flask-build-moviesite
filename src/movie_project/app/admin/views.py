# -*- coding:utf-8 _*-  
""" 
@author: ronething 
@file: views.py 
@time: 2018/10/21
@github: github.com/ronething 

Less is more.
"""

import os
import uuid
import datetime

from . import admin
from flask import render_template, url_for, redirect, flash, session, request
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm
from app.models import Admin, Tag, Movie, Preview
from functools import wraps
from app import db,app
from werkzeug.utils import secure_filename
from pypinyin import lazy_pinyin


# 登陆控制装饰器
def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("account") is None:
            return redirect(url_for("admin.login", next=request.url)) # 和 第 45 行 request.args.get("next") 联动
        return f(*args, **kwargs)

    return decorated_function


# 修改文件名称
def rename_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") \
               + str(uuid.uuid4().hex) \
               + fileinfo[-1]

    return filename


@admin.route("/")
@admin_login_req
def index():
    return render_template("admin/index.html")


@admin.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        account = Admin.query.filter_by(name=data["account"]).first()
        if not account.check_pwd(data["pwd"]):
            flash("密码错误！", "err")
            return redirect(url_for("admin.login"))
        session["account"] = data["account"]
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


@admin.route("/logout/")
@admin_login_req
def logout():
    session.pop("account", None)
    return redirect(url_for("admin.login"))


@admin.route("/pwd/")
@admin_login_req
def pwd():
    return render_template("admin/pwd.html")


# 添加标签
@admin.route("/tag/add/", methods=["GET", "POST"])
@admin_login_req
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag = Tag.query.filter_by(name=data["name"]).count()
        if tag == 1:
            flash("该标签已经存在", "err")
            return render_template("admin/tag_add.html", form=form)
        tag = Tag(
            name=data["name"]
        )
        db.session.add(tag)
        db.session.commit()
        flash("添加标签成功", "ok")
        return redirect(url_for("admin.tag_add"))
    return render_template("admin/tag_add.html", form=form)


# 标签列表
@admin.route("/tag/list/", methods=["GET"])
@admin.route("/tag/list/<int:page>/", methods=["GET"])
@admin_login_req
def tag_list(page=None):
    # 默认为第一页
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.addtime.asc()
    ).paginate(page=page, per_page=5)
    return render_template("admin/tag_list.html", page_data=page_data)


# 标签编辑
@admin.route("/tag/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def tag_edit(id=None):
    form = TagForm()
    tag = Tag.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data["name"]).count()
        # 例如有标签 1 2 现在把 2 改为 1 则要抛出异常 如果 2 不改还是 2 则可以更改成功
        if tag.name != data["name"] and tag_count == 1:
            flash("该标签已经存在", "err")
            return redirect(url_for("admin.tag_edit", id=id))
        tag.name = data["name"]
        db.session.add(tag)
        db.session.commit()
        flash("修改标签成功", "ok")
        return redirect(url_for("admin.tag_edit", id=id))
    return render_template("admin/tag_edit.html", form=form, tag=tag)


# 标签删除
@admin.route("/tag/del/<int:id>/", methods=["GET"])
@admin_login_req
def tag_del(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("删除标签成功", "ok")
    return redirect(url_for("admin.tag_list"))


# 电影添加
@admin.route("/movie/add/", methods=["GET", "POST"])
@admin_login_req
def movie_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        # 判断是否标题重复
        movie = Movie.query.filter_by(title=data["title"]).count()
        if movie == 1:
            flash("该电影已经存在", "err")
            return render_template("admin/movie_add.html", form=form)

        # 先用 pypinyin 将中文转为拼音 这样 secure_filename 就不会因为文件名是中文而过滤掉了
        # 参考 https://pdf-lib.org/Home/Details/6002
        # 保存封面和短片文件
        if not os.path.exists(app.config["UPLOAD_DIR"]):
            os.makedirs(app.config["UPLOAD_DIR"])
            os.chmod(app.config["UPLOAD_DIR"], "rw")

        file_url = secure_filename("".join(lazy_pinyin(form.url.data.filename)))
        url = rename_filename(file_url)
        form.url.data.save(app.config["UPLOAD_DIR"] + url)

        file_logo = secure_filename("".join(lazy_pinyin(form.logo.data.filename)))
        logo = rename_filename(file_logo)
        form.logo.data.save(app.config["UPLOAD_DIR"] + logo)

        movie = Movie(
            title=data["title"],
            url=url,
            info=data["info"],
            logo=logo,
            star=int(data["star"]),
            playnum=0,
            commentnum=0,
            tag_id=int(data["tag_id"]),
            area=data["area"],
            release_time=data["release_time"],
            length=data["length"],
        )
        db.session.add(movie)
        db.session.commit()
        flash("添加电影成功", "ok")
        return redirect(url_for("admin.movie_add"))
    return render_template("admin/movie_add.html", form=form)


# 电影列表
@admin.route("/movie/list/", methods=["GET"])
@admin.route("/movie/list/<int:page>/", methods=["GET"])
@admin_login_req
def movie_list(page=None):
    # 默认为第一页
    if page is None:
        page = 1
    page_data = Movie.query.join(Tag).filter(
      Movie.tag_id == Tag.id
    ).order_by(
        Movie.addtime.asc()
    ).paginate(page=page, per_page=5)
    return render_template("admin/movie_list.html", page_data=page_data)


# 电影删除
@admin.route("/movie/del/<int:id>/", methods=["GET"])
@admin_login_req
def movie_del(id=None):
    movie = Movie.query.filter_by(id=id).first_or_404()
    db.session.delete(movie)
    db.session.commit()
    flash("删除电影成功", "ok")
    return redirect(url_for("admin.movie_list"))


# 电影编辑
@admin.route("/movie/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def movie_edit(id=None):
    form = MovieForm()
    form.url.validators = []
    form.logo.validators = []
    movie = Movie.query.filter_by(id=id).first_or_404()

    if request.method == "GET":
        form.info.data = movie.info
        form.star.data = movie.star
        form.tag_id.data = movie.tag_id

    if form.validate_on_submit():
        data = form.data
        movie_count = Movie.query.filter_by(title=data["title"]).count()
        if movie.title != data["title"] and movie_count == 1:
            flash("该电影名已经存在", "err")
            return redirect(url_for("admin.movie_edit", id=id))

        # 先用 pypinyin 将中文转为拼音 这样 secure_filename 就不会因为文件名是中文而过滤掉了
        # 参考 https://pdf-lib.org/Home/Details/6002
        # 保存封面和短片文件
        if not os.path.exists(app.config["UPLOAD_DIR"]):
            os.makedirs(app.config["UPLOAD_DIR"])
            os.chmod(app.config["UPLOAD_DIR"], "rw")

        # 如果表单 url 数据不为空 说明上传了文件
        # 如果表单的 url 为空 则 form.url.data 为空 且为 str 类型
        if form.url.data:
            file_url = secure_filename("".join(lazy_pinyin(form.url.data.filename)))
            movie.url = rename_filename(file_url)
            form.url.data.save(app.config["UPLOAD_DIR"] + movie.url)

        # 如果表单 logo 数据不为空 说明上传了文件
        # 如果表单的 logo 为空 则 form.logo.data 为空 且为 str 类型
        if form.logo.data:
            file_logo = secure_filename("".join(lazy_pinyin(form.logo.data.filename)))
            movie.logo = rename_filename(file_logo)
            form.logo.data.save(app.config["UPLOAD_DIR"] + movie.logo)

        movie.title = data["title"]
        movie.info = data["info"]
        movie.star = data["star"]
        movie.tag_id = data["tag_id"]
        movie.area = data["area"]
        movie.length = data["length"]
        movie.release_time = data["release_time"]

        db.session.add(movie)
        db.session.commit()
        flash("修改电影成功", "ok")
        return redirect(url_for("admin.movie_edit", id=id))
    return render_template("admin/movie_edit.html", form=form, movie=movie)


# 上映预告添加
@admin.route("/preview/add/", methods=["GET", "POST"])
@admin_login_req
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        data = form.data
        preview = Preview.query.filter_by(title=data["title"]).count()
        if preview == 1:
            flash("该上映预告已经存在", "err")
            return render_template("admin/preview_add.html", form=form)

        if not os.path.exists(app.config["UPLOAD_DIR"]):
            os.makedirs(app.config["UPLOAD_DIR"])
            os.chmod(app.config["UPLOAD_DIR"], "rw")

        file_logo = secure_filename("".join(lazy_pinyin(form.logo.data.filename)))
        logo = rename_filename(file_logo)
        form.logo.data.save(app.config["UPLOAD_DIR"] + logo)

        preview = Preview(
            title=data["title"],
            logo=logo,
        )
        db.session.add(preview)
        db.session.commit()
        flash("添加上映预告成功", "ok")
        return redirect(url_for("admin.preview_add"))
    return render_template("admin/preview_add.html", form=form)


# 上映预告列表
@admin.route("/preview/list/", methods=["GET"])
@admin.route("/preview/list/<int:page>/", methods=["GET"])
@admin_login_req
def preview_list(page=None):
    if page is None:
        page = 1
    page_data = Preview.query.order_by(
        Preview.addtime.asc()
    ).paginate(page=page, per_page=5)
    return render_template("admin/preview_list.html", page_data=page_data)


# 上映预告删除
@admin.route("/preview/del/<int:id>/", methods=["GET"])
@admin_login_req
def preview_del(id=None):
    preview = Preview.query.filter_by(id=id).first_or_404()
    db.session.delete(preview)
    db.session.commit()
    flash("删除电影成功", "ok")
    return redirect(url_for("admin.preview_list"))


# 上映预告编辑
@admin.route("/preview/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def preview_edit(id=None):
    form = PreviewForm()
    form.logo.validators = []
    preview = Preview.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        data = form.data
        preview_count = Preview.query.filter_by(title=data["title"]).count()
        if preview.title != data["title"] and preview_count == 1:
            flash("该上映预告已经存在", "err")
            return redirect(url_for("admin.preview_edit", id=id))

        if not os.path.exists(app.config["UPLOAD_DIR"]):
            os.makedirs(app.config["UPLOAD_DIR"])
            os.chmod(app.config["UPLOAD_DIR"], "rw")

        # 如果表单 logo 数据不为空 说明上传了文件
        # 如果表单的 logo 为空 则 form.logo.data 为空 且为 str 类型
        if form.logo.data:
            file_logo = secure_filename("".join(lazy_pinyin(form.logo.data.filename)))
            preview.logo = rename_filename(file_logo)
            form.logo.data.save(app.config["UPLOAD_DIR"] + preview.logo)

        preview.title = data["title"]

        db.session.add(preview)
        db.session.commit()
        flash("修改上映预告成功", "ok")
        return redirect(url_for("admin.preview_edit", id=id))
    return render_template("admin/preview_edit.html", form=form, preview=preview)


@admin.route("/user/list/")
@admin_login_req
def user_list():
    return render_template("admin/user_list.html")


@admin.route("/user/view/")
@admin_login_req
def user_view():
    return render_template("admin/user_view.html")


@admin.route("/comment/list/")
@admin_login_req
def comment_list():
    return render_template("admin/comment_list.html")


@admin.route("/moviecol/list/")
@admin_login_req
def moviecol_list():
    return render_template("admin/moviecol_list.html")


@admin.route("/oplog/list/")
@admin_login_req
def oplog_list():
    return render_template("admin/oplog_list.html")


@admin.route("/adminloginlog/list/")
@admin_login_req
def adminloginlog_list():
    return render_template("admin/adminloginlog_list.html")


@admin.route("/userloginlog/list/")
@admin_login_req
def userloginlog_list():
    return render_template("admin/userloginlog_list.html")


@admin.route("/auth/add")
@admin_login_req
def auth_add():
    return render_template("admin/auth_add.html")


@admin.route("/auth/list/")
@admin_login_req
def auth_list():
    return render_template("admin/auth_list.html")


@admin.route("/role/add")
@admin_login_req
def role_add():
    return render_template("admin/role_add.html")


@admin.route("/role/list/")
@admin_login_req
def role_list():
    return render_template("admin/role_list.html")


@admin.route("/admin/add")
@admin_login_req
def admin_add():
    return render_template("admin/admin_add.html")


@admin.route("/admin/list/")
@admin_login_req
def admin_list():
    return render_template("admin/admin_list.html")
