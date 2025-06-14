#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/09/27 10:35:25
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   coding.net repo sync

两种授权： token 授权，OAuth2.0 授权

"""
import os,subprocess,sys
from repo_sync.platform.base_platform import BasePlatform
from .project import Project
from .repo import Repo
from repo_sync.utils.colors import bcolors
from repo_sync.utils.logger import logger

class CodingIE(BasePlatform):
    """coding util"""
    client_id = ''
    client_serect = ''
    _host = 'https://e.coding.net'  # 新版接口统一地址
    
    def __init__(self, username: str, token: str, host: str = None, params: dict = None) -> None:
        """init"""
        super().__init__(username, token)
        self.project_name = params.get('coding_project', '')
        self.repo_shared = False if params.get('coding_private', "true").lower() == 'true' else True
        self.url = f'{self._host}/open-api'
    
    def create_project(self):
        ''' create a project '''
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
        r = self.sess.post(self.url, json=data)
        if r.status_code == 200:
            res_data = r.json()
            logger.info(f'Create project success: {res_data}')
            return True
        else:
            logger.error(f'Failed to create project: {r.text}')
            return False
    
    def delete_project(self):
        data = {
            'Action': 'DeleteOneProject',
            'ProjectId': 0,
        }
        r = self.sess.post(self.url, json=data)
        if r.status_code == 200:
            res_data = r.json()
            logger.info(f'Delete project success: {res_data}')
            return True
        else:
            logger.error(f'Failed to delete project: {r.text}')
            return False
    
    def get_project_list(self):
        pass
    
    def get_repo_list(self, username: str = None) -> list:
        """ get repo list from a project
            Args: username: the target username may not self.username
            return: repo list
        """
        data = {
            'Action': 'DescribeTeamDepotInfoList',
            'ProjectName': self.project_name,
            'PageNumber': 1,
            'PageSize': 50
        }
        r = self.sess.post(self.url, json=data)
        if r.status_code == 200:
            res_data = r.json()
            try:
                totalPage = res_data['Response']["DepotData"]["Page"]["TotalPage"]
                if totalPage > 0:
                    currentPage = 1
                    DepotList = []
                    # the first page
                    DepotList = res_data['Response']["DepotData"]["Depots"]
                    for repo in DepotList:
                        repo_model = Repo(
                            Id=repo['Id'],
                            Name=repo['Name'],
                            HttpsUrl=repo['HttpsUrl'],
                            ProjectId=repo['ProjectId'],
                            SshUrl=repo['SshUrl'],
                            WebUrl=repo['WebUrl'],
                            ProjectName=repo['ProjectName'],
                            Description=repo['Description'],
                            CreatedAt=repo['CreatedAt'],
                            GroupId=repo['GroupId'],
                            GroupName=repo['GroupName']
                        )
                        DepotList.append(repo_model)
                    
                    currentPage += 1
                    # the other pages
                    for i in range(2, totalPage + 1):
                        data = {
                            'Action': 'DescribeTeamDepotInfoList',
                            'ProjectName': self.project_name,
                            'PageNumber': currentPage,
                            'PageSize': 50
                        }
                        r = self.sess.post(self.url, json=data)
                        res_data = r.json()
                        DepotList = res_data['Response']["DepotData"]["Depots"]
                        for repo in DepotList:
                            repo_model = Repo(
                                Id=repo['Id'],
                                Name=repo['Name'],
                                HttpsUrl=repo['HttpsUrl'],
                                ProjectId=repo['ProjectId'],
                                SshUrl=repo['SshUrl'],
                                WebUrl=repo['WebUrl'],
                                ProjectName=repo['ProjectName'],
                                Description=repo['Description'],
                                CreatedAt=repo['CreatedAt'],
                                GroupId=repo['GroupId'],
                                GroupName=repo['GroupName']
                            )
                            DepotList.append(repo_model)
                        currentPage += 1
                    return DepotList
                else:
                    logger.warning(f'Cannot find repo in project {self.project_name}')
            except Exception as e:
                logger.error(f'Error retrieving repo list: {str(e)}')
        
    def _repo_exists(self, repo_name: str):
        """get repo list"""
        data = {
            'Action': 'DescribeTeamDepotInfoList',
            'ProjectName': self.project_name,
            'DepotName': repo_name,
            'PageNumber': 1,
            'PageSize': 50
        }
        r = self.sess.post(self.url, json=data)
        if r.status_code == 200:
            res_data = r.json()
            try:
                if res_data['Response']["DepotData"]["Page"]["TotalRow"] > 0:
                    DepotList = res_data['Response']["DepotData"]["Depots"]
                    for repo in DepotList:
                        if repo['Name'] == repo_name:
                            depot = Repo(
                                Id=repo['Id'],
                                Name=repo['Name'],
                                HttpsUrl=repo['HttpsUrl'],
                                ProjectId=repo['ProjectId'],
                                SshUrl=repo['SshUrl'],
                                WebUrl=repo['WebUrl'],
                                ProjectName=repo['ProjectName'],
                                Description=repo['Description'],
                                CreatedAt=repo['CreatedAt'],
                                GroupId=repo['GroupId'],
                                GroupName=repo['GroupName']
                            )
                        break
                    if depot is None:
                        logger.warning(f'Cannot find repo {repo_name} in project {self.project_name}')
                    else:
                        logger.info(f'Find repo {repo_name} in project {self.project_name}')
                    return depot
                else:
                    logger.warning(f'Cannot find repo {repo_name} in project {self.project_name}')
            except Exception as e:
                logger.error(f'Cannot find repo {repo_name} in project {self.project_name}: {str(e)}')
    
    def get_project_info(self) -> Project:
        data = {
            "Action": "DescribeCodingProjects",
            "ProjectName": self.project_name,
            "DepotName": "",
            "PageNumber": 1,
            "PageSize": 50
        }
        r = self.sess.post(self.url, json=data)
        if r.status_code == 200:
            res_data = r.json()
            try:
                if res_data['Response']["Data"]["TotalCount"] > 0:
                    ProjectList = res_data['Response']["Data"]["ProjectList"]
                    project = Project(
                        Id=ProjectList[0]['Id'],
                        Name=ProjectList[0]['Name'],
                        DisplayName=ProjectList[0]['DisplayName'],
                        Description=ProjectList[0]['Description'],
                        TeamOwnerId=ProjectList[0]['TeamOwnerId'],
                        TeamId=ProjectList[0]['TeamId']
                    )
                    return project
            except Exception as e:
                logger.error(f'Error retrieving project info: {str(e)}')
                logger.error(f'{res_data}')
    
    def create_repo(self, repo_name: str):
        """create a repo"""
        # get project id
        project = self.get_project_info()
        if project is not None:
            repo = self._repo_exists(repo_name=repo_name)
            if repo is None:
                data = {
                    "Action": "CreateGitDepot",
                    "ProjectId": project.Id, 
                    "DepotName": repo_name,
                    "Shared": self.repo_shared,
                    "Description": "this is your first depot"
                }
                r = self.sess.post(self.url, json=data)
                if r.status_code == 200:
                    logger.info(f'Create repo {repo_name} success')
                    logger.info(f'https://e.coding.net/{self.username}/{self.project_name}/{repo_name}')
                    return True
                else:
                    logger.error(f'Failed to create repo')
                    return False
        else:
            logger.error(f"Project: {self.project_name} does not exist, cannot create repo in it.")
    
    def delete(self, repo_name: str):
            """delete a repo"""
            repo = self._repo_exists(repo_name=repo_name)
            if repo is not None:
                data = {
                    "Action": "DeleteGitDepot",
                    "DepotId": repo.Id
                    }
                r = self.sess.post(self.url, json=data)
                if r.status_code == 200:
                    logger.info(f'delete repo {repo_name} success')
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
        logger.info(f'pull repo:{self.username}/{repo_name} from coding')
        os.chdir(local_repo_path)
        try:
            os.system('git remote remove origin_coding')
        except Exception as e:
            pass
        os.system(
            f'git remote add origin_coding https://{self.username}:{self.token}@e.coding.net/{self.username}/{self.project_name}/{repo_name}.git'
        )
        result = subprocess.run(
            ['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        os.system(f'git pull origin_coding {current_branch}')
        os.system('git remote remove origin_coding')
        os.chdir('..')
        logger.info(f'pull from coding success')

    def push(self, local_repo_path: str):
        ''' push a local repo to remote
            Args: local_repo_path: local repo path
            '''
        # check if remote repo is exist

        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        logger.info(f'push repo:{self.username}/{repo_name} to coding')
        self.create_repo(repo_name=repo_name)
        os.chdir(local_repo_path)

        os.system('git remote remove origin_coding')
        os.system(
            f'git remote add origin_coding https://{self.username}:{self.token}@e.coding.net/{self.username}/{self.project_name}/{repo_name}.git'
        )
        result = subprocess.run(
            ['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        os.system(f'git pull origin_coding {current_branch}')
        
        os.system(f'git push -u origin_coding {current_branch}')
        os.system('git remote remove origin_coding')
        os.chdir('..')
        logger.info(f'push to coding success')

    def clone(self, repo_path: str):
        ''' clone all repo from remote
            Args: repo_name: repo name
            '''
        repos = self.get_repo_list()
        for repo in repos:
            try:
                cmd = f'git clone https://{self.username}:{self.token}@e.coding.net/{self.username}/{self.project_name}/{repo["Name"]}.git {repo_path}/{repo["Name"]}'
                os.system(cmd)
                logger.info(f'clone success')
            except Exception as e:
                pass

    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        if extractor == 'coding':
            return True
        else:
            return False

