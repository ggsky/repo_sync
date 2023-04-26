#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/04/27 03:09:58
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   sync utils
'''
import os
import sys
import time
import json
import logging
import argparse
from repo_sync.coding_repo import CodingRepo
from repo_sync.github_repo import GitHubRepo
from repo_sync.github_repo import Coding

class SyncUtils:
    '''
    SyncUtils class
    '''
    def __init__(self, debug=False):
        self.args = None
        self.logger = None
        self.init_logger(debug)
        self.init_args()

    def run(self):
        '''
        run repo
        '''
        repos= []
        with open("repos.text", "r") as f:
            repos = f.readlines()
        for repo in repos:
            repo_name = repo.split("/")[-1].replace(".git","")
            user_name=repo.split("/")[-2]
            if not os.path.exists(user_name):
                os.mkdir(user_name)

            if not os.path.exists(os.path.join(user_name,repo_name)):
                self.logger.info("clone repo: %s", repo_name)
                os.system("git clone %s" % repo_name)

            self.logger.info("sync repo: %s", repo_name)
            repoModel = None
            if self.args.type == "github":
                repoModel = GitHubRepo(user_name, repo_name, self.logger)
            elif self.args.type == "coding":
                repoModel = CodingRepo(user_name, repo_name)
            repoModel.sync()

    def init_logger(self, debug:bool):
        '''
        init logger
        '''
        self.logger = logging.getLogger(self.repo_name)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def init_args(self):
        '''
        init args
        '''
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--debug', action='store_true', help='debug mode')
        parser.add_argument('-type', '--type', action='store_true',default="github", help='github,gitlab,gitee,coding')
        parser.add_argument('-repo', '--repository', action='store_true', default="github", help='run repo')
        self.args = parser.parse_args()
