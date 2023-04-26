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
import yaml

from repo_sync.base_repo import BaseRepo

class GitHubRepo(BaseRepo):
    '''
    GitHubRepo class
    '''
    def __init__(self, user_name, repo_name, logger : logging.Logger):
        super(GitHubRepo, self).__init__(user_name, repo_name,logger)
        
    def sync(self):
        '''
        sync repo
        '''
        # read conf/config.yml
        with open("conf/config.yml", "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        # get github token
        zUser = config["zhizhou"]["user"]
        if zUser == self.user_name:
            self.repo_url = "https://github.com"+"/"+config["github"]["user"]+"/"+self.repo_name+".git"
            self.logger.info("sync repo: %s", self.repo_name)
            self.sess.headers={
                "Authorization": "token "+config["github"]["token"],
            }
            if self.repos==None:
                self.repos = self.sess.get("https://api.github.com/user/repos").json()
            # if repo is not exist, create it
            if self.repo_name not in [repo["name"] for repo in self.repos]:
                self.logger.info("create repo: %s", self.repo_name)
                self.sess.post("https://api.github.com/user/repos", json={"name": self.repo_name})

            os.system("git push %s %s" % (self.repo_url, self.repo_path))
        else:
            self.logger.info("not sync repo: %s", self.repo_name)