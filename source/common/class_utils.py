#!/usr/bin/env python
# encoding: utf-8


class Config(object):
    ''' 可用.操作符取属性的参数实例 '''

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
