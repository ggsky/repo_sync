import requests,csv,os
from repo_sync.repo import Repo
from repo_sync.utils.colors import bcolors

class BasePlatform(object):
    """base platform"""
    
    repo_list_path = 'repo_list.csv'

    def __init__(self, username:str, token:str ) -> None:
        """init"""
        self.sess = requests.Session()
        self.username = username
        self.token = token
        self.repos = []
        self.sess.headers.update(
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
                'Authorization': f'token {self.token}',
            }
        )
        if os.path.exists(self.repo_list_path):
            with open(self.repo_list_path, 'r', encoding='utf8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    repo = Repo()
                    repo.__dict__ = row
                    self.repos.append(repo)

    def create_repo(self, repo_name: str):
        """create a repo"""
        raise NotImplementedError('crawl not implemented')

    def delete(self, repo_name: str):
        """delete a repo, maybe request a confirm by input"""
        raise NotImplementedError('crawl not implemented')
    
    def clone(self, repo_name: str):
        """clone a repo"""
        raise NotImplementedError('crawl not implemented')
    
    def pull(self, repo_path: str):
        """pull a repo"""
        raise NotImplementedError('crawl not implemented')

    def push(self, repo_path: str):
        """push a repo"""
        raise NotImplementedError('crawl not implemented')

    @classmethod
    def suitable(cls, extractor: str) -> bool:
        """check if this extractor is suitable for this platform"""
        raise NotImplementedError('crawl not implemented')

    def save_csv(self):
        with open(self.repo_list_path, 'w', newline='') as f:
            if len(self.repos) == 0:
                print(f"{bcolors.WARNING}repo list is empty, please delete repo_list.csv and try again{bcolors.ENDC}")
                return
            writer = csv.DictWriter(f, fieldnames=self.repos[0].__dict__.keys(), lineterminator='\n')
            writer.writeheader()
            for repo in self.repos:
                writer.writerow(repo.__dict__)
