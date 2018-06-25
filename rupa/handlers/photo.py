#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: photo.py
@time: 18/6/6 5:27
"""

from flask import Blueprint, request, send_file, abort, render_template, flash
from rupa.models import Photo, User, Icon
from rupa.decorators import roles_required
from rupa.forms import user_photo_form
import os

photo = Blueprint('photo', __name__, url_prefix='/photo')


@photo.route('/upload/', methods=['GET', 'POST'])
@roles_required([User.ROLE_USER])
def photo_upload():
    form = user_photo_form()
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        if form.validate_on_submit():
            new_photo = form.save_photo(form.photo_field.data)
            if new_photo:
                flash('上传成功 ' + new_photo.url, 'success')
            else:
                flash('上传失败', 'danger')
        else:
            flash('上传失败', 'danger')
    return render_template('dashboard/photo_upload.html', form=form)


@photo.route('/p/<filename>/', methods=['GET'])
def photo_get(filename):
    target = Photo.query.filter_by(image_name=filename).first()
    # print(target)
    if request.referrer is None or request.referrer.find(request.host_url) is None:
        abort(404)
    path = target.full_path
    # print(path)
    return send_file(os.getcwd() + '/' + path)


@photo.route('/thumb/<filename>/', methods=['GET'])
def photo_thumb(filename):
    target = Photo.query.filter_by(thumb_name=filename).first()
    if request.referrer is None or request.referrer.find(request.host_url):
        abort(404)

    path = target.full_path_thumb
    print(path)

    return send_file(os.getcwd() + '/' + path)


@photo.route('/icon/<filename>/', methods=['GET'])
def icon_get(filename):
    size = request.args.get('size', default=400, type=int)
    target = Icon.query.filter_by(image_name=filename).first_or_404()
    if request.referrer is None or request.referrer.find(request.host_url) is None:
        abort(404)

    return send_file(os.getcwd() + target.full_path(size))
