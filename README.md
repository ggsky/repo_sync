# repo_sync

跨平台项目同步工具

由于项目众多，单一通过自己的代码托管平台存在一定风险。此项目将定期将代码同步到其他平台，以防止代码丢失。

* github
* gitlab
* gitee
* coding

## Usage

* 1、pc配置 github clone 权限
* 2、conf/config.json 中配置 github token 创建项目权限
* 3、data/repo.txt 中配置需要同步的项目
* 4、执行同步脚本：

比如把 data/repo.txt 中的项目同步到 github 上：
```
python repo_sync.py --debug true --repo data/repo.txt --type github
```

把 data/repo.txt 中的项目同步到 gitlab 上：
```
python repo_sync.py --type gitlab
```

## 计划任务

1、项目以 zhizhou/github 作为项目源，同步到其他平台。
2、同步项目最好每月定时执行一次，以防止代码丢失。

```bash
vim /etc/crontab

0 0 1 * * python repo_sync.py --type github
```
