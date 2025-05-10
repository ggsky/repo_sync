#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/09/27 12:16:56
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   gitlab async
"""
import os
import json
import re
import csv
import subprocess
from .base_platform import BasePlatform
from repo_sync.models import Repo
from repo_sync.utils.logger import logger

class GitlabIE(BasePlatform):
    """gitlab async"""
    def __init__(self, username: str, token: str, host: str = None, params: dict = None) -> None:
        super().__init__(username=username, token=token)
        self.host = host or 'https://gitlab.com'
        self.sess.headers.update({"Authorization": f"Bearer {self.token}"})
        self.repo_private = 'private' if params.get('gitlab_private', "true").lower() == 'true' else 'public'
    
    def create_repo(self, repo_name: str):
        """create a repo
        and save project id to csv: gitlab_repo_list.csv
        """
        if not self._repo_exists(repo_name):
            url = f"{self.host}/api/v4/projects"
            payload = {
                "name": repo_name,
                "visibility": self.repo_private,
            }
            r = self.sess.post(url, data=json.dumps(payload))
            if r.status_code != 201:
                logger.error(f"create repo {repo_name} failed, status code {r.status_code}")
                return
            logger.info(f"create repo {repo_name} success")
            logger.info(f'{self.host}/{self.username}/{repo_name}')
            # for repo in self.repos:
            #     if repo.name == repo_name:
            #         repo.url = r.json()["web_url"]
            #         repo.id = r.json()["id"]
            #         break
            # self.save_csv()
    
    def delete(self, repo_name: str):
        """delete a repo,
        find project id from csv: gitlab_repo_list.csv
        """
        project_id = ""
        r = self.sess.get(f"{self.host}/api/v4/users/{self.username}/projects?search={repo_name}")
        if r.status_code == 200:
            try:
                project_id = r.json()[0]["id"]
                url = f"{self.host}/api/v4/projects/{project_id}"
                response = self.sess.delete(url)
                if response.status_code == 202:
                    logger.info(f"Repository: {repo_name} deleted from gitlab successfully!")
                else:
                    logger.error(
                        f"Failed to delete repository: {repo_name} from gitlab. Error {response.status_code}: {response.text}"
                    )
            except Exception as e:
                logger.error(f"Failed to delete repository: {repo_name} from gitlab. Error {e}, check repo is exist first.")
        else:
            logger.error(f"Failed to delete repository: {repo_name} from gitlab. Error {r.status_code}: {r.text}")
    
    def get_repo_list(self, username: str) -> list:
        """get repo list"""
        url = f"{self.host}/api/v4/users/{username}/projects"
        r = self.sess.get(url)
        if r.status_code != 200:
            logger.error(f"get repo list failed, status code {r.status_code}")
            return []
        repo_list = []
        for res in r.json():
            repo = Repo()
            repo.name = res["name"]
            repo.url = res["web_url"]
            repo.local_path = None
            repo.id = res["id"]
            repo_list.append(repo)
        self.save_csv()
        return repo_list
    
    def pull(self, local_repo_path: str):
        """push a local repo to remote
        Args:
            local_repo_path (str): local repo path
        """
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        logger.info(f"pull repo:{self.username}/{repo_name} from gitlab")
        self.create_repo(repo_name)
        pur_host = re.search(r'(?<=//)[^/]+', self.host).group()
        os.chdir(local_repo_path)
        os.system("git remote remove origin_gitlab")
        os.system(
            f"git remote add origin_gitlab https://{self.username}:{self.token}@{pur_host}/{self.username}/{repo_name}.git"
        )
        result = subprocess.run(
            ['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        os.system(f'git pull origin_gitlab {current_branch}')
        os.system("git remote remove origin_gitlab")
        os.chdir("..")
        logger.info(f"pull repo:{self.username}/{repo_name} from gitlab success")
    
    def push(self, local_repo_path: str):
        """push a local repo to remote
        Args:
            local_repo_path (str): local repo path
        """
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        logger.info(f"push repo:{self.username}/{repo_name} to gitlab")
        self.create_repo(repo_name)
        pur_host = re.search(r'(?<=//)[^/]+', self.host).group()
        os.chdir(local_repo_path)
        os.system("git remote remove origin_gitlab")
        os.system(
            f"git remote add origin_gitlab https://{self.username}:{self.token}@{pur_host}/{self.username}/{repo_name}.git"
        )
        result = subprocess.run(
            ['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        os.system(f'git pull origin_gitlab {current_branch}')
        os.system(f"git push -u origin_gitlab {current_branch}")
        os.system("git remote remove origin_gitlab")
        os.chdir("..")
        logger.info(f"push repo:{self.username}/{repo_name} to gitlab success")
    
    def clone(self):
        pass

    def _repo_exists(self, repo_name: str):
        """ check if a repo exists
        if not exist, return [] empty list
        """
        project_id = ""
        r = self.sess.get(f"{self.host}/api/v4/users/{self.username}/projects?search={repo_name}")
        if r.status_code == 200:
            try:
                project_id = r.json()[0]["id"]
                logger.info(f'repo: {repo_name} is existed.')
                return True
            except Exception as e:
                return False
            
    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        return extractor == 'gitlab'
