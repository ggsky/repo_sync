#!/bin/bash
# @Contact :   liuyuqi.gov@msn.cn
# @Time    :   2023/12/17 03:57:36
# @License :   (C)Copyright 2022 liuyuqi.
# @Desc    :   执行 /opt/repo_sync/repo_sync 命令
# 传入两个参数，/opt/repo_sync/repo_sync create --platform github --repo_path /home/workspace/xx
###############################################################################

function install() {
    echo "开始安装"
    cd /opt
    mkdir repo_sync
    cd repo_sync
    wget https://fileshare.yoqi.me/repo_sync/repo_sync
    chmod +x repo_sync
    echo '.env' >> .env
    echo "export PATH=$PATH:/opt/repo_sync" >> /etc/profile
    echo "安装完成"
}

function uninstall() {
    echo "开始卸载"
    rm -rf /opt/repo_sync
    sed -i '/repo_sync/d' /etc/profile
    echo "卸载完成"
}

# 打印logo，用户使用指南
function print_logo() {
    echo -e "\033[32
    
    repo sync 项目同步工具 v1.0
        作者：liuyuqi
    Usage:
        repo_sync create --platform github --repo_path /home/workspace/xx
        repo_sync delete --platform github --repo_path /home/workspace/xx
        repo_sync update --platform github --repo_path /home/workspace/xx
        repo_sync list --platform github --repo_path /home/workspace/xx
        repo_sync help
    \033[0m"
}

print_logo


while true; do
    echo "请输入操作，create(1),push(2),pull(3),delete(4), 回车默认1"
    read -p "请输入操作：" action
    if [ $action == 1 ] || [ $action == 2 ] || [ $action == 3 ] || [ $action == 4 ] || [ $action == 5 ] || [ $action == 6 ] || [ $action == 7 ]; then
        break
    fi
    
done

while true; do
    # 请输入平台，github(1),gitlab(2),coding(3),gitee(4),gogs(5)
    echo "请输入平台，github(1),gitlab(2),coding(3),gitee(4),gogs(5)"
    read -p "请输入平台：" platform
    if [ $platform == 1 ] || [ $platform == 2 ] || [ $platform == 3 ] || [ $platform == 4 ] || [ $platform == 5 ]; then
        if [ $platform == 1 ]; then
            platform="github"
        elif [ $platform == 2 ]; then
            platform="gitlab"
        elif [ $platform == 3 ]; then
            platform="coding"
        elif [ $platform == 4 ]; then
            platform="gitee"
        elif [ $platform == 5 ]; then
            platform="gogs"
        fi
        break
    fi
done

# 请输入仓库路径，/home/workspace/xx
echo "请输入仓库路径，/home/workspace/xx"
read -p "请输入仓库路径：" repo_path

cd /opt/repo_sync
if [ $action == 1 ]; then
    /opt/repo_sync/repo_sync create --platform $platform --repo_path $repo_path
elif [ $action == 2 ]; then
    /opt/repo_sync/repo_sync push --platform $platform --repo_path $repo_path
elif [ $action == 3 ]; then
    /opt/repo_sync/repo_sync pull --platform $platform --repo_path $repo_path
elif [ $action == 4 ]; then
    /opt/repo_sync/repo_sync delete --platform $platform --repo_path $repo_path
elif [ $action == 5 ]; then
    /opt/repo_sync/repo_sync update --platform $platform --repo_path $repo_path
elif [ $action == 6 ]; then
    /opt/repo_sync/repo_sync list --platform $platform --repo_path $repo_path
elif [ $action == 7 ]; then
    print_logo
else
    print_logo
fi
