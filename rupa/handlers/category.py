#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: category.py
@time: 18/5/11 4:56
"""

from flask import Blueprint, url_for, render_template, request, current_app
from rupa.models import db, Category, Post

category = Blueprint('category', __name__, url_prefix='/category')


@category.route('/<int:category_id>/')
def category_page(category_id):
    """
    分类的文章列表
    :param category_id: 分类的id
    :return:
    """
    page = request.args.get('page', default=1, type=int)
    category_ = Category.query.get_or_404(category_id)
    pagination = category_.posts.order_by(Post.published_at.desc()).paginate(
        page=page,
        per_page=current_app.config['INDEX_PER_PAGE'],
        error_out=False
    )
    return render_template('category.html',
                           category=category_,
                           pagination=pagination,
                           endpoint='category.category_page',
                           category_id=category_id)
