#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: decorators.py
@time: 18/5/21 0:57
"""

from functools import wraps

from flask import abort, redirect, url_for
from flask_login import current_user

from rupa.models import User


def roles_required(*roles):
    """
    支持多个用户角色判断
    使用方式：
        @roles_required(User., User.ROLE_ADMIN)
        foo(*args, **kwargs)
            pass


    :param roles: User.ROLE_XX
    :return: roles_required 装饰器
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                # abort(404)
                return redirect(url_for('front.index'))
            return func(*args, **kwargs)
        return wrapper
    return decorator


def blog_required():
    """
    检查当前用户是否开通了博客，没有则跳往新建博客页面
    :return: blog_required 装饰器
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.blog is None:
                return redirect(url_for('dashboard.blog_new'))
            return func(*args, **kwargs)
        return wrapper
    return decorator
