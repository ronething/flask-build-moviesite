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
from wtforms.validators import DataRequired, EqualTo, Email, Regexp, ValidationError
from app.models import User


class RegisterForm(FlaskForm):
    """
    会员注册表单
    """
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称！")
        ],
        description="昵称",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入昵称！",
            "required": False
        }
    )

    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入昵称！"),
            Email("邮箱格式不正确")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入邮箱！",
            "required": False
        }
    )

    phone = StringField(
        label="手机号码",
        validators=[
            DataRequired("请输入手机号码！"),
            Regexp(r"1[3-9]\d{9}$", message="手机格式不正确！")
        ],
        description="手机号码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入手机号码！",
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
            "class": "form-control input-lg",
            "placeholder": "请输入密码！",
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
            "class": "form-control input-lg",
            "placeholder": "请输入确认密码！",
            "required": False
        }
    )

    submit = SubmitField(
        "注册",
        render_kw={
            "class": "btn btn-lg btn-success btn-block"
        }
    )

    def validate_name(self, field):
        name = field.data
        user = User.query.filter_by(name=name).count()
        if user == 1:
            raise ValidationError("昵称已经存在")

    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).count()
        if user == 1:
            raise ValidationError("邮件已经存在")

    def validate_phone(self, field):
        phone = field.data
        user = User.query.filter_by(phone=phone).count()
        if user == 1:
            raise ValidationError("手机号码已经存在")


class LoginForm(FlaskForm):
    """
    会员登陆表单
    """
    name = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={
            "class": "form-control input-lg",
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
            "class": "form-control input-lg",
            "placeholder": "请输入密码！",
            "required": False
        }
    )

    submit = SubmitField(
        "登录",
        render_kw={
            "class": "btn btn-lg btn-primary btn-block"
        }
    )

    def validate_name(self, field):
        name = field.data
        count = User.query.filter_by(name=name).count()
        if count == 0:
            raise ValidationError("账号不存在！")


class UserDetailForm(FlaskForm):
    """
    会员详情表单
    """
    name = StringField(
        label="昵称",
        description="昵称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入昵称！",
            "readonly": "readonly",
            "required": False
        }
    )

    email = StringField(
        label="邮箱",
        description="邮箱",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入邮箱！",
            "readonly": "readonly",
            "required": False
        }
    )

    phone = StringField(
        label="手机号码",
        description="手机号码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入手机号码！",
            "readonly": "readonly",
            "required": False
        }
    )

    logo = FileField(
        label="头像",
        validators=[
            DataRequired("请上传头像")
        ],
        description="头像",
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

    submit = SubmitField(
        "保存修改",
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
        "修改密码",
        render_kw={
            "class": "btn btn-primary"
        }
    )

    def validate_old_pwd(self, field):
        from flask import session, flash
        old_pwd = field.data
        if session.get("user_id") is None:
            raise ValidationError("不谈了！")
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        if not user.check_pwd(old_pwd):
            flash("旧密码错误！", "err")
            raise ValidationError("旧密码错误！")


class CommentForm(FlaskForm):
    """
    评论表单
    """
    content =TextAreaField(
        label="评论内容",
        validators=[
            DataRequired("请输入评论内容"),
        ],
        description="评论内容",
        render_kw={
            "required": False
        }
    )

    submit = SubmitField(
        "提交评论",
        render_kw={
            "class": "btn btn-success",
        }
    )
