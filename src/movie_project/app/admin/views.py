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
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, PwdForm, AuthForm, RoleForm
from app.models import Admin, Tag, Movie, Preview, User, Comment, Moviecol, Oplog, Adminlog, Userlog, Auth, Role
from functools import wraps
from app import db, app
from werkzeug.utils import secure_filename
from pypinyin import lazy_pinyin
from werkzeug.security import generate_password_hash


# 上下文应用处理器
@admin.context_processor
def tpl_extra():
    data = dict(
        online_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    return data


# 登陆控制装饰器
def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("account") is None:
            return redirect(url_for("admin.login", next=request.url))  # 和 第 410 行 request.args.get("next") 联动
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
            oplog = Oplog(
                admin_id=account.id,
                ip=request.remote_addr,
                reason="登陆管理员账户 {0} 失败".format(account.name)
            )
            db.session.add(oplog)
            db.session.commit()
            flash("密码错误！", "err")
            return redirect(url_for("admin.login"))
        session["account"] = data["account"]
        session["admin_id"] = account.id
        adminlog = Adminlog(
            admin_id=account.id,
            ip=request.remote_addr
        )
        oplog = Oplog(
            admin_id=account.id,
            ip=request.remote_addr,
            reason="登陆管理员账户 {0} 成功".format(account.name)
        )
        db.session.add(adminlog)
        db.session.add(oplog)
        db.session.commit()
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


@admin.route("/logout/")
@admin_login_req
def logout():
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="注销管理员账户 {0} ".format(session["account"])
    )
    db.session.add(oplog)
    db.session.commit()
    session.pop("account", None)
    session.pop("admin_id", None)
    flash("注销成功", "ok")
    return redirect(url_for("admin.login"))


# 管理员修改密码
@admin.route("/pwd/", methods=["GET", "POST"])
@admin_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        if data["new_pwd"] != data["check_pwd"]:
            flash("两次密码输入不一致！", "err")
            return render_template("admin/pwd.html", form=form)
        name = session["account"]
        account = Admin.query.filter_by(name=name).first()
        account.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(account)
        db.session.commit()
        flash("修改密码成功，请重新登陆！", "ok")
        # 修改成功应该退出然后提示登陆
        return redirect(url_for("admin.logout"))
    return render_template("admin/pwd.html", form=form)


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
        # db.session.commit()
        oplog = Oplog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加标签：{0}".format(data["name"])
        )
        db.session.add(oplog)
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
    ).paginate(page=page, per_page=10)
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
    # db.session.commit()
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除标签：{0}".format(tag.name)
    )
    db.session.add(oplog)
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
        oplog = Oplog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加电影：{0}".format(data["title"])
        )
        db.session.add(oplog)
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
    ).paginate(page=page, per_page=10)
    return render_template("admin/movie_list.html", page_data=page_data)


# 电影删除
@admin.route("/movie/del/<int:id>/", methods=["GET"])
@admin_login_req
def movie_del(id=None):
    movie = Movie.query.filter_by(id=id).first_or_404()
    db.session.delete(movie)
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除电影：{0}".format(movie.title)
    )
    db.session.add(oplog)
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
        oplog = Oplog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加上映预告：{0}".format(data["title"])
        )
        db.session.add(oplog)
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
    ).paginate(page=page, per_page=10)
    return render_template("admin/preview_list.html", page_data=page_data)


# 上映预告删除
@admin.route("/preview/del/<int:id>/", methods=["GET"])
@admin_login_req
def preview_del(id=None):
    preview = Preview.query.filter_by(id=id).first_or_404()
    db.session.delete(preview)
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除上映预告：{0}".format(preview.title)
    )
    db.session.add(oplog)
    db.session.commit()
    flash("删除上映预告成功", "ok")
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


