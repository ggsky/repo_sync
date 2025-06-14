#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2025/05/05 18:19:43
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   https://api.cnb.cool/
'''
from .base_platform import BasePlatform
from repo_sync.utils.colors import bcolors
import os, subprocess,json
from repo_sync.utils.logger import logger

class CnbIE(BasePlatform):
    """ cnb platform """

    def __init__(self, username:str, token:str, host:str =None ,params: dict = None) -> None:
        super().__init__(username=username,token=token)
        self._host = 'https://api.cnb.cool' if host is None else host
        self._api: str = self._host # + '/api/v5'
        self.repo_private = True if params.get('cnb_private', "true").lower() == 'true' else False
        self.group = params.get('cnb_group', "")
        if not self.group:
            raise ValueError("cnb_group is required")
        
    def create_repo(self, repo_name: str):
        """ create a repo """
        if not self._repo_exists(repo_name=repo_name):
            url = f'{self._api}/{self.group}/-/repos'
            response = self.sess.post(url, json={
                "name": repo_name, 
                "description": "",
             "visibility": "private" if self.repo_private else "public"
             })
            if response.status_code == 201:
                logger.info(f'create repo {self.group}/{repo_name} success')
            else:
                logger.error(f'create repo {self.group}/{repo_name} failed. {response.text}')
        else:
            logger.warning(f'repo {self.group}/{repo_name} already exists')

    def delete(self, repo_name: str):
        """ delete a repo """
        url = f'{self._api}/{self.group}/{repo_name}'
        response = self.sess.delete(url)
        if response.status_code == 200:
            logger.info(f'delete repo {self.group}/{repo_name} success')
        else:
            logger.error(f'delete repo {self.group}/{repo_name} failed. {response.text}')
            return
        logger.info(f'{self._host}/{self.group}/{repo_name}')
            
    def push(self, local_repo_path: str):
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        logger.info(f'push repo:{self.group}/{repo_name} to cnb')
        self.create_repo(repo_name)
        os.chdir(local_repo_path)
        os.system('git remote remove origin_cnb')
        os.system(f'git remote add origin_cnb https://git:{self.token}@cnb.cool/{self.group}/{repo_name}.git')
        
        result = subprocess.run(['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        
        os.system(f'git pull origin_cnb {current_branch}')
        os.system(f'git push -u origin_cnb {current_branch}')
        os.system('git remote remove origin_cnb')
        os.chdir('..')
        
        logger.info(f'push to cnb success')

    def pull(self, local_repo_path: str):
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        logger.info(f'pull repo:{self.group}/{repo_name} from cnb')
        
        os.chdir(local_repo_path)
        os.system('git remote remove origin_cnb')
        os.system(f'git remote add origin_cnb https://git:{self.token}@cnb.cool/{self.group}/{repo_name}.git')
        
        result = subprocess.run(['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        os.system(f'git pull origin_cnb {current_branch}')
        os.system('git remote remove origin_cnb')
        os.chdir('..')
        
        logger.info(f'pull from cnb success')
    

    def _repo_exists(self, repo_name: str) -> bool:
        """ check if repo exists """
        url = f"{self._api}/{self.group}/{repo_name}"
        try:
            response = self.sess.get(url)
            if response.status_code == 200:
                logger.info(f'repo: {repo_name} is existed.')
                return True
        except Exception as e:
            return False

    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        if extractor == 'cnb':
            return True
        else:
            return False
        
