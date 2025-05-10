#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/04/27 02:55:59
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   
'''
from repo_sync import main, gui_main
import sys

if __name__=='__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'gui':
        gui_main()
    else:
        main()
