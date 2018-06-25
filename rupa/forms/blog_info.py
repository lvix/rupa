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


class BlogInfoForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(message='标题不可为空'), Length(max=256)])
    description = TextAreaField('博客介绍', validators=[Length(max=256)])
    # password =
    submit = SubmitField('提交')

    def update_info(self):
        try:
            if current_user.blog is None:
                blog = Blog(user=current_user)
            else:
                blog = current_user.blog
            blog.title = self.title.data
            blog.description = self.description.data
            db.session.add(blog)
            db.session.commit()
            return blog
        except Exception as e:
            db.session.rollback()
            print('failed creating/updating blog info')
            print('e')

    def load_info(self):
        try:
            blog = current_user.blog
            self.title.data = blog.title
            self.description.data = blog.description
            return True
        except Exception as e:
            print('Failed loading blog info：')
            print(e)
            return False
    