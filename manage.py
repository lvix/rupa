#!/usr/bin/env python3
# encoding: utf-8

from rupa.app import create_app
from rupa.models import db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

import os

rupa_config = os.environ.get('FLASK_ENV')
# if rupa_config is None:
#     rupa_config = 'development'

app = create_app(rupa_config)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
