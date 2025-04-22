#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/09/26 16:30:04
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   
"""


class Repo(object):
    """repo model"""

    def __init__(self):
        self.id = None
        self.platform = "github"
        self.name = None
        self.url = None
        self.remote_url = None
        self.description = None
        self.language = None
        self.star = None
        self.fork = None
        self.watch = None
        self.issues = None
        self.local_path = None
