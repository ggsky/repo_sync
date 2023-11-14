#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/11/09 19:17:57
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   
"""


class GiteaIE(object):
    def __init__(self, username:str, token:str, host:str =None ,params: dict = None) -> None:
        super().__init__(username=username,token=token)
        self._host = 'https://gitea.com' if host is None else host

    def create_repo(self, repo_name: str):
        pass

    def delete(self, repo_name: str):
        pass

    def get_repo_list(self) -> list:
        pass

    def clone(self):
        pass

    def push(self, local_repo_path: str):
        pass
        
    def pull(self, local_repo_path: str):
        return super().pull(local_repo_path)
    
    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        if extractor == 'gitea':
            return True
        else:
            return False
