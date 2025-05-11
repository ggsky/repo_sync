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
from .utils.config_reader import ConfigReader
from .utils.frozen_dir import get_app_path

def parser_args(overrideArguments=None):
    """解析参数"""

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-c', '--config', help='config file', default='config.yml')
    argparser.add_argument(
        'command',
        help='command: ',
        choices=['create', 'clone', 'push', 'delete', 'pull'],
        nargs='?',
        default=''
    )
    argparser.add_argument('-d', '--debug', help='debug mode', action='store_true')
    argparser.add_argument(
        '-p',
        '--platform',
        help='set a platform',
        choices=['github', 'gitee', 'gitlab', 'gogs', 'gitea', 'bitbucket', 'coding', 'aliyun','gitcode','cnb'],
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
        custom_conf = _read_custom_platform_conf(args.config, args.platform)
   
    app_path = get_app_path()
    system_conf["app_path"] = app_path

    system_conf.update(user_conf)
    system_conf.update(command_line_conf)
    system_conf.update(custom_conf)
    if args.command == None and args.extractor == None:
        raise 'Error, please input cmd and extractor params'
    return system_conf


def only_combine_conf(args:dict):

    system_conf = user_conf = custom_conf = OrderedDict()
    user_conf = _read_custom_platform_conf("config.yml", args['platform'])

    app_path = get_app_path()
    system_conf["app_path"] = app_path
    
    system_conf.update(user_conf)
    system_conf.update(custom_conf)
    system_conf.update(args)
    return system_conf

def _read_user_conf() -> OrderedDict:
    """读取用户配置文件: .env 文件"""
    user_conf = OrderedDict()
    dotenv_path = '.env'
    if os.path.exists(dotenv_path):
        user_conf = dotenv.dotenv_values(dotenv_path)
    return OrderedDict(user_conf)

def _read_custom_platform_conf(config_path:str="config.yml",platform:str="github") -> OrderedDict:
    """读取自定义平台配置文件"""
    config_reader = ConfigReader(config_path)
    custom_conf = OrderedDict()
    
    # Get platform enable list
    platform_config = config_reader.get_platform_config(platform)
    # Convert platform config to environment variables format
    for key, value in platform_config.items():
        custom_conf[f"{platform}_{key}"] = str(value)
    
    return custom_conf

def _read_custom_conf(config_path: str) -> OrderedDict:
    """读取自定义配置文件"""
    config_reader = ConfigReader(config_path)
    custom_conf = OrderedDict()
    
    # Get all platform accounts
    platform_accounts = config_reader.get_platform_accounts()
    
    # Convert platform accounts to environment variables format
    for platform, accounts in platform_accounts.items():
        for account in accounts:
            account_config = config_reader.get_account_config(platform, account)
            for key, value in account_config.items():
                custom_conf[f"{platform}_{account}_{key}"] = str(value)
    
    return custom_conf
