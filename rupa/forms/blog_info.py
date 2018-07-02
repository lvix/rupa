#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: blog_info.py
@time: 18/6/15 5:55
"""


from flask_wtf import FlaskForm

from wtforms import StringField, SelectField, SubmitField, TextAreaField, BooleanField, ValidationError
from wtforms.validators import Length, Email, EqualTo, DataRequired, Regexp, URL

from rupa.models import db, Blog
from flask_login import current_user

import re


class BlogInfoForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(message='标题不可为空'), Length(max=256)])
    description = TextAreaField('博客介绍', validators=[Length(max=256)])
    permanent_link = StringField('永久链接', validators=[Length(4, 16)])
    # password =
    submit = SubmitField('提交')

    def validate_permanent_link(self, field):
        if current_user.blog.permanent_link:
            raise ValidationError('永久链接只能设置一次')
        if len(field.data) > 0:
            if re.compile(r'^[0-9a-zA-Z\-]*$').match(field.data) is None:
                raise ValidationError('永久链接仅包含字母、数字 和连字符(-) ')

    def update_info(self):
        try:
            if current_user.blog is None:
                blog = Blog(user=current_user)
            else:
                blog = current_user.blog
            blog.title = self.title.data
            blog.description = self.description.data
            if blog.permanent_link is None and self.permanent_link.data:
                blog.permanent_link = self.permanent_link.data.lower()
            db.session.add(blog)
            db.session.commit()
            return blog
        except Exception as e:
            db.session.rollback()
            print('failed creating/updating blog info')
            raise e

    def load_info(self):
        try:
            blog = current_user.blog
            self.title.data = blog.title
            self.description.data = blog.description
            self.permanent_link.data = blog.permanent_link
            return True
        except Exception as e:
            print('Failed loading blog info：')
            print(e)
            return False
    