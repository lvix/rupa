#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: photo.py
@time: 18/6/20 4:46
"""
from flask import current_app
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, ValidationError, SubmitField
from rupa.models import db, Photo, Album
from PIL import Image
import re
import hashlib
import os
from datetime import datetime


class PhotoUploadForm(FlaskForm):
    """
    上传照片的表单
    """
    photo_field = FileField('上传照片')
    submit = SubmitField('上传')

    def validate_photo_field(self, field):
        if field.data:
            # print(field.data.filename)
            if not re.compile(r'^[^/\\]+\.(jpg|jpeg|png|gif)$').match(field.data.filename):
                raise ValidationError('文件类型错误')

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
            new_photo.album = Album.query.get(int(self.albums_field.data))
            # print(new_photo.album)

            fmt = field_data.filename.split('.')[-1].lower()
            img_name = hashlib.md5((fmt + datetime.utcnow().strftime('%Y%m%d%H%M%S%f') + fmt).encode('utf-8')).hexdigest()
            img_dir = current_app.config['UPLOADED_PHOTO_DEST']

            img = Image.open(field_data)
            img_path = os.getcwd() + img_dir + img_name + '.{}'.format(fmt)

            img.save(img_path, 'jpeg' if fmt == 'jpg' else fmt)

            thumb = Image.open(field_data)
            w, h = thumb.size
            if w < 120 < h:
                w = int(h / 120 * w)
                h = 120
            elif w > 120 > h:
                h = int(w / 120 * w)
                w = 120
            elif w > 120 and h > 120:
                if h > w:
                    w = int(h / 120 * w)
                    h = 120
                else:
                    h = int(w / 120 * w)
                    w = 120

            thumb.thumbnail((w, h))
            thumb_name = img_name + 'x120.png'
            thumb_path = os.getcwd() + img_dir + thumb_name
            thumb.save(thumb_path, 'png')

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


def user_photo_form(user=current_user):
    """
    根据用户相册信息生成表格
    :param user: 被读取相册信息的用户
    :return: 带有用户相册信息的 PhotoUploadForm 对象
    """
    class DynamicForm(PhotoUploadForm):
        pass

        def validate_albums_field(self, field):
            target = Album.query.get(int(field.data))
            if target is None:
                raise ValidationError('相册不存在')
            if target.user.id != current_user.id:
                raise ValidationError('数据错误')

    choices = []
    for album in user.albums:
        choices.append((str(album.id), album.name))
    albums_field = SelectField('选择相册', choices=choices)
    setattr(DynamicForm, 'albums_field', albums_field)
    form = DynamicForm()
    return form



