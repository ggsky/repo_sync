#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/11/01 00:01:04
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   命令行参数，或配置文件
"""

import argparse
import os
import shlex
import dotenv
from collections import OrderedDict
from .utils.str_util import preferredencoding


def parser_args(overrideArguments=None):
    """解析参数"""

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-c', '--config', help='config file', default='config.ini')
    argparser.add_argument(
        'command',
        help='command: ',
        choices=['create', 'clone', 'push', 'delete', 'pull'],
    )
    argparser.add_argument('-d', '--debug', help='debug mode', action='store_true')
    argparser.add_argument(
        '-p',
        '--platform',
        help='set a platform',
        choices=['github', 'gitee', 'gitlab', 'gogs', 'gitea', 'bitbucket', 'coding', 'gitcode'],
        default='github',
    )
    argparser.add_argument('-token', '--token', help='set a token')
    argparser.add_argument(
        '-repo_path', '--repo_path', help='set a repo'
    )  # , default=os.getcwd())
    args = argparser.parse_args()

    # remove None
    command_line_conf = OrderedDict(
        {k: v for k, v in args.__dict__.items() if v is not None}
    )

    system_conf = user_conf = custom_conf = OrderedDict()
    user_conf = _read_user_conf()

    if args.config:
        custom_conf = _read_custom_conf(args.config)

    system_conf.update(user_conf)
    system_conf.update(command_line_conf)
    if args.command == None and args.extractor == None:
        raise 'Error, please input cmd and extractor params11'
    return system_conf


def _read_custom_conf(config_path: str) -> OrderedDict:
    """读取自定义配置文件 config.yaml"""

    def compat_shlex_split(s, comments=False, posix=True):
        if isinstance(s, str):
            s = s.encode('utf-8')
        return list(map(lambda s: s.decode('utf-8'), shlex.split(s, comments, posix)))

    try:
        with open(config_path, 'r', encoding=preferredencoding()) as f:
            contents = f.read()
            res = compat_shlex_split(contents, comments=True)
    except Exception as e:
        return []
    return res


def _read_user_conf() -> OrderedDict:
    """读取用户配置文件: .env 文件"""
    user_conf = OrderedDict()
    dotenv_path = '.env'
    if os.path.exists(dotenv_path):
        user_conf = dotenv.dotenv_values(dotenv_path)
    return OrderedDict(user_conf)
