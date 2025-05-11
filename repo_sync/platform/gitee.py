#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/11/09 17:40:42
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   gitee async

"""
from .base_platform import BasePlatform
import csv, subprocess
import os
from repo_sync.models import Repo
from repo_sync.utils.colors import bcolors
from repo_sync.utils.logger import logger
class GiteeIE(BasePlatform):
    """gitee async"""
    _host = 'https://gitee.com'
    _api = _host + '/api/v5'
    
    def __init__(self, username:str, token:str, host:str=None, params: dict=None) -> None:
        super().__init__(username=username, token=token)
        self.sess.headers.update({'Content-Type': 'multipart/form-data'})
        self.repo_private = True if params.get('gitee_private', "true").lower() == 'true' else False
    
    def create_repo(self, repo_name: str):
        """create a repo"""
        if not self._repo_exists(repo_name=repo_name):
            url = f'{self._api}/user/repos'
            form_data = {
                'name': repo_name, 
                'private': self.repo_private,
            }
            r = self.sess.post(url, params=form_data)
            if r.status_code != 201:
                logger.error(f'create repo {repo_name} failed, status code {r.status_code}')
                return
            logger.info(f'create repo {repo_name} success')
        logger.info(f'{self._host}/{self.username}/{repo_name}')

    def delete(self, repo_name: str):
        """delete a repo"""
        url = f'{self._api}/repos/{self.username}/{repo_name}'
        response = self.sess.delete(url)
        if response.status_code == 204:
            logger.info(f'Repository: {repo_name} deleted from gitee successfully!')
        else:
            logger.error(f'Failed to delete repository: {repo_name} from gitee. Error {response.status_code}: {response.text}')
    
    def get_repo_list(self) -> list:
        """get repo list"""
        if os.path.exists(self.repo_list_path):
            with open(self.repo_list_path, 'r', encoding='utf8') as f:
                reader = csv.reader(f)
                for row in reader:
                    repo = Repo()
                    repo.__dict__ = row
                    self.repos.append(repo)
            return self.repos
        
        url = f'{self._api}/user/repos'
        r = self.sess.get(url)
        if r.status_code != 200:
            logger.error(f'get repo list failed, status code {r.status_code}')
            return
        
        repo_list = r.json()
        self.save_csv()
        return repo_list
    
    def clone(self):
        pass
    
    def pull(self, local_repo_path: str):
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        logger.info(f'pull repo:{self.username}/{repo_name} from gitee')
        
        os.chdir(local_repo_path)
        os.system('git remote remove origin_gitee')
        os.system(f'git remote add origin_gitee https://{self.username}:{self.token}@gitee.com/{self.username}/{repo_name}.git')
        
        result = subprocess.run(['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        os.system(f'git pull origin_gitee {current_branch}')
        os.system('git remote remove origin_gitee')
        os.chdir('..')
        
        logger.info(f'pull from gitee success')
    
    def push(self, local_repo_path: str):
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        logger.info(f'push repo:{self.username}/{repo_name} to gitee')
        self.create_repo(repo_name)
        os.chdir(local_repo_path)
        os.system('git remote remove origin_gitee')
        os.system(f'git remote add origin_gitee https://{self.username}:{self.token}@gitee.com/{self.username}/{repo_name}.git')
        
        result = subprocess.run(['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        
        os.system(f'git pull origin_gitee {current_branch}')
        os.system(f'git push -u origin_gitee {current_branch}')
        os.system('git remote remove origin_gitee')
        os.chdir('..')
        
        logger.info(f'push to gitee success')
    
    def _repo_exists(self, repo_name: str):
        """check if a repo exists
        不存在，{
                "message": "Not Found Project"
                }
        存在：返回 repo 数据
        """
        url = f'{self._api}/repos/{self.username}/{repo_name}'
        try:
            response = self.sess.get(url)
            if response.status_code == 200 and response.json()['message'] != 'Not Found Project':
                logger.info(f'repo: {repo_name} is existed.')
                return True
        except Exception as e:
            return False
        
    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        return extractor == 'gitee'
