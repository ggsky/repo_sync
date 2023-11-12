#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/09/27 10:35:25
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   coding.net repo sync

两种授权： token 授权，OAuth2.0 授权

"""
import os
from repo_sync.platform.base_platform import BasePlatform
from .project import Project
from .repo import Repo

class CodingIE(BasePlatform):
    """coding util"""
    client_id = ''
    client_serect = ''
    _host = 'https://e.coding.net'  # 新版接口统一地址

    def __init__(self, username:str, token:str,host:str =None ,params: dict = None) -> None:
        """init"""
        super().__init__(username , token)
        self.project_name = params.get('coding_project', '')

    def create_project(self):
        ''' createt a project '''
        url = f'{self._host}/open-api'
        data = {
            'Action': 'CreateCodingProject',
            'Name': '',
            'DisplayName': '',
            'Description': '',
            'GitReadmeEnabled': False,
            'VscType': 'git',
            'CreateSvnLayout': False,
            'Shared': 1,
            'ProjectTemplateId': 'DEV_OPS',
        }
        r = self.sess.post(url, json=data)
        if r.status_code == 200:
            res_data = r.json()
            return True
        else:
            return False

    def delete_project(self):
        url = f'{self._host}/open-api'
        data = {
            'Action': 'DeleteOneProject',
            'ProjectId': 0,
        }
        r = self.sess.post(url, json=data)
        if r.status_code == 200:
            res_data = r.json()
            return True
        else:
            return False

    def get_project_list(self):
        pass

    def get_repo_list(self, username: str):
        """get repo list"""
        url = f'{self._host}/open-api'
        data = {
            'Action': 'DescribeTeamDepotInfoList',
            'ProjectName': '',
            'DepotName': '',
            'PageNumber': 1,
            'PageSize': 50
        }
        r = self.sess.post(url, json=data)
    
    def get_repo_info(self, repo_name: str):
        """get repo list"""
        url = f'{self._host}/open-api'
        data = {
            'Action': 'DescribeTeamDepotInfoList',
            'ProjectName': self.project_name,
            'DepotName': repo_name,
            'PageNumber': 1,
            'PageSize': 50
        }
        r = self.sess.post(url, json=data)
        if r.status_code == 200:
            res_data = r.json()
            if res_data['Response']["DepotData"]["Page"]["TotalRow"] > 0:
                DepotList = res_data['Response']["DepotData"]["Depots"]
                depot = Repo(
                    Id=DepotList[0]['Id'],
                    Name=DepotList[0]['Name'],
                    HttpsUrl=DepotList[0]['HttpsUrl'],
                    ProjectId=DepotList[0]['ProjectId'],
                    SshUrl=DepotList[0]['SshUrl'],
                    WebUrl=DepotList[0]['WebUrl'],
                    ProjectName=DepotList[0]['ProjectName'],
                    Description=DepotList[0]['Description'],
                    CreatedAt=DepotList[0]['CreatedAt'],
                    GroupId=DepotList[0]['GroupId'],
                    GroupName=DepotList[0]['GroupName']
                )
                return depot

    def get_project_info(self)->Project:
        url = f'{self._host}/open-api'
        data = {
            "Action": "DescribeCodingProjects",
            "ProjectName": self.project_name,
            "DepotName": "",
            "PageNumber": 1,
            "PageSize": 50
            }
        r = self.sess.post(url, json=data)
        if r.status_code == 200:
            res_data = r.json()
            if res_data['Response']["Data"]["TotalCount"] > 0:
                ProjectList = res_data['Response']["Data"]["ProjectList"]
                projet = Project(
                    Id=ProjectList[0]['Id'],
                    Name=ProjectList[0]['Name'],
                    DisplayName=ProjectList[0]['DisplayName'],
                    Description=ProjectList[0]['Description'],
                    TeamOwnerId=ProjectList[0]['TeamOwnerId'],
                    TeamId=ProjectList[0]['TeamId']
                )
                return projet

    def create_repo(self, repo_name: str):
        """create a repo"""
        # get project id
        project = self.get_project_info()

        url = f'{self._host}/open-api/repos'
        data = {
            "Action": "CreateGitDepot",
            "ProjectId": project.Id,
            "DepotName": repo_name,
            "Shared": False,
            "Description": ""
            }
        r = self.sess.post(url, json=data)
        if r.status_code == 200:
            print(f'create repo {repo_name} success', data,r.json())
            return True
        else:
            return False

    def delete(self, repo_name: str):
        """delete a repo"""
        repo = self.get_repo_info(repo_name=repo_name)
        url = f'{self._host}/open-api/repos'
        data = {
            "Action": "DeleteGitDepot",
            "DepotId": repo.Id
            }
        r = self.sess.post(url, json=data)
        if r.status_code == 200:
            print(f'delete repo {repo_name} success', data,r.json())
            return True
        else:
            return False

    def pull(self, local_repo_path: str):
        ''' pull a repo from remote
            Args: local_repo_path: local repo path
         '''
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        print(f'pull repo:{self.username}/{repo_name} from coding')
        os.chdir(local_repo_path)
        try:
            os.system('git remote remove origin_coding')
        except Exception as e:
            pass
        os.system(
            f'git remote add origin_coding https://{self.username}:{self.token}@e.coding.net/{self.username}/{self.project_name}/{repo_name}.git'
        )
        os.system('git pull origin_coding')
        os.system('git remote remove origin_coding')
        os.chdir('..')
        print('pull success')

    def push(self, local_repo_path: str):
        ''' push a local repo to remote
            Args: local_repo_path: local repo path
         '''
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        print(f'push repo:{self.username}/{repo_name} to coding')
        os.chdir(local_repo_path)

        os.system('git remote remove origin_coding')
        os.system(
            f'git remote add origin_coding https://{self.username}:{self.token}@e.coding.net/{self.username}/{self.project_name}/{repo_name}.git'
        )
        os.system('git push -u origin_coding')
        os.system('git remote remove origin_coding')
        os.chdir('..')
        print('push success')

    def clone(self, repo_name: str):
        pass

    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        if extractor == 'coding':
            return True
        else:
            return False
