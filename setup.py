#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 获取版本号
version = {}
with open(os.path.join("repo_sync", "version.py")) as f:
    exec(f.read(), version)

setup(
    name="repo_sync",
    version=version.get("__version__", "0.0.1"),
    description="Repository synchronization tool",
    author="liuyuqi",
    author_email="liuyuqi.gov@msn.cn",
    url="https://github.com/jianboy/repo_sync",
    packages=find_packages(),
    install_requires=[
        "PyYAML",
        "PyQt5",
        "pywin32;platform_system=='Windows'",
    ],
    entry_points={
        "console_scripts": [
            "repo_sync=repo_sync:main",
        ],
        "gui_scripts": [
            "repo_sync_gui=main_gui:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
)
