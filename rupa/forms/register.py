#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: register.py
@time: 18/6/4 5:04
"""
from flask import url_for, session, current_app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, IMAGES
from wtforms import StringField, SelectField, PasswordField, SubmitField, TextAreaField, BooleanField, ValidationError
from wtforms.validators import Length, Email, EqualTo, DataRequired, Regexp, URL

from rupa.models import db, User, Notifibox, MicroBlog, MessageBox, Icon, InvitationCode, Album

from datetime import datetime
import re
import hashlib


class RegisterForm(FlaskForm):
    register_username = StringField('用户名', validators=[DataRequired(message='用户名不可为空'),
                                                       Length(4, 16, message='长度应在4~16个字符之间'),
                                                       Regexp('^[\w]*$', message='仅包括字母、数字和下划线')])

    nickname = StringField('昵称', validators=[DataRequired(message='昵称不可为空'),
                                             Length(4, 20, message='长度应在4~20个字符之间'),
                                             Regexp(r'^[^,<>;:\-_=&%#@!~`\*\.\?\+\$\^\[\]\(\)\{\}\|\\\/]*$',
                                                    message='包含有奇怪的字符')])
    register_password = PasswordField('密码', validators=[DataRequired(message='密码不可为空'), ])
    repeat_password = PasswordField('重复密码', validators=[DataRequired(message='密码不可为空'),
                                                        EqualTo('register_password', message='密码不一致')])
    email = StringField('邮箱', validators=[DataRequired(message='邮箱不可为空'), Email(message='请输入正确的邮箱地址')])

    captcha = StringField('验证码', validators=[DataRequired(), Length(max=4)])
    invitation_code = StringField('邀请码')
    user_agreement = BooleanField('我已阅读并同意用户协议')
    submit = SubmitField('注册')

    def validate_register_username(self, field):
        # 在数据库中没有记录
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已注册')

    def validate_register_password(self, field):
        # 只包含英文字母和标点符号
        if re.compile(r'^[\w,<>;:\-_=&%#@!~`\*\.\?\+\$\^\[\]\(\)\{\}\|\\\/]{8,16}$').match(field.data) is None:
            raise ValidationError('密码应为8~16个字符长度，仅包含数字、字母和标点符号')

    def validate_email(self, field):
        # 在数据库中没有记录
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已注册')

    def validate_user_agreement(self, field):
        if field.data is None:
            raise ValidationError('必须同意用户协议')

    def validate_captcha(self, field):
        captcha_word = session.get('captcha_word')
        # print(captcha_word)
        # print(self.captcha.data.upper())
        if captcha_word != self.captcha.data.upper():
            raise ValidationError('验证码错误')

    def validate_invitation_code(self, field):
        if current_app.config['INVITE_REQUIRED']:
            if len(field.data) != 24:
                raise ValidationError('邀请码格式错误')
            ic = InvitationCode.query.filter_by(code=field.data).first()
            if ic is None:
                raise ValidationError('邀请码错误')
            if ic.status == ic.STATUS_USED:
                raise ValidationError('邀请码已被使用')
            if ic.status == ic.STATUS_EXPIRED or ic.expired_time < datetime.utcnow():
                ic.status = ic.STATUS_EXPIRED
                try:
                    db.session.add(ic)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                raise ValidationError('邀请码已过期')

    def register_user(self):
        try:
            new_user = User()
            new_user.role = User.ROLE_USER

            new_user.username = self.register_username.data.lower()
            new_user.password = self.register_password.data
            new_user.nickname = self.nickname.data
            new_user.email = self.email.data

            new_notifbox = Notifibox(user=new_user)
            new_microblog = MicroBlog(user=new_user)
            new_messagebox = MessageBox(user=new_user)
            new_icon = Icon(user=new_user)
            new_album = Album(name='默认相册', user=new_user)
            if current_app.config['INVITE_REQUIRED']:
                code = InvitationCode.query.filter_by(code=self.invitation_code.data).first()
                new_user.invitation_code = code
                code.status = code.STATUS_USED

            db.session.add(new_notifbox)
            db.session.add(new_microblog)
            db.session.add(new_messagebox)
            db.session.add(new_icon)
            db.session.add(new_user)
            db.session.add(new_album)
            db.session.commit()

            return new_user
        except Exception as e:
            db.session.rollback()
            print(e)
            return


class ProfileForm(FlaskForm):
    nickname = StringField('昵称', validators=[DataRequired(message='用户名不可为空'),
                                             Length(3, 20, message='长度应在3~20个字符之间'),
                                             Regexp('^[^,<>;:\-=&%#@!~`\*\.\?\+\$\^\[\]\(\)\{\}\|\\\/]*$',
                                                    message='包含有奇怪的字符')])
    icon = FileField('上传头像')
    introduction = TextAreaField('自述', validators=[Length(max=300, message='不能超过300字')])
    gender = SelectField('性别', validators=[DataRequired(message='性别信息错误')],
                         choices=[('0', '性别保密'), ('1', '男'), ('2', '女')])
    country = StringField('国家', validators=[Length(max=24, message='不得超过24个字符')])
    province = StringField('省份', validators=[Length(max=24, message='不得超过24个字符')])
    city = StringField('城市', validators=[Length(max=24, message='不得超过24个字符')])
    submit = SubmitField('保存')
    # icon_url = None

    def validate_icon(self, field):
        if field.data:
            # print(field.data.filename)
            if not re.compile(r'^[^/\\]+\.(jpg|jpeg|png|gif)$').match(field.data.filename):
                raise ValidationError('文件类型错误')

    def load_info(self, user):
        self.nickname.data = user.nickname
        self.introduction.data = user.introduction
        self.gender.data = str(user.gender)
        self.country.data = user.country
        self.province.data = user.province
        self.city.data = user.city
        # self.icon_url = url_for('static', filename='icon/default_icon.png')
        # if user.icon is not None:
        #     self.icon_url = user.icon.url_thumb

    def update_info(self, user):
        try:
            user.nickname = self.nickname.data
            user.introduction = self.introduction.data
            # print(self.gender.data)
            user.gender = int(self.gender.data)
            user.country = self.country.data
            user.province = self.province.data
            user.city = self.city.data
            db.session.add(user)
            db.session.commit()

            if self.icon.data:
                icon = user.icon
                if user.icon is None:
                    icon = Icon(user=user)
                icon.update_icon(self.icon.data)
            return True
        except Exception as e:
            db.session.rollback()
            raise e
