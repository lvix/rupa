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
    if blog_.permanent_link:
        return redirect(url_for('blog.blog_page_plink', permanent_link=blog_.permanent_link, page=page))
    if current_user == blog_.user:
        # 如果是用户本人则加载所有文章
        pagination = blog_.posts.order_by(Post.published_at.desc()).paginate(
            page=page,
            per_page=current_app.config['INDEX_PER_PAGE'],
            error_out=False
        )
    elif current_user.is_authenticated:
        # 加载登录后可见的文章
        # TODO 以及参与协作的文章
        pagination = blog_.posts.filter(Post._visibility <= 1).order_by(
            Post.published_at.desc()).paginate(
            page=page,
            per_page=current_app.config['INDEX_PER_PAGE'],
            error_out=False
        )
    else:
        # 加载公开的文章
        pagination = blog_.posts.filter(Post._visibility == 0).order_by(
            Post.published_at.desc()).paginate(
            page=page,
            per_page=current_app.config['INDEX_PER_PAGE'],
            error_out=False
        )
    if page > pagination.pages:
        return redirect(url_for('blog.blog_page', user_id=blog_.user.id, page=pagination.pages))
    return render_template('blog.html', blog=blog_,
                           pagination=pagination,
                           endpoint='blog.blog_page',
                           blog_id=blog_id
                           )


@blog.route('/<permanent_link>/')
def blog_page_plink(permanent_link):
    page = request.args.get('page', default=1, type=int)
    blog_ = Blog.query.filter_by(permanent_link=permanent_link).first_or_404()
    if current_user == blog_.user:
        # 如果是用户本人则加载所有文章
        pagination = blog_.posts.order_by(Post.published_at.desc()).paginate(
            page=page,
            per_page=current_app.config['INDEX_PER_PAGE'],
            error_out=False
        )
    elif current_user.is_authenticated:
        # 加载登录后可见的文章
        # TODO 以及参与协作的文章
        pagination = blog_.posts.filter(Post._visibility <= 1).order_by(
            Post.published_at.desc()).paginate(
            page=page,
            per_page=current_app.config['INDEX_PER_PAGE'],
            error_out=False
        )
    else:
        # 加载公开的文章
        pagination = blog_.posts.filter(Post._visibility == 0).order_by(
            Post.published_at.desc()).paginate(
            page=page,
            per_page=current_app.config['INDEX_PER_PAGE'],
            error_out=False
        )
    if page > pagination.pages:
        return redirect(url_for('blog.blog_page', user_id=blog_.user.id, page=pagination.pages))
    return render_template('blog.html', blog=blog_,
                           pagination=pagination,
                           endpoint='blog.blog_page_plink',
                           blog_id=blog_.id
                           )