#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/09/27 10:48:38
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   
"""
import requests, json


class Repo(object):
    ''' Depot info, repo info '''
    
    host = 'https://e.coding.net/open-api'

    def __init__(self,Id, Name, HttpsUrl, ProjectId, SshUrl, WebUrl, ProjectName, Description, CreatedAt, GroupId, GroupName):
        self.Id = Id
        self.Name = Name
        self.HttpsUrl = HttpsUrl
        self.ProjectId = ProjectId
        self.SshUrl = SshUrl
        self.WebUrl = WebUrl
        self.ProjectName = ProjectName
        self.Description = Description
        self.CreatedAt = CreatedAt
        self.GroupId = GroupId
        self.GroupName = GroupName

    def create_repo(self):
        """创建项目"""
        url = self.host + '/open-api?Action=CreateGitDepot'
        payload = {
            'ProjectId': 0,
            'DepotName': '',
            'Shared': True,
            'Description': '',
        }
        r = self.sess.post(url, data=json.dumps(payload))

    def delete_repo(self):
        """删除项目"""
        pass

    def get_repo(self):
        """查询项目信息"""
        pass

    def get_repo_user(self):
        """查询项目成员"""
        # https://{your-team}.coding.net/api/user/{user}/project/{project}/members
        pass
