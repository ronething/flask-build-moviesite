# -*- coding:utf-8 _*-  
""" 
@author: ronething 
@file: forms.py 
@time: 2018/10/21
@github: github.com/ronething 

Less is more.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, \
    SubmitField, FileField, TextAreaField, \
    SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo

from app.models import Admin, Tag, Auth, Role

# TODO 无法实时更新 tags or auths_lsit 后续需要修改
# 查询所有标签
tags = Tag.query.all()
# 查询所有权限
auths_list = Auth.query.order_by(
    Auth.url.desc()
)
# 查询所有角色
role_list = Role.query.all()


class LoginForm(FlaskForm):
    """
    管理员登陆表单
    """
    account = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号！",
            "required": False
        }
    )

    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码！",
            "required": False
        }
    )

    submit = SubmitField(
        "登录",
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }
    )

    def validate_account(self, field):
        account = field.data
        count = Admin.query.filter_by(name=account).count()
        if count == 0:
            raise ValidationError("账号不存在！")


class TagForm(FlaskForm):
    """
    标签表单
    """
    name = StringField(
        label="名称",
        validators=[
            DataRequired("请输入标签！")
        ],
        description="标签",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入标签名称！",
            "required": False
        }
    )

    submit = SubmitField(
        "确认",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class MovieForm(FlaskForm):
    """
    电影表单
    """
    title = StringField(
        label="片名",
        validators=[
            DataRequired("请输入片名！")
        ],
        description="片名",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入片名！",
            "required": False
        }
    )

    url = FileField(
        label="文件",
        validators=[
            DataRequired("请上传文件")
        ],
        description="文件",
        render_kw={
            "required": False
        }
    )

    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入简介！")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "rows": "10",
            "required": False
        }
    )

    logo = FileField(
        label="封面",
        validators=[
            DataRequired("请上传封面")
        ],
        description="封面",
        render_kw={
            "required": False
        }
    )

    star = SelectField(
        label="星级",
        validators=[
            DataRequired("请选择星级！")
        ],
        coerce=int,
        choices=[(1, "1星"), (2, "2星"), (3, "3星"), (4, "4星"), (5, "5星")],
        description="星级",
        render_kw={
            "class": "form-control",
            "required": False
        }
    )

    tag_id = SelectField(
        label="标签",
        validators=[
            DataRequired("请选择标签！")
        ],
        coerce=int,
        choices=[(i.id, i.name) for i in tags],
        description="标签",
        render_kw={
            "class": "form-control",
            "required": False
        }
    )

    area = StringField(
        label="地区",
        validators=[
            DataRequired("请输入地区！")
        ],
        description="地区",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入地区！",
            "required": False
        }
    )

    length = StringField(
        label="片长",
        validators=[
            DataRequired("请输入片长！")
        ],
        description="片长",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入片长！",
            "required": False
        }
    )

    release_time = StringField(
        label="上映时间",
        validators=[
            DataRequired("请选择上映时间！")
        ],
        description="上映时间",
        render_kw={
            "class": "form-control",
            "placeholder": "请选择上映时间！",
            "required": False
        }
    )

    submit = SubmitField(
        "确认",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class PreviewForm(FlaskForm):
    """
    上映预告表单
    """
    title = StringField(
        label="预告标题",
        validators=[
            DataRequired("请输入预告标题！")
        ],
        description="预告标题",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入预告标题！",
            "required": False
        }
    )

    logo = FileField(
        label="预告封面",
        validators=[
            DataRequired("请上传预告封面")
        ],
        description="预告封面",
        render_kw={
            "required": False
        }
    )

    submit = SubmitField(
        "确认",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class PwdForm(FlaskForm):
    """
    密码表单
    """
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("请输入旧密码！")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码！",
            "required": False
        }
    )

    new_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("请输入新密码！")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码！",
            "required": False
        }
    )

    check_pwd = PasswordField(
        label="确认密码",
        validators=[
            DataRequired("请输入确认密码！"),
            EqualTo("new_pwd", message="两次密码不一致！")
        ],
        description="确认密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入确认密码！",
            "required": False
        }
    )

    submit = SubmitField(
        "确认",
        render_kw={
            "class": "btn btn-primary"
        }
    )

    def validate_old_pwd(self, field):
        from flask import session, flash
        old_pwd = field.data
        if session.get("account") is None:
            raise ValidationError("不谈了！")
        name = session["account"]
        account = Admin.query.filter_by(name=name).first()
        if not account.check_pwd(old_pwd):
            flash("旧密码错误！", "err")
            raise ValidationError("旧密码错误！")


class AuthForm(FlaskForm):
    """
    权限控制表单
    """
    name = StringField(
        label="权限名称",
        validators=[
            DataRequired("请输入权限名称！")
        ],
        description="权限名称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限名称！",
            "required": False
        }
    )

    url = StringField(
        label="权限地址",
        validators=[
            DataRequired("请输入权限地址！")
        ],
        description="权限地址",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限地址！",
            "required": False
        }
    )

    submit = SubmitField(
        "确认",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class RoleForm(FlaskForm):
    """
    角色表单
    """
    name = StringField(
        label="角色名称",
        validators=[
            DataRequired("请输入角色名称！")
        ],
        description="角色名称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入角色名称！",
            "required": False
        }
    )

    auths = SelectMultipleField(
        label="操作权限",
        validators=[
            DataRequired("请选择操作权限")
        ],
        description="操作权限",
        coerce=int,
        choices=[(i.id, i.name) for i in auths_list],
        render_kw={
            "class": "form-control",
            "required": False
        }
    )

    submit = SubmitField(
        "确认",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class AdminForm(FlaskForm):
    """
    管理员表单
    """
    name = StringField(
        label="管理员名称",
        validators=[
            DataRequired("请输入管理员名称！")
        ],
        description="管理员名称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员名称！",
            "required": False
        }
    )

    pwd = PasswordField(
        label="管理员密码",
        validators=[
            DataRequired("请输入管理员密码！")
        ],
        description="管理员密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员密码！",
            "required": False
        }
    )

    re_pwd = PasswordField(
        label="确认密码",
        validators=[
            DataRequired("请输入确认密码！"),
            EqualTo("pwd", message="两次密码不一致！")
        ],
        description="确认密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入确认密码！",
            "required": False
        }
    )

    role_id = SelectField(
        label="所属角色",
        validators=[
            DataRequired("请选择角色！")
        ],
        coerce=int,
        choices=[(i.id, i.name) for i in role_list],
        description="所属角色",
        render_kw={
            "class": "form-control",
            "required": False
        }
    )

    submit = SubmitField(
        "确认",
        render_kw={
            "class": "btn btn-primary"
        }
    )