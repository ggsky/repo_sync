#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/04/27 04:23:34
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   github repo
'''
from repo_sync.base_repo import BaseRepo
import logging
import yaml

class GitlabRepo(BaseRepo):
    '''
    GitlabRepo class
    '''
    def __init__(self, user_name, repo_name, logger : logging.Logger):
        super(GitlabRepo, self).__init__(user_name, repo_name,logger)
    
    def sync(self):
        ''' sync repo '''
        # read conf/config.yml
        with open("conf/config.yml", "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        # get github token
        zUser = config["zhizhou"]["user"]
        if zUser == self.user_name:
            self.repo_url="https://gitlab.com/"+config["gitlab"]["user"]+"/"+self.repo_name+".git"
            self.logger.info("sync repo: %s", self.repo_name)
            self.sess.headers={
                "PRIVATE-TOKEN": config["gitlab"]["token"],
            }
            if self.repos==None:
                self.repos = self.sess.get("https://gitlab.com/api/v4/projects").json()
            # if repo is not exist, create it
            if self.repo_name not in [repo["name"] for repo in self.repos]:
                self.logger.info("create repo: %s", self.repo_name)
                self.sess.post("https://gitlab.com/api/v4/projects", json={"name": self.repo_name})
            os.system("git push %s %s" % (self.repo_url, self.repo_path))
        else:
            self.logger.info("not sync repo: %s", self.repo_name)