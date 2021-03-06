#!/usr/bin/env python3
# encoding: utf-8

from flask import Flask 
from config import configs 
from .models import db, User, Post, Blog, Category
from flask_moment import Moment
from flaskext.markdown import Markdown
from flask_pagedown import PageDown
from flask_login import LoginManager


moment = Moment()
pagedown = PageDown()


def register_filters(app):
    @app.template_filter()
    def simple_html_parser(text):
        lines = text.split('\n')
        new_text = ''
        for l in lines:
            new_text += '<p>{}</p>'.format(l)
        return new_text

    @app.template_filter()
    def long_string_cutter(long_string, max_length=20):
        """
        把长字符串按字符数剪短
        :param long_string: 待处理的字符串
        :param max_length: 最大长度
        :return: 处理后的字符串

        示例：
        example_str = '一二三四五六七八九十一二三四五六'
        {{ example_str  | long_string_cutter(12)}}
        返回值为
        '一二三四五六七八九十……'
        """
        if long_string is None:
            return ''
        if len(long_string) > max_length:
            return long_string[:max_length-2] + '…'
        else:
            return long_string

    @app.template_filter()
    def js_raw_escape(text):
        """
        把字符串中的 ` 替换为 \`
        :param text:
        :return:
        """
        return text.replace('`', '\`')

    @app.template_filter()
    def album_cover_url(album):
        """
        获得
        :param album:
        :return:
        """
        from rupa.models import Photo
        target = album.photos.order_by(Photo.created_at.desc()).first()
        if target:
            return target.url_thumb
        else:
            return ''

    @app.template_global()
    def sidebar_recent_users(lmt=9):
        # 最新用户
        return User.query.filter_by(role=User.ROLE_USER).order_by(User.created_at.desc()).limit(lmt).all()

    @app.template_global()
    def sidebar_recent_posts(blog=None, lmt=10):
        # 最新文章
        if blog is None:
            return Post.query.filter_by(_visibility=0).order_by(Post.published_at.desc()).limit(lmt).all()
        else:
            return blog.posts.filter_by(_visibility=0).order_by(Post.published_at.desc()).limit(lmt).all()

    @app.template_global()
    def sidebar_blog_categories(blog):
        if blog:
            return blog.categories.order_by(Category.created_at).all()


def register_extensions(app):
    db.init_app(app)
    moment.init_app(app)
    Markdown(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    pagedown.init_app(app)

    @login_manager.user_loader
    def user_loader(id):
        return User.query.get(id)

    login_manager.login_view = 'front.login'
    login_manager.login_message = '请登录后操作！'
    login_manager.login_message_category = "danger"


def register_blueprints(app):
    from .handlers import front, post, user, category, tag, dashboard, admin, blog, photo
    app.register_blueprint(front)
    app.register_blueprint(post)
    app.register_blueprint(user)
    app.register_blueprint(category)
    app.register_blueprint(tag)
    app.register_blueprint(dashboard)
    app.register_blueprint(admin)
    app.register_blueprint(blog)
    app.register_blueprint(photo)


def register_error_handlers(app):
    from .handlers import page_forbidden, page_not_found, internal_error, request_size_error
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(403, page_forbidden)
    app.register_error_handler(413, request_size_error)
    app.register_error_handler(500, internal_error)


def create_app(config):
    """
    Args: 
        config(str): 应用运行配置
    """
    app = Flask(__name__)
    app.config.from_object(configs.get(config))
    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_filters(app)

    return app 
