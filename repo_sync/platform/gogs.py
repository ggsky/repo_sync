#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/11/08 14:29:44
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   
"""
from .base_platform import BasePlatform
import csv, re, subprocess
import json, os
from repo_sync.utils.colors import bcolors
from repo_sync.utils.logger import logger
class GogsIE(BasePlatform):
    """ gogs plotform class """
    gityoqi_repo_list = 'gityoqi_repo_list.csv'
    def __init__(self, username: str, token: str, host: str = None, params: dict = None) -> None:
        super().__init__(username=username, token=token)
        self._host = 'https://git.yoqi.me' if host is None else host
        self.repo_private: bool = True if params.get('gogs_private', "true").lower() == 'true' else False

    def create_org_repo(self, org_name: str, repo_name: str):
        """create org repo"""
        url = f'{self._host}/api/v1/orgs/{org_name}/repos'
        payload = {
            'name': repo_name,
            'description': 'This is your first repository',
            'private': self.repo_private,
            'auto_init': True,
            'gitignores': 'Go',
            'license': 'Apache v2 License',
            'readme': 'Default',
        }
        r = self.sess.post(url, data=json.dumps(payload))
        if r.status_code != 201:
            logger.error(f'create org repo {repo_name} failed, status code {r.status_code}')
            return
        logger.info(f'create org repo {repo_name} success')
        logger.info(f'{self._host}/{org_name}/{repo_name}')
        
    def create_repo(self, repo_name: str):
        """create a repo"""
        url = f'{self._host}/api/v1/user/repos'
        payload = {
            'name': repo_name,
            'description': 'This is your first repository',
            'private': True,
            # "auto_init": True,
            # "gitignores": "Go",
            # "license": "Apache v2 License",
            # "readme": "Default",
        }
        r = self.sess.post(url, data=json.dumps(payload))
        if r.status_code != 201:
            logger.error(f'create repo {repo_name} failed, status code {r.status_code}')
            return
        logger.info(f'create repo {repo_name} success')

    def delete(self, repo_name: str):
        """delete a repo, maybe request a confirm by input"""
        url = f'{self._host}/api/v1/repos/{self.username}/{repo_name}'
        r = self.sess.delete(url)
        if r.status_code != 204:
            logger.error(f'delete repo {repo_name} failed, status code {r.status_code}')
            return
        logger.info(f'delete repo {repo_name} success')

    def get_repo_list(self, repo_name: str):
        """get repo list"""
        url = f'{self._host}/api/v1/users/{self.username}/repos'
        r = self.sess.get(url)
        if r.status_code != 200:
            logger.error(f'get repo list failed, status code {r.status_code}')
            return
        self.repos = r.json()
        logger.info(f'get repo list success')

    def clone(self):
        pass

    def pull(self, local_repo_path: str):
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        logger.info(f'pull repo:{self.username}/{repo_name} from {self._host}')
        pur_host = re.search(r'(?<=//)[^/]+', self._host).group()
        os.chdir(local_repo_path)
        os.system('git remote remove origin_gogs')
        os.system(
            f'git remote add origin_gogs https://{self.username}:{self.token}@{pur_host}/{self.username}/{repo_name}.git'
        )
        result = subprocess.run(
            ['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        os.system(f'git pull origin_gogs {current_branch}')
        os.system('git remote remove origin_gogs')
        os.chdir('..')

    def push(self, local_repo_path: str):
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        logger.info(f'push repo:{self.username}/{repo_name} to {self._host}')
        pur_host = re.search(r'(?<=//)[^/]+', self._host).group()
        os.chdir(local_repo_path)
        os.system('git remote remove origin_gogs')
        os.system(
            f'git remote add origin_gogs https://{self.username}:{self.token}@{pur_host}/{self.username}/{repo_name}.git'
        )
        result = subprocess.run(
            ['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        os.system(f'git pull origin_gogs {current_branch}')
        os.system(f'git push -u origin_gogs {current_branch}')
        os.system('git remote remove origin_gogs')
        os.chdir('..')

    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        if extractor == 'gogs':
            return True
        else:
            return False
