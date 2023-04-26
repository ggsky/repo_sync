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
    def __init__(self, user_name, repo_name, logger, debug=False):
        self.sess= requests.Session()
        self.user_name= user_name
        self.repo_name = repo_name
        self.repo_url = "https://github.com"
        self.logger = logger

    def sync(self):
        '''
        sync repo
        '''
        raise NotImplementedError
    
 