# 会员列表
@admin.route("/user/list/", methods=["GET"])
@admin.route("/user/list/<int:page>/", methods=["GET"])
@admin_login_req
def user_list(page=None):
    if page is None:
        page = 1
    page_data = User.query.order_by(
        User.addtime.asc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/user_list.html", page_data=page_data)


# 会员查看
@admin.route("/user/view/<int:id>/", methods=["GET"])
@admin_login_req
def user_view(id=None):
    user = User.query.filter_by(id=id).first_or_404()
    return render_template("admin/user_view.html", user=user)


# 会员删除
# 暂时不启用 会员直接删除好像有点蠢 可以考虑加黑名单
@admin.route("/user/del/<int:id>/", methods=["GET"])
@admin_login_req
def user_del(id=None):
    pass
    # user = User.query.filter_by(id=id).first_or_404()
    # db.session.delete(user)
    # db.session.commit()
    # flash("删除会员成功", "ok")
    # return redirect(url_for("admin.user_list"))


# 评论列表
@admin.route("/comment/list/", methods=["GET"])
@admin.route("/comment/list/<int:page>", methods=["GET"])
@admin_login_req
def comment_list(page=None):
    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.asc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/comment_list.html", page_data=page_data)


# 评论删除
@admin.route("/comment/del/<int:id>/", methods=["GET"])
@admin_login_req
def comment_del(id=None):
    comment = Comment.query.filter_by(id=id).first_or_404()
    db.session.delete(comment)
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除评论，评论 id 为：{0}，用户 id 为：{1}，电影 id 为：{2}".format(comment.id, comment.user_id, comment.movie_id)
    )
    db.session.add(oplog)
    db.session.commit()
    flash("删除评论成功", "ok")
    return redirect(url_for("admin.comment_list"))


# 电影收藏列表
@admin.route("/moviecol/list/", methods=["GET"])
@admin.route("/moviecol/list/<int:page>/", methods=["GET"])
@admin_login_req
def moviecol_list(page=None):
    if page is None:
        page = 1
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == Moviecol.user_id
    ).order_by(
        Moviecol.addtime.asc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/moviecol_list.html", page_data=page_data)


# 电影收藏删除
@admin.route("/moviecol/del/<int:id>/", methods=["GET"])
@admin_login_req
def moviecol_del(id=None):
    moviecol = Moviecol.query.filter_by(id=id).first_or_404()
    db.session.delete(moviecol)
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除电影收藏，电影 id 为：{0}，用户 id 为：{1}".format(moviecol.movie_id, moviecol.user_id)
    )
    db.session.add(oplog)
    db.session.commit()
    flash("删除电影收藏成功", "ok")
    return redirect(url_for("admin.moviecol_list"))


