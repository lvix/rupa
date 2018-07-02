#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: front.py
@time: 18/5/9 7:42
"""

from flask import Blueprint, render_template, url_for, flash, request, current_app, redirect, make_response, session
from rupa.models import Post, User
from rupa.forms import LoginForm, RegisterForm
from flask_login import login_user, logout_user, login_required, current_user

from rupa.tools import Captcha
from io import BytesIO

front = Blueprint('front', __name__)


@front.route('/')
def index():
    page = request.args.get('page', default=1, type=int)
    # 文章列表
    pagination = Post.query.filter(Post._password == None,
                                   Post._visibility == Post.VISIBILITY_OPTIONS['public'],
                                   Post.status == Post.STATUS_PUBLISHED).order_by(
        Post.published_at.desc()).paginate(
        page=page,
        per_page=current_app.config['INDEX_PER_PAGE'],
        error_out=False
    )

    return render_template('index.html',
                           page=page,
                           pagination=pagination,
                           endpoint='front.index')


@front.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('front.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.status == User.STATUS_NORMAL:
            login_user(user, form.remember_me.data)
            user.update_login_info(request)
            flash('欢迎回来，{}'.format(user.username), 'success')
            return redirect(request.args.get('next') or
                            request.referrer or
                            url_for('front.index'))
        else:
            flash('登录失败，该账号已被停用', 'danger')
    else:
        for field in form:
            if field.errors:
                flash('登录失败', 'danger')
                break
    return render_template('login.html', form=form)


@front.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('您已退出登录', 'success')
    return redirect(request.args.get('next') or
                    request.referrer or
                    url_for('front.index'))


@front.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('front.index'))

    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = form.register_user()
            if new_user is None:
                flash('注册失败', 'secondary')
            flash('注册成功', 'success')

            login_user(new_user, 1)
            return redirect(url_for('dashboard.profile_edit'))
        else:
            flash('提交失败', 'secondary')
    elif request.method == 'GET':
        pass
    return render_template('register.html', form=form)


@front.route('/captcha/')
def get_captcha():
    cap = Captcha()
    image, word = cap.gen_captcha()
    # 将验证码图片以二进制形式写入在内存中，防止将图片都放在文件夹中，占用大量磁盘
    buf = BytesIO()
    image.save(buf, 'gif')
    buf_content = buf.getvalue()
    # 把二进制作为response发回前端，并设置首部字段
    response = make_response(buf_content)
    response.headers['Content-Type'] = 'image/gif'
    # 将验证码字符串储存在session中
    session['captcha_word'] = word
    return response
