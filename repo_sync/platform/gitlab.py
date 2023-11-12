#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/09/27 12:16:56
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   gitlab async
"""
import os
import json,re 
import csv
from .base_platform import BasePlatform
from repo_sync.repo import Repo

class GitlabIE(BasePlatform):
    """gitlab async"""

    def __init__(self, username:str, token:str,host:str =None ,params: dict = None) -> None:
        super().__init__(username=username, token=token)
        self.host = self.host or 'https://gitlab.com'
        self.sess.headers.update({"Authorization": f"Bearer {self.token}"})

    def create_repo(self, repo_name: str):
        """create a repo
            and save project id to csv: gitlab_repo_list.csv
        """
        url = f"{self.host}/api/v4/projects"
        payload = {
            "name": repo_name,
            "visibility": "private",
        }
        r = self.sess.post(url, data=json.dumps(payload))
        if r.status_code != 201:
            print(
                "create repo {} failed, status code {}".format(repo_name, r.status_code)
            )
            return
        print("create repo {} success".format(repo_name))
        for repo in self.repos:
            if repo.name == repo_name:
                repo.url = r.json()["web_url"]
                repo.id = r.json()["id"]
                break
        self.save_csv()
        
    def delete(self, repo_name: str):
        """delete a repo,
            find project id from csv: gitlab_repo_list.csv
        """
        project_id=""
        r = self.sess.get(f"{self.host}/api/v4/users/{self.username}/projects?search={repo_name}")
        if r.status_code == 200:
            project_id = r.json()[0]["id"]
            url = f"{self.host}/api/v4/projects/{project_id}"
            response = self.sess.delete(url)
            if response.status_code == 202:
                print(f"Repository: {repo_name} deleted from gitlab successfully!")
            else:
                print(
                    f"Failed to delete repository: {repo_name} from gitlab. Error {response.status_code}: {response.text}"
                )
        else:
            print(f"Failed to delete repository: {repo_name} from gitlab. Error {r.status_code}: {r.text}")
       
    def get_repo_list(self, username: str)->list:
        """get repo list"""
        url = f"{self.host}/api/v4/users/{username}/projects"
        r = self.sess.get(url)
        if r.status_code != 200:
            print("get repo list failed, status code {}".format(r.status_code))
            return
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

    def pull(self):
        pass

    def push(self, local_repo_path: str):
        """push a local repo to remote
        Args:
            local_repo_path (str): local repo path
        """
        repo_name = local_repo_path.split(os.path.sep)[-1]
        print(f"push repo:{self.username}/{repo_name} to gitlab")
        self.create_repo(repo_name)
        pur_host = re.search(r'(?<=//)[^/]+', self.host).group()

        os.chdir(local_repo_path)

        os.system("git remote remove origin_gitlab")
        os.system(
            f"git remote add origin_gitlab https://{self.username}:{self.token}@{pur_host}/{self.username}/{repo_name}.git"
        )
        os.system("git push -u origin_gitlab")
        os.system("git remote remove origin_gitlab")
        os.chdir("..")

    def clone(self):
        pass

    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        if extractor == 'gitlab':
            return True
        else:
            return False
