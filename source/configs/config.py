#!/usr/bin/env python
# coding=utf-8

import os
import logging

from ..common import class_utils


DEBUG = True

ENV = os.getenv('ENV', 'dev')
LOG_LEVEL = logging.DEBUG


RAVEN_CONFIG = {}

ALLOWED_HOSTS = ['*']


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

try:
    if ENV == 'test':
        from .test_config import *  # noqa
    elif ENV == 'pro':
        from .pro_config import *  # noqa
except Exception as e:
    print '*** Import env config failed ***'
    print str(e)

try:
    from .local_config import *  # noqa
except Exception as e:
    print '*** Import local config failed ***'
    print str(e)


REDIS.host_port = '{host}:{port}'.format(
    host=REDIS.host,
    port=REDIS.port,
)

if REDIS.password:
    REDIS.url = 'redis://:{password}@{host_port}'.format(
        password=REDIS.password,
        host_port=REDIS.host_port,
    )
else:
    REDIS.url = 'redis://{host_port}'.format(
        host_port=REDIS.host_port
    )
