#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2024/08/07 19:14:51
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   huawei platform
'''

from repo_sync.platform.base_platform import BasePlatform
import csv, subprocess,os,json
from repo_sync.utils.colors import bcolors

class HuaweiIE(BasePlatform):
    """ huawei platform class """
    def __init__(self, username: str, token: str, host: str = None, params: dict = None) -> None:
        super().__init__(username=username, token=token)
        self._host = 'https://git.huawei.com' if host is None else host


    def clone(self, repo_name: str, repo_url: str, branch: str = None) -> bool:
        pass
    def pull(self, repo_name: str, branch: str = None) -> bool:
        pass
    def push(self, repo_name: str, branch: str = None) -> bool:
        pass
    def delete(self, repo_name: str) -> bool:
        pass