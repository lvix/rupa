#!/usr/bin/env python3
# encoding: utf-8

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('RUPA_SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INDEX_PER_PAGE = 16
    LIST_PER_PAGE = 20
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,
                                                                                                'data-dev.sqlite')
    UPLOADED_ICONS_DEST = '/rupa/static/debug_img/icons/'
    UPLOADED_MD_DEST = '/rupa/static/debug_img/mds/'
    UPLOADED_PHOTO_DEST = '/rupa/static/debug_img/upload_img/'
    # SQLALCHEMY_ECHO = True
    INVITE_REQUIRED = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,
                                                                                                'data-test.sqlite')


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRO_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    UPLOADED_ICONS_DEST = '/rupa/static/rupa_files/icons/'
    UPLOADED_MD_DEST = '/rupa/static/rupa_files/mds/'
    UPLOADED_PHOTO_DEST = '/rupa/static/rupa_files/photos/'
    INVITE_REQUIRED = True


configs = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
