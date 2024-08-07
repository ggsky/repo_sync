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

from repo_sync.platform.base_platform import BasePlatform
import csv,subprocess
import os
from repo_sync.repo import Repo
from repo_sync.utils.colors import bcolors


class AliyunDevOps(BasePlatform):
    """aliyun devops"""

    _host = 'https://devops.cn-hangzhou.aliyuncs.com'

    def __init__(self, username:str, token:str,host:str =None, params: dict = None) -> None:
        super().__init__(username=username, token=token)
        self.sess.headers.update({'Content-Type': 'multipart/form-data'})
        self.repo_private = True if params.get('aliyun_private', "true").lower()  == 'true' else False
        self.companyId = 1411978
        self.groupId = 1411978

    def create_project(self, project_name: str):
        """create a project
        这里概念是：代码组
        """        
        url = f'{self._api}/repository/groups/create'
        form_data = {
            "accessToken":"",
            'name': project_name, 
            'path': project_name,
            'visibilityLevel': self.repo_private==True ? 10 : 0, 
            'parentId': 1411978,
            'private': self.repo_private,
        }
        r = self.sess.post(url, params=form_data)
        if r.status_code != 200:
            print(f'{bcolors.FAIL}create project {project_name} failed, status code {r.status_code}{bcolors.ENDC}')
            return
        else:
            print(r.json())
            print(f'{bcolors.OKGREEN}create project {project_name} success{bcolors.ENDC}')

    def get_project_info(self, project_name: str):
        """get project info"""
        url = f'{self._api}/api/4/groups/find_by_path'
        form_data = {
            "organizationId": self.companyId,
            "identity": "%s/%s" % (self.companyId, project_name)
        }
        r = self.sess.get(url, params=form_data)
        if r.status_code != 200:
            print(f"{bcolors.FAIL}get project info failed{bcolors.ENDC}")
            return
        else:
            print(r.json())
            return r.json()

    def delete_project(self, project_name: str):
        """delete a project"""
        # get group id
        url = f'{self._api}/api/4/groups/find_by_path'
        form_data = {
            "organizationId": self.companyId,
            "identity": "%s/%s" % (self.companyId, project_name)
        }
        r = self.sess.get(url, params=form_data)
        if r.status_code != 200:
            print(f"{bcolors.FAIL}get group id failed{bcolors.ENDC}")
            return
        else:
            # delete the project
            group = r.json()
            groupId = group['result']['id']
            url = f'{self._api}/repository/groups/{groupId}/remove'
            form_data = {
                "accessToken":"",
                "organizationId": self.companyId,
                "groupId": groupId,
                "reason":"not need"
                }
            response = self.sess.post(url)
            if response.status_code == 204:
                print(f'{bcolors.OKGREEN}Project: {project_name} deleted from aliyun successfully!{bcolors.ENDC}')
            else:
                print(f'{bcolors.FAIL}Failed to delete project: {project_name} from aliyun. Error {response.status_code}: {response.text}{bcolors.ENDC}')
    def get_project_list(self) -> list:
        pass
    
    def get_repo_list(self) -> list:
        """ get repo list"""
        url = f'{self._api}/repository/list'
        form_data = {
            "organizationId": self.companyId,
            "page": 1,
            "pageSize": 100,
            "orderBy":"last_activity_at",
            # "search":"",
            "archived":"true",
        }
        r = self.sess.get(url, params=form_data)
        if r.status_code != 200:
            print(f"{bcolors.FAIL}get repo list failed, status code {r.status_code}{bcolors.ENDC}")
            return
        repo_list = r.json()
        return repo_list
    
    def _get_repo_info(self, repo_name: str):
        """get repo info"""
        url = f'{self._api}/repository/get'
        form_data = {
            "accessToken":"",
            "organizationId": self.companyId,
            "name": repo_name
        }
        r = self.sess.get(url, params=form_data)
        if r.status_code != 200:
            print(f"{bcolors.FAIL}get repo info failed, status code {r.status_code}{bcolors.ENDC}")
            return
        return r.json()


    def create_repo(self, repo_name: str):
        """create a repo"""        
        url = f'{self._api}/repository/create'
        form_data = {
        "accessToken":"",
        'name': repo_name, 
        'private': self.repo_private,
        }
        r = self.sess.post(url, params=form_data)
        if r.status_code != 201:
            print(f"{bcolors.FAIL}create repo {repo_name} failed, status code {r.status_code}{bcolors.ENDC}")
            return

    def delete(self, repo_name: str):
            """delete a project"""
            url = f'{self._api}/project/{repo_name}'

            response = self.sess.delete(url)
            if response.status_code == 204:
                print(f"{bcolors.OKGREEN}Project: {repo_name} deleted from aliyun successfully!{bcolors.ENDC}")
            else:
                print(f'{bcolors.FAIL}Failed to delete project: {repo_name} from aliyun. Error {response.status_code}: {response.text}{bcolors.ENDC}')
    def pull(self, local_repo_path: str):
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        print(f"{bcolors.OKGREEN}pull repo:{self.username}/{repo_name} from aliyun{bcolors.ENDC}")
        os.chdir(local_repo_path)
        result = subprocess.run(['git', 'pull', 'https://codeup.aliyun.com/api/v1/repository/get?accessToken=&organizationId=1411978&name='+repo_name])
    
    def push(self, local_repo_path: str):
        """ push local repo to aliyun"""
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        print(f"{bcolors.OKGREEN}push repo:{self.username}/{repo_name} to aliyun{bcolors.ENDC}")
        os.chdir(local_repo_path)
        result = subprocess.run(['git', 'push', 'https://codeup.aliyun.com/api/v1/repository/create?accessToken=&organizationId=1411978&name='+repo_name])
            
    def clone(self):
        """ clone repo from aliyun"""
        pass

    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        if extractor == 'aliyun_devops':
            return True
        else:
            return False
