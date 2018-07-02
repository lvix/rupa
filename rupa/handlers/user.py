#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: user.py
@time: 18/5/10 16:40
"""

from flask import Blueprint, url_for, render_template, request, current_app, redirect
from flask_login import current_user
from rupa.models import db, User, Post, Blog

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/<int:user_id>/')
def user_page(user_id):
    """
    用户详情页面
    :param user_id: 用户id
    :return:
    """
    page = request.args.get('page', default=1, type=int)
    user_ = User.query.get_or_404(user_id)
    blog = Blog.query.filter_by(user=user_).first_or_404()

    if current_user == user_:
        # 如果是用户本人则加载所有文章
        pagination = blog.posts.order_by(Post.published_at.desc()).paginate(
            page=page,
            per_page=current_app.config['INDEX_PER_PAGE'],
            error_out=False
        )
    elif current_user.is_authenticated:
        # 加载登录后可见的文章
        # TODO 以及参与协作的文章
        pagination = blog.posts.filter(Post._visibility <= 1).order_by(
            Post.published_at.desc()).paginate(
            page=page,
            per_page=current_app.config['INDEX_PER_PAGE'],
            error_out=False
        )
    else:
        # 加载公开的文章
        pagination = blog.posts.filter(Post._visibility == 0).order_by(
            Post.published_at.desc()).paginate(
            page=page,
            per_page=current_app.config['INDEX_PER_PAGE'],
            error_out=False
        )
    if page > pagination.pages:
        return redirect(url_for('user.user_page', user_id=user_.id, page=pagination.pages))
    return render_template('user.html', user=user_,
                           pagination=pagination,
                           endpoint='user.user_page',
                           user_id=user_id
                           )
