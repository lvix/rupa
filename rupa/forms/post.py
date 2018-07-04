#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: post.py
@time: 18/5/23 16:35
"""
import hashlib
import re
import os
from datetime import datetime

from flask import current_app, request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField, BooleanField, ValidationError, FileField
from wtforms.validators import Length, DataRequired

from rupa.models import db, Post, Category, Tag, Photo, Album

from PIL import Image


class PostForm(FlaskForm):
    # 官方文档建议使用 DataRequired() 代替 Required()
    title = StringField('标题', validators=[DataRequired(message='标题不可为空'), Length(max=200)])
    text = TextAreaField('正文')
    new_cate = StringField('新分类', validators=[Length(max=200)])
    submit = SubmitField('发表')
    save_draft = SubmitField('保存草稿')

    intro_photo = FileField('封面照片')
    abstract = TextAreaField('摘要', validators=[Length(max=500)])
    auto_abstract = BooleanField('自动生成摘要')

    visibility = SelectField('发表状态', choices=[
        ('0', '公开'),
        ('1', '登录后可见'),
        ('2', '参与的作者可见'),
        ('3', '输入密码后可见'),
        ('4', '仅自己可见')
    ])

    post_password = StringField('文章密码', validators=[Length(max=20)])
    tags = StringField('标签', validators=[Length(max=200)])

    permanent_link = StringField('永久链接', validators=[Length(max=60)])

    category_fields = {}

    intro_photo_url = ''

    def validate_password(self, field):
        if len(field.data) > 0:
            if re.compile(r'^[0-9a-zA-Z]*$').match(field.data) is None:
                raise ValidationError('密码仅包含字母和数字')

    def validate_permanent_link(self, field):
        if len(field.data) > 0:
            if re.compile(r'^[0-9a-zA-Z\-]*$').match(field.data) is None:
                raise ValidationError('永久链接仅包含字母、数字 和连字符(-) ')

    def validate_intro_photo(self, field):
        if field.data:
            # print(field.data.filename)
            if not re.compile(r'^[^/\\]+\.(jpg|jpeg|png|gif)$').match(field.data.filename):
                raise ValidationError('文件类型错误')

    def update_post(self, post=None):
        """
        根据自身的
        :return: True False
        """

        if post is None:
            post = Post(blog=current_user.blog)
        post.title = self.title.data
        post.text = self.text.data

        # 根据分类信息创建 Boolean Fields
        post.categories = []
        for k, cate_field in self.category_fields.items():
            if cate_field.data is True:
                cate = current_user.blog.categories.filter_by(name=cate_field.label.text).first()
                if cate:
                    post.categories.append(cate)

        # 创建新的分类
        cate_str = self.new_cate.data.strip()
        new_cate_names = re.split(r'\s*[,，]\s*', cate_str)
        if len(new_cate_names) > 0:
            for cate_name in new_cate_names:
                if len(cate_name) > 0:
                    cate = current_user.blog.categories.filter_by(name=self.new_cate.data).first()
                    if cate is None:
                        cate = Category(blog=current_user.blog, name=cate_name)
                    if cate not in post.categories:
                        post.categories.append(cate)
                    db.session.add(cate)

        # 处理永久链接
        permanent_link = self.permanent_link.data
        if len(permanent_link) > 0:
            post.permanent_link = permanent_link.lower().strip()

        # 处理可见性
        post.visibility = int(self.visibility.data)

        # 处理Tags
        post.tags = []
        tags_str = self.tags.data.strip()
        tag_names = re.split(r'\s*[,，]\s*', tags_str)
        # print(tags_str, tag_names)
        if len(tag_names) > 0:
            for tag_name in tag_names:
                if len(tag_name) > 0:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if tag is None:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    post.tags.append(tag)

        # 处理摘要
        if self.auto_abstract.data is True:
            post.gen_abstract()
        else:
            post.abstract = self.abstract.data

        # 处理封面照片
        if self.intro_photo.data:
            post.intro_photo = self.save_photo(self.intro_photo.data)
            self.intro_photo_url = post.intro_photo.url_thumb

        post.password = self.post_password.data if len(self.post_password.data) > 0 else None

        self.new_cate.data = ''
        db.session.add(post)
        db.session.commit()

        return post

    def load_post(self, post):
        """
        从数据库中加载文章内容到表格
        :param post: 文章数据库对象
        :return:
        """

        self.title.data = post.title
        self.text.data = post.text
        for cate in post.categories:
            getattr(self, 'cate_' + cate.name).data = True
        self.permanent_link.data = post.permanent_link
        self.visibility.data = str(post._visibility)
        self.abstract.data = post.abstract

        tags_str = ', '.join([tag.name for tag in post.tags])
        self.tags.data = tags_str
        self.post_password.data = post.password

        if post.intro_photo:
            self.intro_photo_url = post.intro_photo.url_thumb

    def save_photo(self, field_data):
        """
        保存照片，并生成数据库记录
        :return: 数据记录 Photo 对象
        """
        if field_data is None:
            return
        img_path = ''
        thumb_path = ''
        try:
            new_photo = Photo()
            new_photo.album = Album.query.filter_by(user=current_user).filter_by(name='文章封面').first()
            # print(new_photo.album)
            if new_photo.album is None:
                cover_album = Album(name="文章封面", user=current_user)
                db.session.add(cover_album)
                new_photo.album = cover_album

            title = field_data.filename.split('.')[0].lower()
            fmt = field_data.filename.split('.')[-1].lower()
            img_name = hashlib.md5((fmt + datetime.utcnow().strftime('%Y%m%d%H%M%S%f') + fmt).encode('utf-8')).hexdigest()
            img_dir = current_app.config['UPLOADED_PHOTO_DEST']

            img = Image.open(field_data)
            img_path = os.getcwd() + img_dir + img_name + '.{}'.format(fmt)

            img.save(img_path, 'jpeg' if fmt == 'jpg' else fmt)

            thumb = Image.open(field_data)
            w, h = thumb.size
            if h > w:
                h = int(240 / w * h)
                w = 240
                if h < 320:
                    w, h = thumb.size
                    w = int(320 / h * w)
                    h = 320
            elif w > h:
                w = int(320 / h * w)
                h = 320
                if w < 240:
                    w, h = thumb.size
                    h = int(240 / w * h)
                    w = 240
            else:
                h = 320
                w = 320
            thumb = thumb.resize((w, h), Image.BICUBIC)

            # if w > 240:
            x0, y0 = int((w - 240) / 2), int((h - 320) / 2)
            x1, y1 = x0 + 240, y0 + 320
            # print((x0, y0, x1, y1))
            thumb = thumb.crop((x0, y0, x1, y1))

            thumb_name = img_name + '240x320.png'
            thumb_path = os.getcwd() + img_dir + thumb_name
            thumb.save(thumb_path, 'png')

            new_photo.title = title
            new_photo.image_name = img_name + '.{}'.format(fmt)
            new_photo.image_dir = img_dir
            new_photo.thumb_name = thumb_name
            new_photo.thumb_dir = img_dir

            db.session.add(new_photo)
            db.session.commit()
            return new_photo
        except Exception as e:
            db.session.rollback()
            if os.path.isfile(img_path):
                os.remove(img_path)
            if os.path.isfile(thumb_path):
                os.remove(thumb_path)
            raise e


class PostUploadForm(FlaskForm):
    file = FileField('上传 markdown 文件', validators=[])  # Regexp(r'^[^/\\]\.(md|MD)$', message='请选择正确的文件类型')])
    auto_process = BooleanField('自动处理标题')
    submit = SubmitField('上传')

    def save_file(self):

        save_dir = os.getcwd() + current_app.config['UPLOADED_MD_DEST']
        # print(save_dir)
        # print(self.file.data.filename)
        # print(self.file.data)

        filename = hashlib.md5(
            ('md' + datetime.utcnow().strftime('%Y%m%d%H%M%S%f') + 'md').encode('utf-8')).hexdigest() + '.md'
        # print(save_dir + filename)
        try:
            with open(save_dir + filename, 'wb') as f:
                file_data = self.file.data.read()
                # print('file_data\n:', file_data)
                f.write(file_data)
            # TODO 应该再加上数据库模型 File
            return save_dir + filename
        except Exception as e:
            # print('Failed saving file')
            # print(e)
            if os.path.isfile(save_dir + filename):
                os.remove(save_dir + filename)
            raise e

    def create_post(self, file):
        post = Post(blog=current_user.blog)
        text = ''

        with open(file, 'r', encoding='utf-8') as f:
            if self.auto_process:
                # 尝试自动添加标题
                # 需要第一行是 '# title' 的格式
                first_line = f.readline()

                title_re_results = re.compile(r'^# (.*?)$').findall(first_line[:200])
                if len(title_re_results) > 0:
                    post.title = title_re_results[0].strip()
                else:
                    text += first_line

            for line in f.readlines():
                text += line
        post.text = text
        db.session.add(post)
        db.session.commit()
        return post

