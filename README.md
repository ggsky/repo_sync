# repo_sync
[![](https://img.shields.io/badge/version-1.4.0-brightgreen.svg)](https://git.yoqi.me/lyq/repo_sync)
[![](https://img.shields.io/badge/Python-3.11.5-brightgreen.svg)](https://git.yoqi.me/lyq/repo_sync)



跨平台项目同步工具

由于项目众多，单一通过自己的代码托管平台存在一定风险。此项目将定期将代码同步到其他平台，以防止代码丢失。

* github
* gitlab
* gitee
* coding
* gitea,gogs


## Usage

windows 下载 [release]()使用即可

## Develop

```
python main.py --help
python main.py create --platform gitlab --repo_path F:\workspace\python\repo_sync

# clone all repo to local path
python main.py clone --platform coding --repo_path F:\workspace\python\repo_sync
```


## License

Licensed under the [Apache 2.0](LICENSE) © [liuyuqi.gov@msn.cn](https://github.com/jianboy)


## Reference

* [gitlab api](https://docs.gitlab.com/ee/api/)