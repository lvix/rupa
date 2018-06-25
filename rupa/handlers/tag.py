#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: tag.py
@time: 18/5/11 4:56
"""

from flask import Blueprint, url_for, render_template, request, current_app
from rupa.models import db, Tag, Post

tag = Blueprint('tag', __name__, url_prefix='/tag')


@tag.route('/<int:tag_id>')
def tag_page(tag_id):
    """
    标签的文章列表
    :param tag_id: 分类的id
    :return:
    """
    page = request.args.get('page', default=1, type=int)
    tag_ = Tag.query.get_or_404(tag_id)
    pagination = tag_.posts.order_by(Post.published_at.desc()).paginate(
        page=page,
        per_page=current_app.config['INDEX_PER_PAGE'],
        error_out=False
    )
    return render_template('tag.html',
                           tag=tag_,
                           pagination=pagination,
                           endpoint='tag.tag_page',
                           tag_id=tag_id)
