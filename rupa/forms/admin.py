#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: admin
@time: 18/5/31 15:41
"""


from flask_wtf import FlaskForm

from wtforms import StringField, SelectField, SubmitField, TextAreaField, BooleanField, ValidationError
from wtforms.validators import Length, Email, EqualTo, DataRequired, Regexp, URL

from rupa.models import User, db

import re


class AdminUserForm(FlaskForm):
    """
    user_edit 页面所用的表单
    """
    nickname = StringField('昵称', validators=[DataRequired(message='昵称不可为空'),
                                             Length(6, 20, message='长度应在6~20个字符之间'),
                                             Regexp('^[^,<>;:\-_=&%#@!~`\*\.\?\+\$\^\[\]\(\)\{\}\|\\\/]*$',
                                                    message='包含有奇怪的字符')])
    role = SelectField('角色', choices=[('ADMIN', '管理员'), ('USER', '普通用户')], default='USER')
    status = SelectField('状态', choices=[('0', '正常'), ('1', '封禁')])
    introduction = TextAreaField('个人简介', validators=[Length(message='不超过256字', max=256)])

    password = StringField('重置密码')
    submit = SubmitField('提交')

    def validate_password(self, field):
        pw = field.data
        if len(pw) > 0 and re.compile('^[\w,<>;:\-_=&%#@!~`\*\.\?\+\$\^\[\]\(\)\{\}\|\\\/]{8,16}$').match(pw) is None:
            raise ValidationError('密码仅包含数字、字母和标点符号')

    def update_user(self, user=None):
        """
        根据自身的内容更新数据库相关记录
        :return: True False
        """
        try:
            if user is None:
                user = User()
                user.password = self.password.data
            else:
                if len(self.password.data) > 0:
                    user.password = self.password.data
            # user.username = self.username.data
            user.nickname = self.nickname.data
            user.role = self.role.data
            user.status = self.status.data
            # user.email = self.email.data
            user.introduction = self.introduction.data
            print(user)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            print('Failed creating/updating user info:')
            print(e)

    def load_user(self, user):
        """
        从数据库中加载用户信息到表单
        :param cate: 分类数据库对象
        :return: 成功返回 True， 否则返回 False
        """
        try:
            # self.username.data = user.username
            self.nickname.data = user.nickname
            self.role.data = user.role
            self.status.data = user.status
            # self.email.data = user.email
            self.introduction.data = user.introduction
            return True
        except Exception as e:
            print('Failed loading user info：')
            print(e)
            return False


class AdminNewUserForm(AdminUserForm):

    username = StringField('用户名', validators=[DataRequired(message='用户名不可为空'),
                                              Length(4, 16, message='长度应在4~16个字符之间')])

    email = StringField('邮箱', validators=[DataRequired(message='邮箱不可为空'),
                                          Length(message='长度应再64字符以内', max=64),
                                          Email(message='邮箱格式不正确')])

    def __init__(self):
        super().__init__(self)

    def validate_username(self, field):
        # 在数据库中没有记录
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已注册')

    def validate_email(self, field):
        # 在数据库中没有记录
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已注册')

    def update_user(self, user=None):
        """
        根据自身的内容更新数据库相关记录
        :return: True False
        """
        try:
            if user is None:
                user = User()
                user.password = self.password.data
            else:
                if len(self.password.data) > 0:
                    user.password = self.password.data
            user.username = self.username.data
            user.nickname = self.nickname.data
            user.role = self.role.data
            user.status = self.status.data
            user.email = self.email.data
            user.introduction = self.introduction.data
            print(user)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            print('Failed creating/updating user info:')
            print(e)

    def load_user(self, user):
        """
        从数据库中加载用户信息到表单
        :param cate: 分类数据库对象
        :return:
        """
        try:
            self.username.data = user.username
            self.nickname.data = user.nickname
            self.role.data = user.role
            self.status.data = user.status
            self.email.data = user.email
            self.introduction.data = user.introduction
            return True
        except Exception as e:
            print('Failed loading user info：')
            print(e)
            return False
