#!/usr/bin/env python
# encoding: utf-8


from ..common import class_utils

DEBUG = False

# REDIS
REDIS = class_utils.Config(
    host='redis',
    port=6379,
    password='',
    db=0,
)

# MYSQL
MYSQL = class_utils.Config(
    host='mysql',
    port='3306',
    user='root',
    password='',
    db='{project}',
)

RAVEN_CONFIG = {
    'dsn': '',
}
