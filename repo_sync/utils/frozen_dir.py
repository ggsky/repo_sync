#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2024/04/12
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   
"""
import sys  
import os  
   
def get_app_path() -> str:  
    """Returns the base application path."""  
    if hasattr(sys, 'frozen'):  
        # Handles PyInstaller  
        return os.path.dirname(sys.executable)  #使用 pyinstaller 打包后的 exe 目录
    # return os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # 没打包前的py目录
    return sys.path[0]
