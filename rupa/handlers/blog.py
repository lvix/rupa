#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: user.py
@time: 18/5/10 16:40
"""

from flask import Blueprint, url_for, render_template, request, current_app
from rupa.models import db, User, Post, Blog

blog = Blueprint('blog', __name__, url_prefix='/blog')


@blog.route('/<int:blog_id>/')
def blog_page(blog_id):
    """
    博客首页
    :param blog_id: 博客id
    :return:
    """
    page = request.args.get('page', default=1, type=int)
    blog_ = Blog.query.get_or_404(blog_id)
    pagination = blog_.posts.order_by(Post.published_at.desc()).paginate(
        page=page,
        per_page=current_app.config['INDEX_PER_PAGE'],
        error_out=False
        )

    return render_template('blog.html', blog=blog_,
                           pagination=pagination,
                           endpoint='blog.blog_page',
                           blog_id=blog_id
                           )
