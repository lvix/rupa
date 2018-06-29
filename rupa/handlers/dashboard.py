#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: dashboard.py
@time: 18/5/10 16:41
"""
from flask import Blueprint, render_template, url_for, flash, current_app, redirect, request
from flask_login import current_user
from rupa.decorators import roles_required, blog_required
from rupa.models import db, User, Post, Blog, Notification, Message, Category, Album, Photo
from rupa.forms import PostForm, CateForm, ProfileForm, BlogInfoForm, PostUploadForm
from wtforms import BooleanField

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard.route('/')
@roles_required(User.ROLE_USER)
def index():
    # 最近发表
    recent_posts = None
    if current_user.blog:
        recent_posts = current_user.blog.posts.order_by(Post.published_at.desc()).limit(5).all()

    recent_notifications = current_user.notifibox.notifications.order_by(Notification.updated_at.desc()).limit(
        5).all()
    recent_messages = Message.query.filter_by(receiver=current_user).order_by(Message.updated_at.desc()).limit(5).all()
    return render_template('dashboard/index.html',
                           user=current_user,
                           recent_posts=recent_posts,
                           recent_messages=recent_messages,
                           recent_notifications=recent_notifications)


@dashboard.route('/blog/new/', methods=['GET', 'POST'])
@roles_required(User.ROLE_USER)
def blog_new():
    form = BlogInfoForm()
    if current_user.blog is not None:
        return redirect(url_for('dashboard.blog_info'))
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        if form.validate_on_submit():
            form.update_info()
            flash('创建成功，开始写第一篇博客吧！', 'success')
            return redirect(url_for('dashboard.post_new'))
        else:
            flash('创建失败', 'danger')
    return render_template('dashboard/blog_info.html',
                           user=current_user,
                           form=form, endpoint=url_for('dashboard.blog_new'),
                           page_title='创建博客')


@dashboard.route('/blog/info/', methods=['GET', 'POST'])
@blog_required()
@roles_required(User.ROLE_USER)
def blog_info():
    form = BlogInfoForm()
    if request.method == 'GET':
        form.load_info()
    elif request.method == 'POST':
        if form.validate_on_submit():
            form.update_info()
            flash('更新成功', 'success')
        else:
            flash('提交失败', 'danger')
    return render_template('dashboard/blog_info.html',
                           user=current_user,
                           form=form, endpoint=url_for('dashboard.blog_info'),
                           page_title='博客信息')


@dashboard.route('/post/')
@blog_required()
@roles_required(User.ROLE_USER)
def post():
    page = request.args.get('page', default=1, type=int)
    pagination = current_user.blog.posts.order_by(Post.published_at.desc()).paginate(
        page=page,
        per_page=current_app.config['INDEX_PER_PAGE'],
        error_out=False
        )
    if page > pagination.pages:
        return redirect(url_for('dashboard.post', page=pagination.pages))
    return render_template('dashboard/post_list.html', user=current_user,
                           pagination=pagination,
                           endpoint='dashboard.post'
                           )


@dashboard.route('/post/new', methods=['GET', 'POST'])
@blog_required()
@roles_required(User.ROLE_USER)
def post_new():
    form = gen_dynamic_form()
    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.status == User.STATUS_NORMAL and current_user.blog.status == Blog.STATUS_NORMAL:
                try:

                    target = form.update_post()
                    flash('发表成功', 'success')
                    return redirect(url_for('dashboard.post_edit', post_id=target.id))
                except Exception as e:
                    print(e)
                    flash('提交失败', 'danger')
                    db.session.rollback()
                    return render_template('dashboard/post_new.html', form=form)
            else:
                flash('现在无法发表', 'danger')
                return render_template('dashboard/post_new.html', form=form)
        else:
            flash('发表失败', 'danger')
            return render_template('dashboard/post_new.html', form=form)
    elif request.method == 'GET':
        return render_template('dashboard/post_new.html', form=form)


@dashboard.route('/post/delete/<int:post_id>', methods=['GET'])
@blog_required()
@roles_required(User.ROLE_USER)
def post_delete(post_id):
    target = current_user.blog.posts.filter_by(id=post_id).first()
    if target:
        try:
            title = target.title
            db.session.delete(target)
            db.session.commit()
            flash('成功删除文章 ' + title, 'success')
        except Exception as e:
            db.session.rollback()
            flash('操作失败', 'danger')
        return redirect(request.args.get('next') or
                        request.referrer or
                        url_for('dashboard.index'))
    else:
        flash('操作失败', 'danger')
        return redirect(url_for('dashboard.post'))


@dashboard.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
@blog_required()
@roles_required(User.ROLE_USER)
def post_edit(post_id):

    form = gen_dynamic_form()

    target = Post.query.get_or_404(post_id)
    if target.blog.user != current_user:
        return redirect('dashboard.index')

    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.status == User.STATUS_NORMAL and current_user.blog.status == Blog.STATUS_NORMAL:
                try:

                    form.update_post(target)

                    db.session.add(target)
                    db.session.commit()

                    flash('发表成功', 'success')
                    form = gen_dynamic_form()
                    form.load_post(target)
                    form.new_cate.data = ''
                    return render_template('dashboard/post_edit.html', form=form, post_id=target.id)
                except Exception as e:
                    print(e)
                    flash('提交失败', 'danger')
                    db.session.rollback()
                    return render_template('dashboard/post_edit.html', form=form, post_id=post_id)
            else:
                flash('现在无法发表', 'danger')
                return render_template('dashboard/post_edit.html', form=form, post_id=post_id)
        else:
            # print('验证失败')
            for field in form:
                if field.errors:
                    for error in field.errors:
                        print(error)
            flash('提交失败', 'danger')
            return render_template('dashboard/post_edit.html', form=form, post_id=post_id)

    elif request.method == 'GET':
        form.load_post(target)
    return render_template('dashboard/post_edit.html', form=form, post_id=post_id)


def gen_dynamic_form():
    # 动态生成表格
    class DynamicPostForm(PostForm):
        pass

    for cat in current_user.blog.categories:
        if not hasattr(DynamicPostForm, 'cate_' + cat.name):
            cate_field_ = BooleanField(cat.name)
            setattr(DynamicPostForm, 'cate_' + cat.name, cate_field_)

    form = DynamicPostForm()

    # 把分类的 Field 分组，渲染的时候方便操作
    for key in form.__dict__:
        if key[:5] == 'cate_':
            field_ = form.__dict__[key]
            form.category_fields[key] = field_

    return form


@dashboard.route('/post/upload/', methods=['GET', 'POST'])
@blog_required()
@roles_required(User.ROLE_USER)
def post_upload():
    form = PostUploadForm()
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        if form.validate_on_submit():
            try:
                post_uri = form.save_file()
                new_post = form.create_post(post_uri)
                # print(new_post)
                return redirect(url_for('dashboard.post_edit', post_id=new_post.id))
                flash('上传成功', 'success')
            except Exception as e:
                print(e)
                flash('上传失败', 'danger')
        else:
            flash('上传失败', 'danger')
            # for field in form:
            #     if field.errors:
            #         print(field)
            #         for e in field.errors:
            #             print(e)
    return render_template('dashboard/post_upload.html', form=form, file_accept='.md')


@dashboard.route('/category/')
@blog_required()
@roles_required(User.ROLE_USER)
def category():
    page = request.args.get('page', default=1, type=int)
    pagination = current_user.blog.categories.order_by(Category.updated_at.desc()).paginate(
        page=page,
        per_page=current_app.config['INDEX_PER_PAGE'],
        error_out=False
        )
    if page > pagination.pages:
        return redirect(url_for('dashboard.category', page=pagination.pages))
    return render_template('dashboard/category_list.html', user=current_user,
                           pagination=pagination,
                           endpoint='dashboard.category',
                           next_url=url_for('dashboard.category', page=page)
                           )


@dashboard.route('/category/new/')
@blog_required()
@roles_required(User.ROLE_USER)
def category_new():
    form = CateForm()
    if request.method == 'GET':
        return render_template('dashboard/category_edit.html', form=form)
    elif request.method == 'POST':
        form.update_cate()
        flash('分类修改成功', 'success')
        return redirect(request.args.get('next') or
                        request.referrer or
                        url_for('dashboard.category'))


@dashboard.route('/category/<int:cate_id>/delete/')
@blog_required()
@roles_required(User.ROLE_USER)
def category_delete(cate_id):
    target = current_user.blog.categories.filter_by(id=cate_id).first()
    if target:
        try:
            name = target.name
            db.session.delete(target)
            db.session.commit()
            flash('成功删除分类' + name, 'success')
        except Exception as e:
            db.session.rollback()
            flash('操作失败', 'danger')
        return redirect(request.args.get('next') or
                        request.referrer or
                        url_for('dashboard.category'))
    else:
        flash('操作失败', 'danger')
        return redirect(request.args.get('next') or
                        request.referrer or
                        url_for('dashboard.category'))


@dashboard.route('/category/<int:cate_id>/edit/', methods=['GET', 'POST'])
@blog_required()
@roles_required(User.ROLE_USER)
def category_edit(cate_id):

    target = current_user.blog.categories.filter_by(id=cate_id).first_or_404()
    form = CateForm()
    if request.method == 'GET':
        form.load_cate(target)
    elif request.method == 'POST':
        if form.validate_on_submit():
            form.update_cate(target)
            flash('分类修改成功', 'success')
            return redirect(request.args.get('next') or
                            request.referrer or
                            url_for('dashboard.category'))
        else:
            flash('修改失败', 'danger')
    return render_template('dashboard/category_edit.html', form=form,
                           user=current_user, cate_id=cate_id)


@dashboard.route('/<int:user_id>/profile_edit/', methods=['GET', 'POST'])
@roles_required(User.ROLE_USER)
def profile_edit(user_id):

    target = User.query.get_or_404(user_id)
    form = ProfileForm()

    if request.method == 'GET':
        form.load_info(target)
    elif request.method == 'POST':
        if form.validate_on_submit():
            if form.update_info(target):
                flash('更新成功', 'success')
            else:
                flash('更新失败', 'danger')
        else:
            flash('更新失败', 'danger')
            # for field in form:
            #     if field.errors:
            #         print(field)
            #         for e in field.errors:
            #             print(e)
    return render_template('dashboard/profile_edit.html', form=form)



