#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/04/27 05:12:59
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   gitee repo
'''

from repo_sync.base_repo import BaseRepo
import logging
import os
import yaml

class GiteeRepo(BaseRepo):
    
    def __init__(self, user_name, repo_name, logger : logging.Logger):
        super(GiteeRepo, self).__init__(user_name, repo_name,logger)
        self.repos=None

    def sync(self):
        ''' sync repo
        '''
        # read conf/config.yml
        with open("conf/config.yml", "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        # get github token
        zUser = config["zhizhou"]["user"]
        if zUser == self.user_name:
            self.repo_url = "https://gitee.com"+"/"+config["gitee"]["user"]+"/"+self.repo_name+".git"
            self.logger.info("sync repo: %s", self.repo_name)
            self.sess.headers={
                "Authorization": "token "+config["gitee"]["token"],
            }
            if self.repos==None:
                res = self.sess.get("https://api.gitee.com/user/repos")
                if res.status_code != 200:
                    self.logger.error("get gitee repo list failed, status_code: %s, please check the token.", res.status_code)
                    return
                self.repos = res.json()
            # if repo is not exist, create it
            if self.repo_name not in [repo["name"] for repo in self.repos]:
                self.logger.info("create repo: %s", self.repo_name)
                self.sess.post("https://api.gitee.com/user/repos", json={"name": self.repo_name})
            # git push it
            os.chdir(self.user_name+"/"+self.repo_name)
            os.system("git remote add origin2 "+self.repo_url)
            os.system("git push -u origin2 master")
            os.chdir("../..")
        else:
            self.logger.info("not sync repo: %s", self.repo_name)