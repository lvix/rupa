#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: admin.py
@time: 18/5/21 0:33
"""
from flask import Blueprint, render_template, url_for, flash, current_app, redirect, request
from flask_login import current_user
from rupa.decorators import roles_required
from rupa.models import db, User, Post, Blog, Notification, Message, Category, InvitationCode
from rupa.forms import AdminUserForm


admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('/')
@roles_required(User.ROLE_ADMIN)
def index():
    recent_users = User.query.order_by(User.created_at).limit(5).all()
    recent_posts = Post.query.order_by(Post.updated_at.desc()).limit(5).all()
    return render_template('admin/index.html',
                           user=current_user,
                           recent_users=recent_users,
                           recent_posts=recent_posts,
                           )


@admin.route('/user/')
@roles_required(User.ROLE_ADMIN)
def user_list():
    return render_list(User, User.created_at, 'admin.user_list', 'admin/user_list.html')


@admin.route('/user/edit/<int:user_id>/', methods=['GET', 'POST'])
@roles_required(User.ROLE_ADMIN)
def user_edit(user_id):
    if user_id == 1:
        return redirect(url_for('admin.user_list'))
    form = AdminUserForm()
    user = User.query.get_or_404(user_id)
    if request.method == 'GET':
        form.load_user(user)
        return render_template('admin/user_edit.html', form=form, user=user)
    elif request.method == 'POST':
        # form.username.data = user.username
        # form.email.data = user.email
        if form.validate_on_submit():
            try:
                form.update_user(user)
                flash('更新成功', 'success')
            except Exception as e:
                flash('用户信息更新失败', 'danger')
                print(e)
        else:
            for field in form:
                if field.errors:
                    print(field)
                    for error in field.errors:
                        print(error)
        return render_template('admin/user_edit.html', form=form, user=user)


@admin.route('/user/delete/<int:user_id>/')
@roles_required(User.ROLE_ADMIN)
def user_delete(user_id):
    return delete_target(User, user_id, '用户')


@admin.route('/blog/')
@roles_required(User.ROLE_ADMIN)
def blog_list():
    return render_list(Blog, Blog.updated_at, 'admin.blog_list', 'admin/blog_list.html')


@admin.route('/user/change_status/<int:blog_id>/')
@roles_required(User.ROLE_ADMIN)
def blog_change_status(blog_id):
    target = Blog.query.get_or_404(blog_id)
    try:
        if target.status == target.STATUS_NORMAL:
            target.status = target.STATUS_SUSPENDED
        else:
            target.status = target.STATUS_NORMAL
        db.session.add(target)
        flash('修改博客 {} 状态成功'.format(blog_id), 'success')
    except:
        db.session.rollback()
        flash('修改博客 {} 状态失败'.format(blog_id), 'danger')
    return redirect(request.args.get('next') or
                    request.referrer or
                    url_for('admin.index'))


@admin.route('/user/delete/<int:blog_id>/')
@roles_required(User.ROLE_ADMIN)
def blog_delete(blog_id):
    return delete_target(Blog, blog_id, '博客')


@admin.route('/post/')
@roles_required(User.ROLE_ADMIN)
def post_list():
    return render_list(Post, Post.created_at, 'admin.post_list', 'admin/post_list.html')


@admin.route('/post/change_status/<int:post_id>/')
@roles_required(User.ROLE_ADMIN)
def post_change_status(post_id):
    target = Post.query.get_or_404(post_id)
    try:
        if target.status == target.STATUS_PUBLISHED:
            target.status = target.STATUS_SUSPENDED
        elif target.status == target.STATUS_SUSPENDED:
            target.status = target.STATUS_PUBLISHED
        db.session.add(target)
        flash('修改文章 {} 状态成功'.format(post_id), 'success')
    except:
        db.session.rollback()
        flash('修改文章 {} 状态失败'.format(post_id), 'danger')
    return redirect(request.args.get('next') or
                    request.referrer or
                    url_for('admin.index'))


@admin.route('/post/delete/<int:post_id>/')
@roles_required(User.ROLE_ADMIN)
def post_delete(post_id):
    return delete_target(Post, post_id, '文章')


@admin.route('/invitation_codes/')
@roles_required(User.ROLE_ADMIN)
def invitation_codes():
    return render_list(InvitationCode, InvitationCode.created_at, 'admin.invitation_codes', 'admin/invitation_list.html')

@admin.route('/invitation_codes/delete/<code_id>')
@roles_required(User.ROLE_ADMIN)
def invitation_codes_delete(code_id):
    return delete_target(InvitationCode, code_id, '邀请码')


def render_list(db_obj, order_attr, endpoint, template):
    page = request.args.get('page', default=1, type=int)
    pagination = db_obj.query.order_by(order_attr.desc()).paginate(
        page=page,
        per_page=current_app.config['INDEX_PER_PAGE'],
        error_out=False
        )
    if page > pagination.pages:
        return redirect(url_for(endpoint, page=pagination.pages))
    return render_template(template, user=current_user,
                           pagination=pagination,
                           endpoint=endpoint
                           )


def delete_target(db_obj, target_id, flash_word=''):
    target = db_obj.query.get_or_404(target_id)
    print(target)
    try:
        db.session.delete(target)
        db.session.commit()
        flash('删除{} {} 成功'.format(flash_word, target_id), 'success')
    except Exception as e:
        print(e)
        db.session.rollback()
        flash('删除{} {}失败'.format(flash_word, target_id), 'danger')
    return redirect(request.args.get('next') or
                    request.referrer or
                    url_for('admin.index'))


