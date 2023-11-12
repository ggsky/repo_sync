#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/11/08 14:59:46
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   bitbucket.com
"""
from .base_platform import BasePlatform
import csv


class BitbucketIE(BasePlatform):
    """bitbucket extract"""

    _host = 'https://api.bitbucket.org/2.0'
    bitbucket_repo_list = 'bitbucket_repo_list.csv'

    def __init__(self, username:str, token:str,host:str =None ,params: dict = None) -> None:
        super().__init__(username=username,token=token)

    def create_repo(self, repo_name: str):
        """create a repo"""
        pass

    def delete(self, repo_name: str):
        """delete a repo"""
        pass

    def get_repo_list(self, username: str):
        """get repo list"""
        pass

    def clone(self):
        pass
    def pull(self, repo_path: str):
        return super().pull(repo_path)
    

    def push(self):
        pass

    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        if extractor == 'bitbucket':
            return True
        else:
            return False
