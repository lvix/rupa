#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: Rupa
@file: generate_testing_data.py
@time: 18/5/9 15:22
"""

from rupa.models import *
from faker import Faker
import random
from datetime import datetime


fake = Faker()


def fake_datetime():
    dtstr = fake.date() + ' ' + fake.time()
    return datetime.strptime(dtstr, '%Y-%m-%d %H:%M:%S')


def gen_db_data():

    db.drop_all()
    db.create_all()

    # 创建一堆邀请码
    for i in range(100):
        while True:
            code = InvitationCode()
            if InvitationCode.query.filter_by(code=code.code).first() is None:
                break
        db.session.add(code)
    db.session.commit()


    # 创建 admin
    admin = User(username='admin',
                 nickname='admin',
                 email='admin@lvix.me',
                 password='qwerty123',
                 role=User.ROLE_ADMIN,
                 )
    db.session.add(admin)


    # 创建10个用户

    all_users = []
    test_users = []
    for i in range(10):
        fake_name = fake.name()
        username = fake_name.split()[0].lower() + str(random.randint(10, 99))
        new_user = User(username=username[:16],
                        nickname=fake_name[:24],
                        email=username + '@lvix.me',
                        password='qwerty123!@#$%',
                        role=User.ROLE_USER,
        )
        db.session.add(new_user)
        if len(test_users) < 5:
            test_users.append(new_user)
        all_users.append(new_user)
    db.session.commit()

    # 用户之间互相加好友
    # for user in test_users:
    #     for i in range(random.randint(3, 7)):
    #         while True:
    #             selected_user = random.choice(test_users)
    #             if selected_user != user and not user.is_following(selected_user):
    #                 break
    #         user.follow(selected_user)
    #     db.session.add(user)
    for i in range(5):
        user = test_users[i]
        user.follow(all_users[i + 2])
        user.follow(all_users[i + 3])
        user.follow(all_users[i + 4])
        db.session.add(user)
    db.session.commit()

    # 为所有用户创建通知、微博、私信
    for user in all_users:
        new_notifbox = Notifibox(user=user)
        new_microblog = MicroBlog(user=user)
        new_messagebox = MessageBox(user=user)
        new_album = Album(name='默认相册', user=user)
        new_icon = Icon(user=user)
        db.session.add(new_notifbox)
        db.session.add(new_microblog)
        db.session.add(new_messagebox)
        db.session.add(new_album)
        db.session.add(new_icon)
    db.session.commit()

    # 给所有用户发送一个欢迎消息
    for user in all_users:
        new_notification = Notification(notifibox=user.notifibox, text='Welcome to lvix.me, {}.'.format(user.nickname))
        user.notifibox.notifications.append(new_notification)
        db.session.add(new_notification)
    db.session.commit()

    # 所有用户发送 1~3 条微博
    test_micromessages = []
    for user in all_users:
        for i in range(random.randint(1, 4)):
            if random.randint(0, 1) == 1 and len(test_micromessages) > 1:
                chosen_micromsg = random.choice(test_micromessages)
                new_micromessage = MicroMessage(microblog=user.microblog, type=MicroMessage.TYPE_REBLOG,
                                                parent=chosen_micromsg)
            else:
                new_micromessage = MicroMessage(microblog=user.microblog, text='a micromessage from ' + user.nickname)
            test_micromessages.append(new_micromessage)
            db.session.add(new_micromessage)
    db.session.commit()

    # 用户互发私信
    for user in all_users:
        for i in range(random.randint(1, 5)):
            while True:
                chosen_user = random.choice(all_users)
                if chosen_user != user:
                    break
            dialog = user.messagebox.open_dialog(chosen_user)
            new_msg = Message(sender=user.messagebox, receiver=chosen_user.messagebox,
                              messagedialog=dialog,
                              text='hello, ' + chosen_user.nickname)
            db.session.add(new_msg)
        db.session.commit()

    test_tags = []
    # 创建 tag
    for i in range(20):
        while True:
            name = fake.word()
            if Tag.query.filter_by(name=name).first() is None:
                break
        new_tag = Tag(name=name)
        db.session.add(new_tag)
        test_tags.append(new_tag)
    db.session.commit()

    # 为5个用户创建博客
    test_blogs = []
    test_categories = []
    for user in test_users:
        blog = Blog(user=user,
                    title=user.nickname + '\'s blog',
                    description='this is {}\'s blog'.format(user.nickname),
                    )

        # 创建分类
        for i in range(5):
            name = fake.word()
            new_category = Category(name=name, blog=blog)
            db.session.add(new_category)
            test_categories.append(new_category)

        db.session.add(blog)
        test_blogs.append(blog)

    db.session.commit()

    # 创建 Photo 对象
    import re
    photo_path = 'C:\\Users\\hanch\\Desktop\\Rupa\\rupa\\static\\debug_img\\upload_img\\'
    photo_files = os.listdir(photo_path)
    photo_thumbs = list(filter(lambda x: re.compile('^.*?x120\.(jpg|jpeg|gif|png)$').match(x), photo_files))
    photo_files = list(set(photo_files) - set(photo_thumbs))

    for i in range(len(test_users)):
        user = test_users[i]
        album = user.albums[0]
        photo_name = photo_files[i]
        photo_thumb = photo_name.split('.')[0] + 'x120.' + photo_name.split('.')[1]
        new_photo = Photo(album=album,
                          image_name=photo_name,
                          thumb_name=photo_thumb,
                          image_dir='/rupa/static/debug_img/upload_img/',
                          thumb_dir='/rupa/static/debug_img/upload_img/',
                          )
        db.session.add(new_photo)
        db.session.commit()

    # 创建文章
    for blog in test_blogs:
        for cate in blog.categories:
            for i in range(random.randint(1, 5)):
                title = fake.sentence(5)
                permanent_link = '-'.join(title.replace('.', '').lower().split())
                # 文章内容
                text = ''
                for j in range(1, 100):
                    text += fake.sentence()
                    if random.randint(0, 10) < 1:
                        text += '\n'
                    else:
                        text += ' '

                new_post = Post(title=title,
                                text=text,
                                published_at=fake_datetime(),
                                views=random.randint(1, 5000000),
                                likes=random.randint(1, 5000000),
                                permanent_link=permanent_link,
                                blog=blog
                                )

                new_post.intro_photo = blog.user.albums[0].photos[0]
                new_post.gen_abstract()
                new_post.categories.append(cate)
                writers = []
                writer_num = random.randint(0, 3)
                while len(writers) < writer_num:
                    chosen_writer = random.choice(test_users)
                    if chosen_writer not in writers:
                        writers.append(chosen_writer)
                new_post.writers = writers

                chosen_tags = []
                for j in range(random.randint(1, 4)):
                    chosen_tag = random.choice(test_tags)
                    if chosen_tag not in chosen_tags:
                        chosen_tags.append(chosen_tag)
                new_post.tags = chosen_tags
                db.session.add(new_post)

                # 添加评论
                comments = []
                for j in range(1, 10):
                    user = random.choice(test_users)
                    text = fake.sentence()
                    post = new_post
                    parent = None
                    if len(comments) > 0 and random.randint(0, 1) == 1:
                        parent = random.choice(comments)
                    new_comment = Comment(user=user,
                                          text=text,
                                          likes=random.randint(1, 50),
                                          dislikes=random.randint(1, 50),
                                          post=post,
                                          parent=parent
                                          )
                    comments.append(new_comment)
                    db.session.add(new_comment)
                db.session.commit()

    db.session.commit()


if __name__ == '__main__':
    gen_db_data()
