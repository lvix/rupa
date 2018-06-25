#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: test_models.py
@time: 18/5/16 7:56
"""

from rupa.models import User, Blog, Category, Post, Tag, Comment, Follow

class TestUser:
    """
    test User funtionality
    """
    def test_query(self, db, prepare_data):
        jack = User.query.filter_by(username='jack').first()
        assert jack.email == 'jack@123.com'
        assert jack.nickname == 'jacky'

        users = User.query.all()
        assert len(users) == 3

    def test_set_and_check_password(self, db, prepare_data):
        jack = User.query.filter_by(username='jack').first()

        assert jack.check_password('12345')
        assert jack.check_password('123') is not True

        jack.password = '23456'
        db.session.add(jack)
        db.session.commit()

        assert jack.check_password('23456')
        assert jack.check_password('12345') is not True

    def test_modification(self, db, prepare_data):
        jack = User.query.filter_by(username='jack').first()
        jack.nickname = 'jackjack'
        jack.introduction = 'jackintro'
        jack.email='jack123@123.com'
        db.session.add(jack)
        db.session.commit()

        jack = User.query.filter_by(username='jack').first()
        assert jack.nickname == 'jackjack'
        assert jack.introduction == 'jackintro'
        assert jack.email == 'jack123@123.com'

    def test_deleting_user_and_cascaded_objects(self, db, prepare_data):
        jack = User.query.filter_by(username='jack').first()

        assert Post.query.filter_by(blog=jack.blog).first() is not None
        assert Blog.query.count() == 1
        assert Post.query.count() == 2
        assert Category.query.count() == 2

        db.session.delete(jack)
        db.session.commit()

        assert User.query.count() == 2
        assert User.query.filter_by(username='jack').first() is None
        assert Blog.query.filter_by(user=jack).first() is None
        assert Post.query.count() == 0
        assert Category.query.count() == 0

    def test_deleting_blog_and_cascaded_objects(self, db, prepare_data):
        jack = User.query.filter_by(username='jack').first()
        assert Blog.query.count() == 1
        assert Category.query.count() == 2
        assert Post.query.count() == 2
        assert Comment.query.count() == 4

        db.session.delete(jack.blog)
        db.session.commit()

        assert Blog.query.filter_by(user=jack).first() is None
        assert Category.query.count() == 0
        assert Post.query.count() == 0
        assert Comment.query.count() == 0

    def test_deleting_category_and_cascaded_objects(self, db, prepare_data):

        assert Category.query.filter_by(name='cate1').first() is not None
        assert Category.query.count() == 2
        assert Post.query.filter_by(title='post1').first() is not None
        assert Comment.query.count() == 4

        cate1 = Category.query.filter_by(name='cate1').first()
        db.session.delete(cate1)
        db.session.commit()

        assert Category.query.filter_by(name='cate1').first() is None
        assert Post.query.filter_by(title='post1').first() is not None
        assert Category.query.count() == 1

    def test_deleting_post_and_cascaded_objects(self, db, prepare_data):

        assert Post.query.filter_by(title='post1').first() is not None
        assert Comment.query.count() == 4

        post1 = Post.query.filter_by(title='post1').first()
        db.session.delete(post1)
        db.session.commit()

        assert Post.query.filter_by(title='post1').first() is None
        assert Comment.query.count() == 0

    def test_deleting_comment(self, db, prepare_data):

        assert Comment.query.count() == 4

        comment2 = Comment.query.filter_by(text='comment2').first()
        db.session.delete(comment2)
        db.session.commit()

        assert Comment.query.count() == 1
        assert Comment.query.get(1) is not None
        assert Comment.query.get(2) is None
        assert Comment.query.get(3) is None
