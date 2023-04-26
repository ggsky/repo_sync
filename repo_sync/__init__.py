from repo_sync.base_repo import BaseRepo
from repo_sync.sync_utils import SyncUtils

def main():
    sync_utils = SyncUtils()
    sync_utils.run()