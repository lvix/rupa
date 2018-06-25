#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: user.py
@time: 18/5/10 16:40
"""

from flask import Blueprint, url_for, render_template, request, current_app
from rupa.models import db, User, Post

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
    pagination = None
    if user_.blog:
        pagination = user_.blog.posts.order_by(Post.published_at.desc()).paginate(
            page=page,
            per_page=current_app.config['INDEX_PER_PAGE'],
            error_out=False
            )

    return render_template('user.html', user=user_,
                           pagination=pagination,
                           endpoint='user.user_page',
                           user_id=user_id
                           )

