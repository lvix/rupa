#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: fixtures.py
@time: 18/5/16 5:56
"""

import pytest

from rupa.app import create_app
from rupa.models import db as database
from rupa.models import User, Blog, Category, Post, Tag, Comment


@pytest.fixture
def app():
    """
    flask app fixture
    :return:
    """
    return create_app('development')


@pytest.yield_fixture
def db(app):
    """
    create_all() before testing
    drop_all() after finishing
    :param app: app fixture created above
    :return:
    """
    with app.app_context():
        database.create_all()
        yield database
        database.drop_all()


@pytest.fixture
def prepare_data(db):
    """
    create some records in the db for testing
    :param db: db fixture
    :return:
    """
    jack = User(username='jack',
                email='jack@123.com',
                password='12345',
                nickname='jacky',
                introduction='I\'m jack')

    tom = User(username='tom',
                email='tom@123.com',
                password='12345',
                nickname='tommie',
                introduction='I\'m tom')

    adam = User(username='adam',
               email='adam@123.com',
               password='12345',
               nickname='adam',
               introduction='I\'m adam')

    jack_blog = Blog(title='jack blog', user=jack)

    cate1 = Category(
        name='cate1',
        blog=jack.blog
    )

    cate2 = Category(
        name='cate2',
        blog=jack.blog
    )

    jack.blog.categories.append(cate1)
    jack.blog.categories.append(cate2)

    post1 = Post(
        title='post1',
        blog=jack.blog,
    )

    post2 = Post(
        title='post2',
        blog=jack.blog,
    )

    tag1 = Tag(
        name='tag1'
    )

    tag2 = Tag(
        name='tag2'
    )

    comment1 = Comment(
        post=post1,
        user=tom,
        text='comment1'
    )

    comment2 = Comment(
        post=post1,
        user=adam,
        text='comment2',
    )
    comment2.parent = comment1

    comment3 = Comment(
        post=post1,
        user=tom,
        text='comment3',
    )
    comment3.parent = comment2

    comment4 = Comment(
        post=post1,
        user=jack,
        text='comment4',
    )
    comment4.parent = comment3

    cate1.posts.append(post1)
    cate1.posts.append(post2)

    post1.tags.append(tag1)
    post1.tags.append(tag2)

    db.session.add(jack)
    db.session.add(tom)
    db.session.add(adam)

    db.session.add(jack_blog)

    db.session.add(cate1)
    db.session.add(cate2)

    db.session.add(post1)
    db.session.add(post2)

    db.session.add(tag1)
    db.session.add(tag2)

    db.session.add(comment1)
    db.session.add(comment2)
    db.session.add(comment3)
    db.session.add(comment4)
    db.session.commit()
