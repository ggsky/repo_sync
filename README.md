# repo_sync

跨平台项目同步工具

由于项目众多，单一通过自己的代码托管平台存在一定风险。此项目将定期将代码同步到其他平台，以防止代码丢失。

* github
* gitlab
* gitee
* coding

## Usage

比如把 data/repo.txt 中的项目同步到 github 上：
```
python repo_sync.py --debug true --repo data/repo.txt --type github
```

把 data/repo.txt 中的项目同步到 gitlab 上：
```
python repo_sync.py --type gitlab
```
