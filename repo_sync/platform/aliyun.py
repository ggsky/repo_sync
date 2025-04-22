#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2024/07/31 01:47:38
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   aliyun devops
read docs:
https://help.aliyun.com/document_detail/460450.html?spm=a2c4g.460449.0.0.4cc62367VCclNI
'''

from traceback import print_tb
from repo_sync.platform.base_platform import BasePlatform
import csv,subprocess
import os
from repo_sync.models import Repo
from repo_sync.utils.colors import bcolors
import json

class AliyunDevOpsIE(BasePlatform):
    """aliyun devops"""

    # _host = 'https://devops.cn-hangzhou.aliyuncs.com'
    _host = r"https://codeup.aliyun.com"
    _api_host = r"https://openapi-rdc.aliyuncs.com"

    def __init__(self, username:str, token:str, host:str =None, params: dict = None) -> None:
        super().__init__(username=username, token=token)
        self.sess.headers.update({'Content-Type': 'multipart/form-data',
                                  'X-Yunxiao-Token': self.token})
        self.repo_private = "private" if params.get('aliyun_private', "true").lower()  == 'true' else "public"
        self.companyId = params.get('aliyun_compoanyid')
        self._api = self._api_host + '/oapi/v1'

### 查询
# GET {{api}}/codeup/organizations/{{organizationId}}/repositories/{{repositoryId}}
# Content-Type: application/json
# X-Yunxiao-Token: {{token}}


    def _get_repo_info(self, repo_name: str):
        """get repo info"""
        url = f'{self._api}/codeup/organizations/{self.companyId}/repositories/{repo_name}'
        r = self.sess.get(url)
        if r.status_code != 200:
            print(f"{bcolors.FAIL}get repo info failed, status code {r.status_code}{bcolors.ENDC}")
            return
        return r.json()

    def create_repo(self, repo_name: str):
        """create a repo"""        
        url = f'{self._api}/codeup/organizations/{self.companyId}/repositories'
        print(url)
        form_data = {
            'name': repo_name, 
            'path': repo_name,
            'visibility': self.repo_private,
        }
        r = self.sess.post(url, data=json.dumps(form_data))
        print(r.text)
        # r = self.sess.post(url, json=json.dumps(form_data))
        if r.status_code != 200:
            print(f"{bcolors.FAIL}create repo {repo_name} failed, status code {r.status_code}{bcolors.ENDC}")
            print(f"{bcolors.FAIL}response: {r.text}{bcolors.ENDC}")
            return

    def delete(self, repo_name: str):
            """delete a project"""
            repositoryId=f"{self.companyId}%2F{repo_name}"
            url = f'{self._api}/codeup/organizations/{self.companyId}/repositories/{repositoryId}'

            response = self.sess.delete(url)
            if response.status_code == 200:
                print(f"{bcolors.OKGREEN}Project: {repo_name} deleted from aliyun successfully!{bcolors.ENDC}")
            else:
                print(f'{bcolors.FAIL}Failed to delete project: {repo_name} from aliyun. Error {response.status_code}: {response.text}{bcolors.ENDC}')
    
    def pull(self, local_repo_path: str):
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        print(f"{bcolors.OKGREEN}pull repo:{self.username}/{repo_name} from aliyun{bcolors.ENDC}")
        os.chdir(local_repo_path)

        os.system('git remote remove origin_aliyun')
        os.system(f'git remote add origin_aliyun https://{self.username}:{self.token}@codeup.aliyun.com/{self.companyId}/{repo_name}.git')
        result = subprocess.run(['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        os.system(f'git pull origin_aliyun {current_branch}')
        os.system('git remote remove origin_aliyun')
        os.chdir('..')
        
        print(bcolors.OKGREEN + 'pull from aliyun success' + bcolors.ENDC)

    def push(self, local_repo_path: str):
        """ push local repo to aliyun"""
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        print(bcolors.WARNING + f'push repo:{self.username}/{repo_name} to aliyun' + bcolors.ENDC)
        self.create_repo(repo_name)
        os.chdir(local_repo_path)
        os.system('git remote remove origin_aliyun')
        os.system(f'git remote add origin_aliyun https://{self.username}:{self.token}@codeup.aliyun.com/{self.companyId}/{repo_name}.git')
        
        result = subprocess.run(['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        
        os.system(f'git pull origin_aliyun {current_branch}')
        os.system(f'git push -u origin_aliyun {current_branch}')
        os.system('git remote remove origin_aliyun')
        os.chdir('..')
        
        print(bcolors.OKGREEN + 'push to aliyun success' + bcolors.ENDC)


    def clone(self):
        """ clone repo from aliyun"""
        pass

    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        if extractor == 'aliyun':
            return True
        else:
            return False
