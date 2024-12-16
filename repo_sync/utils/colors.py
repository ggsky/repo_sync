#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2024/07/22
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   控制台颜色
"""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


if __name__=='__main__':
    print(bcolors.HEADER+"Hello World!"+bcolors.ENDC)
    print(bcolors.OKBLUE+"Hello World!"+bcolors.ENDC)
    print(bcolors.OKGREEN+"Hello World!"+bcolors.ENDC)
    print(bcolors.WARNING+"Hello World!"+bcolors.ENDC)
    print(bcolors.FAIL+"Hello World!"+bcolors.ENDC)
    print(bcolors.BOLD+"Hello World!"+bcolors.ENDC)
    print(bcolors.UNDERLINE+"Hello World!"+bcolors.ENDC)
