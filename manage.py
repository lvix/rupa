#!/usr/bin/env python3
# encoding: utf-8

from rupa.app import create_app
import os 

rupa_config = os.environ.get('RUPA_CONFIG')
if rupa_config is None:
    rupa_config = 'development'

app = create_app(rupa_config)

if __name__ == '__main__':
    app.run()
