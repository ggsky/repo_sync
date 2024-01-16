#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/04/27 03:09:58
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   sync utils
'''
import os,csv,re
import logging
from .platform import gen_extractor_classes
from .repo import Repo

class RepoSync(object):
    '''
    SyncUtils class
    '''
    repo_list_path = 'repo_list.csv'

    def __init__(self, params: dict, debug=False):
        self.args = None
        self.logger = None
        self.init_logger(debug)

        self.params = params
        self.params['logger'] = self.logger
        self.platforms = []
        self.repos = []
        for p in gen_extractor_classes():
            self.platforms.append(p)
        if params.get('repo_path', None) is not None:
            self.repo_path = params.get('repo_path', None)
            self.get_local_repo_list(params.get('repo_path', None))
    
    def get_local_repo_list(self, repo_path):
        """get git repo list from a folder"""
        if os.path.isdir(repo_path) and os.path.exists(os.path.join(repo_path, '.git')):
            self._find_git_repo(
                path=repo_path, repo_name=repo_path.split(os.path.sep)[-1])
        else:
            for dir in os.listdir(repo_path):
                current_path = os.path.join(repo_path, dir)
                if os.path.isdir(current_path) and os.path.exists(os.path.join(current_path, '.git')):
                    self._find_git_repo(path=current_path, repo_name=dir)
        with open(self.repo_list_path, 'w') as f:
            if len(self.repos) == 0:
                print('repo list is empty, please delete repo_list.csv and try again')
                return
            writer = csv.DictWriter(
                f, fieldnames=self.repos[0].__dict__.keys(), lineterminator='\n'
            )
            writer.writeheader()
            for repo in self.repos:
                writer.writerow(repo.__dict__)
                
    def _find_git_repo(self, path: str, repo_name:str =None):
        try:
            with open('{}/.git/config'.format(path), 'r') as f:
                # get the remote url
                repo =Repo()
                try:
                    url = re.findall(r'url\s+=\ (.*)', f.read())[0]
                    # print(url)
                    repo.name = url.split('/')[-1].replace('.git', '')
                    repo.url = url
                except Exception as e:
                    repo.name = repo_name
                repo.local_path = path
                self.repos.append(repo)
        except Exception as e:
            print("skip {} because of {}".format(path, e))

    def run(self):
        '''
        run repo
        '''
        command = self.params.get('command')
        platform = self.params.get('platform', 'github')
        current_platform = None
        for p in self.platforms:
            if p.suitable(platform):
                current_platform = p
        if current_platform is not None:
            username = self.params.get(f'{platform}_username', None)
            token = self.params.get(f'{platform}_token', None)
            host = self.params.get(f'{platform}_host', None)

            if command == 'clone':
                current_platform(username, token, host, self.params).clone(self.repo_path)
                return
            if os.path.exists(self.repo_list_path):
                with open(self.repo_list_path, 'r', encoding='utf8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        repo = Repo()
                        repo.__dict__ = row
                        if command == 'create':
                            current_platform(username,token, host, self.params).create_repo(repo.name)
                        if command == 'push':
                            current_platform(username,token, host, self.params).push(repo.local_path)
                        elif command == 'delete':
                            current_platform(username,token, host, self.params).delete(repo.name)
                        elif command =='pull':
                            current_platform(username,token, host, self.params).pull(repo.local_path)
            else:
                logging.info(
                    'repo list is not exist, please run list_local command first'
                )

    def init_logger(self, debug:bool):
        '''
        init logger
        '''
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
