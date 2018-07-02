#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: post.py
@time: 18/5/10 14:45
"""

from flask import Blueprint, url_for, render_template, redirect, request, flash
from flask_login import current_user
from rupa.models import db, Post

post = Blueprint('post', __name__, url_prefix='/post')


@post.route('/')
def post_list():
    """
    文章列表页面，跳转到首页
    :return:
    """
    return redirect(url_for('front.index'))


@post.route('/id/<int:post_id>/')
def post_page(post_id):
    """
    文章阅读页面
    :param post_id: 文章的id
    :return: 无
    """
    target = Post.query.get_or_404(post_id)
    # check permission
    if (target.visibility == 'self_only' and current_user != target.blog.user) or (
            target.visibility == 'member_only' and not current_user.is_authenticated) or (
            target.visibility == 'author_only' and (
            current_user != target.blog.user or current_user not in target.assist_writers)):
        flash('没有查看文章的权限', 'secondary')
        return redirect(url_for('front.index'))
    elif target.visibility == 'need_password':
        pass

    if target.permanent_link is not None:
        return redirect(url_for('post.post_page_permanent_link', permanent_link=target.permanent_link))
    target.views += 1
    db.session.add(target)
    db.session.commit()
    return render_template('post.html', post=target)


@post.route('/p/<permanent_link>/')
def post_page_permanent_link(permanent_link):
    """
    文章阅读页面，以永久链接访问
    :param permanent_link: 永久链接
    :return: 无
    """
    target = Post.query.filter_by(permanent_link=permanent_link).first_or_404()
    # check permission
    if (target.visibility == 'self_only' and current_user != target.blog.user) or (
            target.visibility == 'member_only' and not current_user.is_authenticated) or (
            target.visibility == 'author_only' and (
            current_user != target.blog.user or current_user not in target.assist_writers)):
        flash('没有查看文章的权限', 'secondary')
        return redirect(request.args.get('next') or
                        request.referrer or
                        url_for('front.index'))
    elif target.visibility == 'need_password':
        pass

    target.views += 1
    db.session.add(target)
    db.session.commit()
    return render_template('post.html', post=target)
