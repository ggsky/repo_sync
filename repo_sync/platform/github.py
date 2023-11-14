#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/06/04 13:43:46
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   github get a user all open source repo
"""
import os
import json
import csv, subprocess
from repo_sync.repo import Repo
from .base_platform import BasePlatform

class GithubIE(BasePlatform):
    """github util"""

    _host = 'https://api.github.com'

    def __init__(self, username:str, token:str,host:str =None ,params: dict = None) -> None:
        """init"""
        super().__init__(username=username, token=token)
        # 60 unauthenticated requests per hour
        if self.token:
            self.sess.headers.update({'Accept': 'application/vnd.github.v3+json'})

    def create_repo(self, repo_name: str):
        """create a repo"""
        url = f'{self._host}/user/repos'
        payload = {
            'name': repo_name,
            'private': True,
            'has_issues': True,
            'has_projects': False,
            'has_wiki': False,
        }
        r = self.sess.post(url, data=json.dumps(payload))
        if r.status_code != 201:
            print(
                'create repo {} failed, status code {}'.format(repo_name, r.status_code)
            )
            return
        print('create repo {} success'.format(repo_name))

    def delete(self, repo_name: str):
        """delete a repo, maybe request a confirm by input"""
        # print("delete repo:"+repo_name)
        url = f'{self._host}/repos/{self.username}/{repo_name}'

        response = self.sess.delete(url)
        if response.status_code == 204:
            print(f'Repository:{repo_name} deleted from github successfully!')
        else:
            print(
                f'Failed to delete repository: {repo_name} from github. Error {response.status_code}: {response.text}'
            )
        print(f'delete repo:{repo_name} from github success')

    def repo_exists(self, repo_name: str):
        """check if a repo exists"""
        url = f'{self._host}/repos/{self.username}/{repo_name}'
        print('check repo:' + repo_name)
        try:
            response = self.sess.get(url)
            if response.status_code == 200:
                return True
        except Exception as e:
            return False

    def pull(self, local_repo_path: str):
        """pull a repo"""
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        print(f'pull repo:{self.username}/{repo_name} from github')
        
        os.chdir(local_repo_path)
        os.system('git remote remove origin_github')
        os.system(
            f'git remote add origin_github  https://{self.username}:{self.token}@github.com/{self.username}/{repo_name}.git')
        result = subprocess.run(
            ['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True)
        current_branch = result.stdout.strip()
        os.system(f'git pull origin_github {current_branch}')
        os.system('git remote remove origin_github')
        os.chdir('..')
        print('pull from github success')

    def clone(self, repo_name: str):
        pass
    
    def push(self, local_repo_path: str):
        """push a local repo to remote"""
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        print(f'push repo:{self.username}/{repo_name} to github')
        if not self.repo_exists(repo_name):
            self.create_repo(repo_name)
        os.chdir(local_repo_path)

        os.system('git remote remove origin_github')
        os.system(
            f'git remote add origin_github https://{self.username}:{self.token}@github.com/{self.username}/{repo_name}.git'
        )
        result = subprocess.run(['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True)
        current_branch = result.stdout.strip()
        os.system(f'git pull origin_github {current_branch}')
        
        os.system(f'git push -u origin_github {current_branch}')
        os.system('git remote remove origin_github')
        os.chdir('..')

    def get_repo_list(self) -> list:
        """get all repo list of a user"""
        if os.path.exists(self.repo_list_path):
            print(
                'repo is exist, please read from {} file'.format(self.repo_list_path)
            )
            with open(self.repo_list_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    repo = Repo()
                    repo.__dict__ = row
                    self.repos.append(repo)
        else:
            page_num = 1
            url = '{}/users/{}/repos'.format(self._host, self.username)
            while True:
                r = self.sess.get(url, params={'type': 'all', 'page': page_num})
                if r.status_code != 200:
                    print(
                        'request url {} failed, status code {}'.format(
                            url, r.status_code
                        )
                    )
                    return
                # rate limit
                repo_list = r.json()
                for repo in repo_list:
                    repo_obj = Repo()
                    repo_obj.name = repo.get('name')
                    repo_obj.url = repo.get('html_url')
                    repo_obj.description = repo.get('description')
                    repo_obj.language = repo.get('language')
                    repo_obj.star = repo.get('stargazers_count')
                    repo_obj.fork = repo.get('forks_count')
                    repo_obj.watch = repo.get('watchers_count')
                    self.repos.append(repo_obj)
                self.repos.sort(key=lambda x: x.star, reverse=True)
                # Link: <https://api.github.com/user/123456/repos?page=2>; rel="next", <https://api.github.com/user/123456/repos?page=3>; rel="last"
                links = r.headers.get('Link')

                if not links or 'rel="next"' not in links:
                    break

                next_url = None
                for link in links.split(','):
                    if 'rel="next"' in link:
                        next_url = link.split(';')[0].strip('<>')
                        break

                # Break loop if next URL is not valid
                if not next_url:
                    break

                # Increment page number for next iteration
                page_num += 1
            self.save_csv()
        return self.repos

    def _clone_all_repo(self):
        """cloen all repo"""
        for repo in self.repos:
            os.system('git clone {}'.format(repo.url))

    def clone_user_repos(self):
        """clone all repo of a user"""
        # if github.csv exist, read it
        if os.path.exists(self.repo_list_path):
            with open(self.repo_list_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row[0] == 'name':
                        continue
                    repo = Repo()
                    repo.__dict__ = row
                    self.repos.append(repo)
        else:
            self.get_repo_list(self.username)
        self._clone_all_repo()

    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        if extractor == 'github':
            return True
        else:
            return False
