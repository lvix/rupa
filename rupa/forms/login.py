#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: login.py
@time: 18/5/12 18:21
"""
from flask import session
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, TextAreaField, SelectField, DateField, IntegerField
from wtforms.validators import Length, Email, EqualTo, DataRequired, Regexp, URL

from rupa.models import User


class LoginForm(FlaskForm):
    # 官方文档建议使用 DataRequired() 代替 Required()
    email = StringField('邮箱', validators=[DataRequired(message='邮箱不可为空'),
                                          Email(message='邮箱地址格式不正确')])
    password = PasswordField('密码', validators=[DataRequired(message='密码不可为空'),
                                               Length(6, 24, message='密码长度要在6~24个字符之间')])
    captcha = StringField('验证码', validators=[DataRequired(), Length(max=4)])
    remember_me = BooleanField('记住登录')

    submit = SubmitField('登录')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱未注册')

    def validate_password(self, field):
        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user and not user.check_password(field.data):
            raise ValidationError('密码错误')

    def validate_captcha(self, field):
        captcha_word = session.get('captcha_word')
        # print(captcha_word)
        # print(self.captcha.data.upper())
        if captcha_word != self.captcha.data.upper():
            raise ValidationError('验证码错误')
