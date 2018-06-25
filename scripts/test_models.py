#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: test_models.py
@time: 18/5/14 15:52
"""

from rupa.models import *

def init_db():
    db.drop_all()
    db.create_all()


def main():

    init_db()

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

    jack_blog = Blog(title='jack blog')
    jack.blog = jack_blog

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
        blog=jack.blog
    )

    post2 = Post(
        title='post2',
        blog=jack.blog
    )

    tag1 = Tag(
        name='tag1'
    )

    tag2 = Tag(
        name='tag2'
    )

    cate1.posts.append(post1)
    cate1.posts.append(post2)

    post1.tags.append(tag1)
    post1.tags.append(tag2)

    db.session.add(jack)
    db.session.add(jack_blog)
    db.session.add(cate1)
    db.session.add(post1)
    db.session.add(post2)
    db.session.add(tag1)
    db.session.add(tag2)
    db.session.commit()

    comment1 = Comment(
        post=post1,
        user=tom,
        text='comment1'
    )
    db.session.add(comment1)
    db.session.commit()

    comment2 = Comment(
        post=post1,
        user=adam,
        text='comment2',
    )
    comment2.parent = comment1
    db.session.add(comment2)
    db.session.commit()

    comment3 = Comment(
        post=post1,
        user=tom,
        text='comment3',
    )
    comment3.parent = comment2
    db.session.add(comment3)
    db.session.commit()

    comment4 = Comment(
        post=post1,
        user=jack,
        text='comment4',
    )
    comment4.parent = comment3
    db.session.add(comment4)
    db.session.commit()

    print(jack)
    print(tom)
    print(adam)
    print(jack.blog)
    print(jack.blog.categories.all())
    print(jack.blog.posts.all())
    print(post1.tags.all())
    print(post1.comments.all())

    db.session.delete(comment2)
    db.session.commit()
    print(post1.comments.all())

    f = Follow(follower=jack, followed=adam)
    db.session.add(f)
    db.session.commit()
    print(jack.followers.all())
    print(jack.followed.all())

    print(Comment.query.all())
    # db.session.delete(post1)
    # db.session.commit()
    # print(Comment.query.all())

    print(Post.query.all())
    print(Category.query.all())
    # db.session.delete(jack_blog)
    # print(Post.query.all())
    # print(Category.query.all())
    db.session.delete(jack)
    db.session.commit()
    print('')
    print(User.query.all())
    print(Blog.query.all())
    print(Category.query.all())
    print(Post.query.all())
    print(Tag.query.all())
    print(Comment.query.all())


if __name__ == '__main__':
    main()
