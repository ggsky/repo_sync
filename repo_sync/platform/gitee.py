#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/11/09 17:40:42
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   gitee async

"""
from .base_platform import BasePlatform
import csv
import os
from repo_sync.repo import Repo

class GiteeIE(BasePlatform):
    """gitee async"""

    _host = 'https://gitee.com'
    _api = _host + '/api/v5'

    def __init__(self, username:str, token:str,host:str =None ,params: dict = None) -> None:
        super().__init__(username=username, token=token)
        self.sess.headers.update({'Content-Type': 'multipart/form-data'})

    def create_repo(self, repo_name: str):
        """create a repo"""        
        url = f'{self._api}/user/repos'
        form_data = {'name': repo_name, 'private': True}
        r = self.sess.post(url, params=form_data)
        if r.status_code != 201:
            print(
                'create repo {} failed, status code {}'.format(repo_name, r.status_code)
            )
            return
        print('create repo {} success'.format(repo_name))

    def delete(self, repo_name: str):
        """delete a repo"""
        # print("delete repo:"+repo_name)
        url = f'{self._api}/repos/{self.username}/{repo_name}'

        response = self.sess.delete(url)
        if response.status_code == 204:
            print(f'Repository: {repo_name} deleted from gitee successfully!')
        else:
            print(
                f'Failed to delete repository: {repo_name} from github. Error {response.status_code}: {response.text}'
            )

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
            print('get repo list failed, status code {}'.format(r.status_code))
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
        print(f'pull repo:{self.username}/{repo_name} from gitee')
        os.chdir(local_repo_path)
        os.system('git remote remove origin_gitee')
        os.system(
            f'git remote add origin_gitee https://{self.username}:{self.token}@gitee.com/{self.username}/{repo_name}.git'
        )
        os.system('git pull origin_gitee')
        os.system('git remote remove origin_gitee')
        os.chdir('..')
        print('pull from gitee success')
                 
    def push(self, local_repo_path: str):
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        print(f'push repo:{self.username}/{repo_name} to gitee')
        os.chdir(local_repo_path)
        os.system('git remote remove origin_gitee')
        os.system(
            f'git remote add origin_gitee https://{self.username}:{self.token}@gitee.com/{self.username}/{repo_name}.git'
        )
        os.system('git push -u origin_gitee')
        os.system('git remote remove origin_gitee')
        os.chdir('..')
        print('push to gitee success')

    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        if extractor == 'gitee':
            return True
        else:
            return False
