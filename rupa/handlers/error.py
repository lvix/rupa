#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: rupa
@file: error.py
@time: 18/7/5 6:24
"""

from flask import render_template


def page_not_found(e):
    return render_template('error.html', code=404), 404


def page_forbidden(e):
    return render_template('error.html', code=403), 403


def internal_error(e):
    return render_template('error.html', code=500), 500

