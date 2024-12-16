#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2024/12/16 19:26:29
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   hauwei and csdn'

api docs:
https://docs.gitcode.com/docs/openapi/guide/

api 和 gitcode 类似
'''
from .base_platform import BasePlatform
from repo_sync.utils.colors import bcolors
import os, subprocess
class GitcodeIE(BasePlatform):
    """ gitcode platform """
    
    def __init__(self, username:str, token:str, host:str =None ,params: dict = None) -> None:
        super().__init__(username=username,token=token)
        self.sess.headers.update(
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
                'Authorization': f'Bearer {self.token}',
            }
        )
        self._host = 'https://api.gitcode.com' if host is None else host
        self._api = self._host + '/api/v5'
        self.repo_private = True if params.get('gitcode_private', "true").lower() == 'true' else False

    
    def create_repo(self, repo_name: str):
        """ create a repo """
        if not self._repo_exists(repo_name=repo_name):
            
            url = f'{self._api}/user/repos'
            form_data = {
                'name': repo_name, 
                'private': self.repo_private,
            }
            r = self.sess.post(url, params=form_data)
            if r.status_code != 200:
                print(bcolors.FAIL + f'create repo {repo_name} failed, status code {r.status_code}' + bcolors.ENDC)
                return
            print(bcolors.OKGREEN + f'create repo {repo_name} success' + bcolors.ENDC)
    
    def delete(self, repo_name: str):
        """ delete a repo """
        url = f'{self._api}/repos/{self.username}/{repo_name}'
        response = self.sess.delete(url)
        if response.status_code == 204:
            print(bcolors.OKBLUE + f'Repository: {repo_name} deleted from gitcode successfully!' + bcolors.ENDC)
        else:
            print(bcolors.FAIL + f'Failed to delete repository: {repo_name} from gitcode. Error {response.status_code}: {response.text}' + bcolors.ENDC)
    

    def get_repo_list(self) -> list:
        """ get repo list """
        pass
    
    def clone(self):
        pass
        
    def push(self, local_repo_path: str):
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        print(bcolors.WARNING + f'push repo:{self.username}/{repo_name} to gitcode' + bcolors.ENDC)
        self.create_repo(repo_name)
        os.chdir(local_repo_path)
        os.system('git remote remove origin_gitcode')
        os.system(f'git remote add origin_gitcode https://{self.username}:{self.token}@gitcode.com/{self.username}/{repo_name}.git')
        
        result = subprocess.run(['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        
        os.system(f'git pull origin_gitcode {current_branch}')
        os.system(f'git push -u origin_gitcode {current_branch}')
        os.system('git remote remove origin_gitcode')
        os.chdir('..')
        
        print(bcolors.OKGREEN + 'push to gitcode success' + bcolors.ENDC)

    def pull(self, local_repo_path: str):
        if local_repo_path[-1] == os.path.sep:
            local_repo_path = local_repo_path[:-1]
        repo_name = local_repo_path.split(os.path.sep)[-1]
        print(bcolors.WARNING + f'pull repo:{self.username}/{repo_name} from gitcode' + bcolors.ENDC)
        
        os.chdir(local_repo_path)
        os.system('git remote remove origin_gitcode')
        os.system(f'git remote add origin_gitcode https://{self.username}:{self.token}@gitcode.com/{self.username}/{repo_name}.git')
        
        result = subprocess.run(['git', 'symbolic-ref', '--short', 'HEAD'], capture_output=True, text=True, encoding='utf-8')
        current_branch = result.stdout.strip()
        os.system(f'git pull origin_gitcode {current_branch}')
        os.system('git remote remove origin_gitcode')
        os.chdir('..')
        
        print(bcolors.OKGREEN + 'pull from gitcode success' + bcolors.ENDC)
    
    def _repo_exists(self, repo_name: str) -> bool:
        """ check if repo exists """
        url = f"{self._api}/repos/{self.username}/{repo_name}/contributors"
        try:
            response = self.sess.get(url)
            if response.status_code == 200:
                print(f'{bcolors.OKGREEN}repo: {repo_name} is existed. {bcolors.ENDC}')
                return True
        except Exception as e:
            return False

    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        if extractor == 'gitcode':
            return True
        else:
            return False
        
