#!/usr/bin/env python3
# encoding: utf-8

import hashlib
import os
import random
import re
from datetime import datetime, timedelta

from PIL import Image
from flask import url_for, current_app
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# assist_writers
user_post_assist = db.Table('user_post_assist',
                            db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
                            db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                            )

category_post = db.Table('category_post',
                         db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
                         db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
                         )

tag_post = db.Table('tag_post',
                    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
                    )


class Base(db.Model):
    __abstract__ = True
    created_at = db.Column(db.DateTime, default=datetime.utcnow(), )
    updated_at = db.Column(db.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())


class Follow(Base):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)


class User(Base, UserMixin):
    __tablename__ = 'user'

    ROLE_ADMIN = 'ADMIN'
    ROLE_USER = 'USER'

    STATUS_NORMAL = 0
    STATUS_SUSPENDED = 1
    STATUS_NOT_ACTIVATED = 2

    DEFAULT_ICON = None  # url_for('static', filename='icon/default_icon.png')

    # 性别
    GENDER_NULL = 0
    GENDER_M = 1
    GENDER_F = 2

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, index=True, nullable=False)
    role = db.Column(db.String(8), default=ROLE_USER, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    _password = db.Column('password', db.String(256), nullable=False)
    status = db.Column(db.SmallInteger, default=STATUS_NORMAL)

    nickname = db.Column(db.String(24), nullable=False, default='no_name')

    introduction = db.Column(db.String(256))

    gender = db.Column(db.SmallInteger, default=GENDER_NULL)
    country = db.Column(db.String(10))
    province = db.Column(db.String(10))
    city = db.Column(db.String(10))

    # relationship
    icon = db.relationship('Icon', uselist=False, backref=db.backref('user'))
    invitation_code = db.relationship('InvitationCode', uselist=False, backref='user')
    blog = db.relationship('Blog', uselist=False, backref='user', cascade='all, delete-orphan')
    albums = db.relationship('Album', backref='user', cascade='all, delete-orphan')
    notifibox = db.relationship('Notifibox', uselist=False, backref='user', cascade='all, delete-orphan')
    microblog = db.relationship('MicroBlog', uselist=False, backref='user', cascade='all, delete-orphan')
    messagebox = db.relationship('MessageBox', uselist=False, backref='user', cascade='all, delete-orphan')

    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    current_login_ip = db.Column(db.String(32))
    last_login_ip = db.Column(db.String(32))

    current_login_time = db.Column(db.DateTime, default=datetime.utcnow())
    last_login_time = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<User {}: {}>'.format(self.id, self.username)

    @property
    def password(self):
        # return self._password
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, orig_password):
        self._password = generate_password_hash(orig_password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def is_writer(self):
        return self.role == self.ROLE_WRITER

    def is_user(self):
        return self.role == self.ROLE_USER

    def follow(self, user):
        if not self.is_following(user) and user.id != self.id:
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def update_login_info(self, req):
        self.last_login_ip = self.current_login_ip
        self.last_login_time = self.current_login_time

        self.current_login_ip = req.remote_addr
        self.current_login_time = datetime.utcnow()


class Album(Base):
    __tablename__ = 'album'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    photos = db.relationship('Photo', lazy='dynamic', backref=db.backref('album'),
                             cascade='all, delete-orphan')

    def __repr__(self):
        return '<Album {} of User {}>'.format(self.id, self.user_id)


class InvitationCode(Base):
    __tablename__ = 'invitation_code'

    STATUS_NORMAL = 0
    STATUS_USED = 1
    STATUS_EXPIRED = 2

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code = db.Column(db.String(24), unique=True, nullable=False)
    status = db.Column(db.SmallInteger, default=STATUS_NORMAL)
    expired_time = db.Column(db.DateTime)

    def __init__(self):
        super().__init__()
        self.code = ''.join([chr(65 + random.randint(0, 25)) for i in range(24)])
        self.expired_time = datetime.utcnow() + timedelta(days=90)

    def __repr__(self):
        return '<Invitation Code {}: {}>'.format(id, self.code)


class Blog(Base):
    STATUS_NORMAL = 0
    STATUS_SUSPENDED = 1

    __tablename__ = 'blog'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(256), default='No Title')
    description = db.Column(db.String(256))
    password = db.Column(db.String(256))

    status = db.Column(db.SmallInteger, default=STATUS_NORMAL)

    categories = db.relationship('Category', lazy='dynamic', backref=db.backref('blog'), cascade='all, delete-orphan')
    posts = db.relationship('Post', lazy='dynamic', backref=db.backref('blog'), cascade='all, delete-orphan')

    def __repr__(self):
        return '<Blog {} of User {}: {}>'.format(self.id, self.user_id, self.title[:15])

    @property
    def category_choices(self):
        return [(cate.id, cate.name) for cate in self.categories]


