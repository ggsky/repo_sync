#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/04/27 02:59:42
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   github repo
'''
import os,sys,re
import logging
import argparse

from repo_sync.base_repo import BaseRepo

class GitHubRepo(BaseRepo):
    '''
    GitHubRepo class
    '''
    def __init__(self, repo_name, repo_url, repo_branch, repo_path, repo_type):
        super(GitHubRepo, self).__init__(repo_name, repo_url, repo_branch, repo_path, repo_type)
        self.repo_type = 'github'
        self.repos=None
        
    def sync(self):
        '''
        sync repo
        '''
        self.logger.info("sync repo: %s", self.repo_name)
        self.sess.headers={
            "Authorization": "token   6b0b9"
        }
        if self.repos==None:
            self.repos = self.sess.get("https://api.github.com/user/repos").json()
        # if repo is not exist, create it
        if self.repo_name not in [repo["name"] for repo in self.repos]:
            self.logger.info("create repo: %s", self.repo_name)
            self.sess.post("https://api.github.com/user/repos", json={"name": self.repo_name})

        os.system("git push %s %s" % (self.repo_url, self.repo_path))