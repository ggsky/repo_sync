#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/10/31 17:06:37
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   字符串工具类
"""
import argparse
import locale
import re
import sys


def compat_register_utf8():
    """win 兼容utf-8编码"""
    if sys.platform == 'win32':
        from codecs import register, lookup

        register(lambda name: lookup('utf-8') if name == 'cp65001' else None)


def preferredencoding():
    """Get preferred encoding.

    Returns the best encoding scheme for the system, based on
    locale.getpreferredencoding() and some further tweaks.
    """
    try:
        pref = locale.getpreferredencoding()
        'TEST'.encode(pref)
    except Exception:
        pref = 'UTF-8'

    return pref


def SpCharReplace(char):
    """特殊字符替换"""
    temp = str(char)
    for i in temp:
        if '<' == i:
            char = char.replace('<', '《')
        if '>' == i:
            char = char.replace('>', '》')
        if "'" == i:
            char = char.replace("'", '')  # 处理单引号
        if '\\' == i:
            char = char.replace('\\', '')  # 处理反斜杠\
        if '"' == i:
            char = char.replace('"', '`')  # 处理双引号"
        if '&' == i:
            char = char.replace('&', '-')  # 处理&号"
        if '|' == i:
            char = char.replace('|', '')  # 处理&号
        if '@' == i:
            char = char.replace('@', '.')  # 处理@号
        if '%' == i:
            char = char.replace('%', '`')  # 处理单引号
        if '*' == i:
            char = char.replace('*', '`')  # 处理反斜杠\
        if '("' == i:
            char = char.replace('"', '`')  # 处理双引号"
        if ')"' == i:
            char = char.replace(')"', '`')
        if '-' == i:
            char = char.replace('-', '`')  # 处理&号
        if 'ÐÂÎÅ' == i:
            char = char.replace('ÐÂÎÅ', '`')  # 处理ÐÂÎÅ
        # 在后面扩展其他特殊字符
    return char