class Category(Base):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), default='No Title', nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)
    posts = db.relationship('Post', secondary=category_post, lazy='dynamic',
                            backref=db.backref('categories', lazy='dynamic'))

    def __repr__(self):
        return '<Category {}: {}>'.format(self.id, self.name)


class Post(Base):
    __tablename__ = 'post'

    VISIBILITY_OPTIONS = {
        'public': 0,
        'member_only': 1,
        'author_only': 2,
        'need_password': 3,
        'self_only': 4,
    }
    VISIBILITY_OPTIONS_R = {v: k for k, v in VISIBILITY_OPTIONS.items()}

    STATUS_DRAFT = 2
    STATUS_PUBLISHED = 0
    STATUS_SUSPENDED = 1

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), default='No Title')
    text = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=STATUS_PUBLISHED, nullable=False)
    # 摘要
    intro_photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    abstract = db.Column(db.String(240))
    # 永久链接
    permanent_link = db.Column(db.String(64), unique=True)

    # views
    views = db.Column(db.Integer, default=0, nullable=False)
    likes = db.Column(db.Integer, default=0, nullable=False)
    _password = db.Column(db.String(24), default=None)
    _visibility = db.Column(db.SmallInteger, default=VISIBILITY_OPTIONS['public'], nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow, )

    # relationship
    # blog  上文 backref 定义
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)
    # categories 上文 backref 定义
    # 其他作者
    assist_writers = db.relationship('User', secondary=user_post_assist, lazy='dynamic',
                                     backref=db.backref('posts', lazy='dynamic'))

    tags = db.relationship('Tag', secondary=tag_post, lazy='joined',
                           backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return '<Post {}: {}>'.format(self.id, self.title[:15])

    @property
    def visibility(self):
        return self.VISIBILITY_OPTIONS_R.get(self._visibility, 0)

    @visibility.setter
    def visibility(self, visibility):
        """
            设置文章允许被所有人查看
            Args:
                visibility(str):
                    'public': 文章所有人可见
                    'member_only': 仅会员登录后可见
                    'author_only': 仅参与的作者可见
                    'need_password': 输入密码后可见
                    'self_only': 仅自己可见
            Returns:
                None
        """
        vi = self.VISIBILITY_OPTIONS.get(visibility, None)
        if vi:
            self._visibility = vi

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, orig_password):
        self._password = orig_password

    def check_password(self, password):
        return self._password == password

    def gen_abstract(self):
        self.abstract = self.text.split('\n')[0]

    @property
    def get_link(self):
        if self.permanent_link:
            return url_for('post.post_page_permanent_link', permanent_link=self.permanent_link)
        else:
            return url_for('post.post_page', post_id=self.id)


class Tag(Base):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, default='No Title', nullable=False)

    def __repr__(self):
        return '<Tag {}: {}>'.format(self.id, self.name)


class Comment(Base):
    __tablename = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'))

    text = db.Column(db.String(240))
    likes = db.Column(db.Integer, default=0, nullable=False)
    dislikes = db.Column(db.Integer, default=0, nullable=False)

    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic',
                                                      single_parent=True,
                                                      cascade='all, delete-orphan')
                           )
    post = db.relationship('Post', backref=db.backref('comments', lazy='dynamic',
                                                      single_parent=True,
                                                      cascade='all, delete-orphan')
                           )

    parent = db.relationship('Comment', remote_side=[id])
    children = db.relationship('Comment', single_parent=True, cascade='all, delete-orphan')

    def __repr__(self):
        return '<comment {}, user {}, post {}, parent {}>'.format(self.id, self.user.id, self.post.id, self.parent_id)


