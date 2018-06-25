#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: post.py
@time: 18/5/23 16:35
"""

from flask_wtf import FlaskForm

from wtforms import StringField, SelectField, SubmitField, TextAreaField, BooleanField, ValidationError
from wtforms.validators import Length, Email, EqualTo, DataRequired, Regexp, URL

from rupa.models import db, Category
from flask_login import current_user


class CateForm(FlaskForm):
    # 官方文档建议使用 DataRequired() 代替 Required()
    name = StringField('标题', validators=[DataRequired(message='标题不可为空'), Length(max=200)])
    submit = SubmitField('提交')

    def update_cate(self, cate=None):
        """
        根据自身的内容更新数据库相关记录
        :return: True False
        """
        try:
            if cate is None:
                cate = Category(blog=current_user.blog)
            cate.name = self.name.data
            db.session.add(cate)
            db.session.commit()
            return cate
        except Exception as e:
            db.session.rollback()
            print('Failed creating/updating category:')
            print(e)

    def load_cate(self, cate):
        """
        从数据库中加载分类到表格
        :param cate: 分类数据库对象
        :return:
        """
        try:
            self.name.data = cate.name
            return True
        except Exception as e:
            print('Failed loading category：')
            print(e)
            return False
