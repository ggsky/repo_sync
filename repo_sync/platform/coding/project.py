#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/09/27 11:15:55
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   project manger
'''
import os,sys,re,requests,json

class Project(object):
    
    host="https://e.coding.net/open-api"   
    def __init__(self, Id, Name, DisplayName, Description, TeamOwnerId, TeamId) -> None:
        self.Id = Id
        self.Name = Name
        self.DisplayName = DisplayName
        self.Description = Description
        self.TeamOwnerId = TeamOwnerId
        self.TeamId= TeamId

    def create_project(self):
        ''' 创建项目 '''
        # https://{your-team}.coding.net/api/user/{user}/project
        pass
    
    def delete_project(self):
        ''' 删除项目 '''
        # https://{your-team}.coding.net/api/user/{user}/project/{project}
        pass
    
    def get_project(self):
        ''' 查询项目信息 '''
        # https://{your-team}.coding.net/api/user/{user}/project/{project}
        url=self.host + "/open-api?Action=DescribeOneProject"
        payload = {
            
        }
            
    def get_project_uesr(self):
        ''' 查询项目成员 '''
        # https://{your-team}.coding.net/api/user/{user}/project/{project}/members
        pass
 