class Notifibox(Base):
    __tablename__ = 'notifibox'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    notifications = db.relationship('Notification', lazy='dynamic', backref=db.backref('notifibox'),
                                    cascade='all, delete-orphan')

    def __repr__(self):
        return '<Notifbox {} of User {}>'.format(self.id, self.user_id)


class Notification(Base):
    __tablename__ = 'notification'

    STATUS_UNREAD = 0
    STATUS_READ = 1
    id = db.Column(db.Integer, primary_key=True)
    notifibox_id = db.Column(db.Integer, db.ForeignKey('notifibox.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.SmallInteger, default=STATUS_UNREAD, nullable=False)
    text = db.Column(db.String(1024))

    def __repr__(self):
        return '<Notification {} in box {}>'.format(self.id, self.notifbox_id)


class MicroBlog(Base):
    __tablename__ = 'microblog'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    micromessages = db.relationship('MicroMessage', lazy='dynamic', backref=db.backref('microblog'),
                                    cascade='all, delete-orphan')

    def __repr__(self):
        return '<Notifbox {} of User {}>'.format(self.id, self.user_id)


class MicroMessage(Base):
    __tablename__ = 'micromessage'

    STATUS_PUBLISHED = 0
    STATUS_SUSPENDED = 1

    VISIBILITY_EVERYONE = 0
    VISIBILITY_FRIENDS_ONLY = 1
    VISIBILITY_SELF_ONLY = 2

    TYPE_NORMAL = 0
    TYPE_REBLOG = 1

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer, default=0, nullable=False)
    visibility = db.Column(db.Integer, default=0, nullable=False)
    type = db.Column(db.Integer, default=0, nullable=False)

    text = db.Column(db.String(140))
    views = db.Column(db.Integer, default=0, nullable=False)
    likes = db.Column(db.Integer, default=0, nullable=False)

    microblog_id = db.Column(db.Integer, db.ForeignKey('microblog.id', ondelete='CASCADE'), nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey('micromessage.id'))  # ondelete='CASCADE'))
    parent = db.relationship('MicroMessage', remote_side=[id])
    children = db.relationship('MicroMessage', single_parent=True)  # , cascade='all, delete-orphan')

    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    photo = db.relationship('Photo')


# class File(Base):
#     pass

class Photo(Base):
    __tablename__ = 'photo'

    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id', ondelete='CASCADE'), nullable=False)
    image_name = db.Column(db.String, index=True)
    image_dir = db.Column(db.String)
    thumb_name = db.Column(db.String)
    thumb_dir = db.Column(db.String)

    posts_intro = db.relationship('Post', backref='intro_photo')

    def __repr__(self):
        return '<Photo {}: {}>'.format(self.id, self.image_name)

    @property
    def full_path(self):
        return self.image_dir + self.image_name

    @property
    def full_path_thumb(self):
        return self.thumb_dir + self.thumb_name

    @property
    def url(self):
        # print(self.image_name)
        return url_for('photo.photo_get', filename=self.image_name)

    @property
    def url_thumb(self):
        return url_for('photo.photo_thumb', filename=self.thumb_name)


class Icon(Base):
    __tablename__ = 'icon'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    image_name = db.Column(db.String, index=True)
    image_dir = db.Column(db.String)

    def __repr__(self):
        return '<Icon {}: {}>'.format(self.id, self.image_name)

    def full_path(self, size):
        return self.image_dir + self.image_name + 'x{}.png'.format(size)

    @property
    def url(self):
        if self.image_name:
            return url_for('photo.icon_get',
                           filename=self.image_name)
        else:
            return url_for('static', filename='icon/default_icon.png')

    def update_icon(self, field_data):
        """
        把表单中的 Field 数据写入自身的属性
        :param field_data: 表单field
        :return: 无
        """

        if field_data is None:
            return

        sizes = [400, 200, 128, 64, 32]

        prev_image_dir = self.image_dir
        prev_image_name = self.image_name

        fmt = field_data.filename.split('.')[-1].lower()
        img_name = hashlib.md5((fmt + datetime.utcnow().strftime('%Y%m%d%H%M%S%f') + fmt).encode('utf-8')).hexdigest()
        img_dir = current_app.config['UPLOADED_ICONS_DEST']

        try:
            img = Image.open(field_data)
            img = img.convert('RGB')

            w = img.width
            h = img.height

            if w > h:
                x0, y0 = (w - h) / 2, 0
                x1, y1 = x0 + h, y0 + h
            else:
                x0, y0 = 0, (h - w) / 2
                x1, y1 = x0 + w, y0 + w
            img = img.crop((x0, y0, x1, y1))

            for size in sizes:
                img = img.resize((size, size))
                img_path = os.getcwd() + img_dir + img_name + 'x{}.png'.format(size)
                img.save(img_path, 'png')

            self.image_dir = img_dir
            self.image_name = img_name

            db.session.add(self)
            db.session.commit()

            # 删除原先的文件
            self.delete_images(prev_image_dir, prev_image_name)
        except Exception as e:
            db.session.rollback()
            raise e

    def delete_images(self, im_dir, im_name):
        if im_dir is None:
            return
        target_dir = os.getcwd() + im_dir
        for item in filter(lambda x: re.compile(r'^{}.*?png$'.format(im_name)).match(x), os.listdir(target_dir)):
            file_path = target_dir + item
            if os.path.isfile(file_path):
                os.remove(file_path)


messagebox_dialog = db.Table('messagebox_dialog',
                             db.Column('messagebox_id', db.Integer, db.ForeignKey('messagebox.id'), primary_key=True),
                             db.Column('messagedialog_id', db.Integer, db.ForeignKey('messagedialog.id'),
                                       primary_key=True),
                             )


class MessageBox(Base):
    __tablename__ = 'messagebox'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    dialogs = db.relationship('MessageDialog', secondary=messagebox_dialog, lazy='joined',
                              backref=db.backref('messageboxes'),
                              single_parent=True,
                              cascade='all, delete-orphan')

    def __repr__(self):
        return '<MessageBox {} of User {}>'.format(self.id, self.user_id)

    def open_dialog(self, receiver):
        dial = None
        for d in self.dialogs:
            if receiver.messagebox in d.messageboxes:
                dial = d
        if dial is None:
            dial = MessageDialog()
            dial.messageboxes.append(self)
            dial.messageboxes.append(receiver.messagebox)
            db.session.add(dial)
        return dial


class MessageDialog(Base):
    __tablename__ = 'messagedialog'
    id = db.Column(db.Integer, primary_key=True)
    messages = db.relationship('Message', lazy='dynamic', backref=db.backref('messagedialog'),
                               single_parent=True,
                               cascade='all, delete-orphan')


class Message(Base):
    TYPE_NORMAL = 0
    TYPE_REBLOG = 1

    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    dialog_id = db.Column(db.Integer, db.ForeignKey('messagedialog.id', ondelete='CASCADE'), nullable=False)

    sender_id = db.Column(db.Integer, db.ForeignKey('messagebox.id', ondelete='CASCADE'), nullable=False)
    sender = db.relationship('MessageBox', lazy='joined', foreign_keys=[sender_id], uselist=False,
                             backref=db.backref('sent_messages'))

    receiver_id = db.Column(db.Integer, db.ForeignKey('messagebox.id', ondelete='CASCADE'), nullable=False)
    receiver = db.relationship('MessageBox', lazy='joined', foreign_keys=[receiver_id], uselist=False,
                               backref=db.backref('received_messages'))

    type = db.Column(db.Integer, default=0, nullable=False)
    text = db.Column(db.String(2048))

    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))
    post = db.relationship('Post', lazy='joined', uselist=False)

    micromessage_id = db.Column(db.Integer, db.ForeignKey('micromessage.id', ondelete='CASCADE'))
    micromessage = db.relationship('MicroMessage', lazy='joined', uselist=False)
