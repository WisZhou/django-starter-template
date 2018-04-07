# encoding: utf-8

'''
不依赖Django的utils, 该文件不可导入任何Django相关包，否则会循环导入
'''

import logging

from scloud.conf import config


def get_logger(name='utils', logfile=None):
    '''
    参数: name (str): logger name
        logfile (str): log file, 没有时使用stream handler
    返回:
        logger obj
    '''
    my_logger = logging.getLogger(name)
    my_logger.setLevel(config.LOG_LEVEL)
    if logfile:
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler()
    fmt = ('%(asctime)s - %(name)s - %(levelname)s - %(filename)s '
           '- %(funcName)s - %(lineno)s - %(message)s')
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    my_logger.addHandler(handler)
    # 阻止冒泡
    my_logger.propagate = False
    return my_logger


LOGGER = get_logger('utils')