# 操作日志列表
@admin.route("/oplog/list/", methods=["GET"])
@admin.route("/oplog/list/<int:page>/", methods=["GET"])
@admin_login_req
def oplog_list(page=None):
    if page is None:
        page = 1
    page_data = Oplog.query.join(
        Admin
    ).filter(
        Oplog.admin_id == Admin.id,
    ).order_by(
        Oplog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/oplog_list.html", page_data=page_data)


# 管理员登陆日志列表
@admin.route("/adminloginlog/list/", methods=["GET"])
@admin.route("/adminloginlog/list/<int:page>/", methods=["GET"])
@admin_login_req
def adminloginlog_list(page=None):
    if page is None:
        page = 1
    page_data = Adminlog.query.join(
        Admin
    ).filter(
        Adminlog.admin_id == Admin.id,
    ).order_by(
        Adminlog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/adminloginlog_list.html", page_data=page_data)


# 会员登陆日志
@admin.route("/userloginlog/list/", methods=["GET"])
@admin.route("/userloginlog/list/<int:page>/", methods=["GET"])
@admin_login_req
def userloginlog_list(page=None):
    if page is None:
        page = 1
    page_data = Userlog.query.join(
        User
    ).filter(
        Userlog.user_id == User.id,
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/userloginlog_list.html", page_data=page_data)


# 权限添加
@admin.route("/auth/add/", methods=["GET", "POST"])
@admin_login_req
def auth_add():
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        auth = Auth(
            name=data["name"],
            url=data["url"]
        )
        db.session.add(auth)
        oplog = Oplog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加权限控制 "
                   "name: {0} "
                   "url: {1}".format(auth.name, auth.url)
        )
        db.session.add(oplog)
        db.session.commit()
        flash("权限添加成功", "ok")
        return redirect(url_for("admin.auth_add"))
    return render_template("admin/auth_add.html", form=form)


# 权限列表
@admin.route("/auth/list/", methods=["GET"])
@admin.route("/auth/list/<int:page>/", methods=["GET"])
@admin_login_req
def auth_list(page=None):
    if page is None:
        page = 1
    page_data = Auth.query.order_by(
        Auth.url.asc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/auth_list.html", page_data=page_data)


# 权限删除
@admin.route("/auth/del/<int:id>/", methods=["GET"])
@admin_login_req
def auth_del(id=None):
    auth = Auth.query.filter_by(id=id).first_or_404()
    db.session.delete(auth)
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除权限：{0} url: {1}".format(auth.name, auth.url)
    )
    db.session.add(oplog)
    db.session.commit()
    flash("删除权限成功", "ok")
    return redirect(url_for("admin.auth_list"))


# 权限编辑
@admin.route("/auth/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def auth_edit(id=None):
    form = AuthForm()
    auth = Auth.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        data = form.data
        auth.name = data["name"]
        auth.url = data["url"]
        db.session.add(auth)
        db.session.commit()
        flash("修改权限成功", "ok")
        return redirect(url_for("admin.auth_edit", id=id))
    return render_template("admin/auth_edit.html", form=form, auth=auth)


# 角色添加
@admin.route("/role/add/", methods=["GET", "POST"])
@admin_login_req
def role_add():
    form = RoleForm()
    # 在 forms 里面查出的 auths 不会自动更新的 后期看看有没有其他方法 没有的话就用这个吧。
    # form.auths.choices = [(i.id, i.name) for i in Auth.query.all()]
    if form.validate_on_submit():
        data = form.data
        role = Role(
            name=data["name"],
            auths=",".join(map(lambda i: str(i), data["auths"]))
        )
        db.session.add(role)
        oplog = Oplog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加角色：{0}".format(role.name)
        )
        db.session.add(oplog)
        db.session.commit()
        flash("添加角色成功", "ok")
        return redirect(url_for("admin.role_add"))
    return render_template("admin/role_add.html", form=form)


# 角色列表
@admin.route("/role/list/", methods=["GET"])
@admin.route("/role/list/<int:page>/", methods=["GET"])
@admin_login_req
def role_list(page=None):
    if page is None:
        page = 1
    page_data = Role.query.order_by(
        Role.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/role_list.html", page_data=page_data)


# 角色删除
@admin.route("/role/del/<int:id>/", methods=["GET"])
@admin_login_req
def role_del(id=None):
    role = Role.query.filter_by(id=id).first_or_404()
    db.session.delete(role)
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除角色：{0}".format(role.name)
    )
    db.session.add(oplog)
    db.session.commit()
    flash("删除角色成功", "ok")
    return redirect(url_for("admin.role_list"))


# 角色编辑
@admin.route("/role/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def role_edit(id=None):
    form = RoleForm()
    role = Role.query.filter_by(id=id).first_or_404()
    if request.method == "GET":
        auths = role.auths
        if auths:
            form.auths.data = list(map(lambda i: int(i), auths.split(",")))
    if form.validate_on_submit():
        data = form.data
        role.name = data["name"]
        role.auths = ",".join(map(lambda i: str(i), data["auths"]))
        db.session.add(role)
        db.session.commit()
        flash("修改角色成功", "ok")
        return redirect(url_for("admin.role_edit", id=id))
    return render_template("admin/role_edit.html", form=form, role=role)


@admin.route("/admin/add/")
@admin_login_req
def admin_add():
    return render_template("admin/admin_add.html")


@admin.route("/admin/list/")
@admin_login_req
def admin_list():
    return render_template("admin/admin_list.html")
