# -*- coding:utf-8 _*-  
""" 
@author: ronething 
@file: models.py 
@time: 2018/10/21
@github: github.com/ronething 

Less is more.
"""

from datetime import datetime

from app import db


# 会员数据模型
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)   # 昵称
    pwd = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(11), unique=True)
    info = db.Column(db.Text)                       # 个性简介
    face = db.Column(db.String(255), unique=True)   # 头像
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)   # 注册时间
    uuid = db.Column(db.String(255), unique=True)   # 唯一标识符
    userlogs = db.relationship('Userlog', backref='user')   # 会员日志外键关系关联
    comments = db.relationship("Comment", backref='user')   # 评论外键关联
    moviecols = db.relationship("Moviecol", backref='user') # 电影收藏外键关联

    def __repr__(self):
        return "<user %r>" % self.name


# 会员登陆日志
class Userlog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip = db.Column(db.String(100))  # 登陆 ip
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)   # 最近登陆时间

    def __repr__(self):
        return "<Userlog %r>" % self.id


# 电影标签
class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    movies = db.relationship("Movie", backref="tag")    # 电影外键关联

    def __repr__(self):
        return "<Tag %r>" % self.name


# 电影
class Movie(db.Model):
    __tablename__ = "movie"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True)
    url = db.Column(db.String(255), unique=True)
    info = db.Column(db.Text)
    logo = db.Column(db.String(255))
    star = db.Column(db.SmallInteger)   # 星级
    playnum = db.Column(db.BigInteger)
    commentnum = db.Column(db.BigInteger)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))     # 所属标签
    area = db.Column(db.String(255))    # 上映地区
    release_time = db.Column(db.Date)   # 上映时间
    length = db.Column(db.String(100))  # 电影长度
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)   # 添加时间
    comments = db.relationship("Comment", backref='movie')   # 评论外键关联
    moviecols = db.relationship("Moviecol", backref='movie') # 电影收藏外键关联

    def __repr__(self):
        return "<Movie %r>" % self.title


# 上映预告
class Preview(db.Model):
    __tablename__ = "preview"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True)
    logo = db.Column(db.String(255))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)   # 添加时间

    def __repr__(self):
        return "<Preview %r>" % self.title


# 评论
class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)   # 添加时间

    def __repr__(self):
        return "<Comment %r>" % self.id


# 电影收藏
class Moviecol(db.Model):
    __tablename__ = "moviecol"
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)   # 添加时间

    def __repr__(self):
        return "<Moviecol %r>" % self.id


# 权限模型
class Auth(db.Model):
    __tablename__ = "auth"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    url = db.Column(db.String(255), unique=True)    # 权限 url
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)   # 添加时间

    def __repr__(self):
        return "<Auth %r>" % self.name


# 角色模型
class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    auths = db.Column(db.String(600))   # 角色权限列表
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)   # 添加时间
    admins = db.relationship("Admin", backref='role')   #管理员外键关系约束

    def __repr__(self):
        return "<Role %r>" % self.name


# 管理员
class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)   # 管理员账号
    pwd = db.Column(db.String(100))
    is_super = db.Column(db.SmallInteger)   # 是否为超级管理员，0 为超级管理员
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # 所属角色
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)   # 添加时间
    adminlogs = db.relationship("Adminlog", backref='admin')
    oplogs = db.relationship("Oplog", backref='admin')

    def __repr__(self):
        return "<Admin %r>" % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


# 管理员登陆日志
class Adminlog(db.Model):
    __tablename__ = "adminlog"
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属管理员
    ip = db.Column(db.String(100))  # 登陆 ip
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)   # 最近登陆时间

    def __repr__(self):
        return "<Adminlog %r>" % self.id


# 操作日志
class Oplog(db.Model):
    __tablename__ = "oplog"
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属管理员
    ip = db.Column(db.String(100))  # 登陆 ip
    reason = db.Column(db.String(600))  # 操作原因
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)   # 最近登陆时间

    def __repr__(self):
        return "<Oplog %r>" % self.id


if __name__ == '__main__':
    pass
    # db.create_all()
    # role = Role(
    #     name="超级管理员",
    #     auths=""
    # )
    # db.session.add(role)
    # db.session.commit()

    # from werkzeug.security import generate_password_hash
    # admin = Admin(
    #     name="hello",
    #     pwd=generate_password_hash("hello"),
    #     is_super=0,
    #     role_id=1,
    # )
    # db.session.add(admin)
    # db.session.commit()