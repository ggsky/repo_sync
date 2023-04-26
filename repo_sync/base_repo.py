#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/04/27 02:55:45
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   
'''
import requests

class BaseRepo(object):
    '''
    Repo class
    '''
    def __init__(self, repo_name, repo_url, repo_branch, repo_path, repo_type, debug=False):
        self.sess= requests.Session()
        self.repo_name = repo_name
        self.repo_url = repo_url
        self.repo_branch = repo_branch
        self.repo_path = repo_path
        self.repo_type = repo_type

    def sync(self):
        '''
        sync repo
        '''
        raise NotImplementedError
    
 