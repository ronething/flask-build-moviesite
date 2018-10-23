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
    SelectField
from wtforms.validators import DataRequired, ValidationError

from app.models import Admin, Tag

# 查询所有标签
tags = Tag.query.all()


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
            "id": "input_name",
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
            "id": "input_title",
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
            "id": "input_url",
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
            "id": "input_info",
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
            "id": "input_logo",
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
            "id": "input_star",
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
            "id": "input_tag_id",
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
            "id": "input_area",
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
            "id": "input_length",
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
            "id": "input_release_time",
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

