#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2024/03/21
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   YAML configuration reader
'''

import os
import yaml
from typing import Dict, Any, Optional

class ConfigReader:
    """YAML configuration reader"""
    
    def __init__(self, config_path: str = 'config.yml'):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config file: {e}")
            return {}
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """Get platform configuration"""
        if not self.config or 'accounts' not in self.config:
            return {}
        
        platform_config = self.config['accounts'].get(platform, {})
        if not platform_config or not platform_config.get('enable'):
            return {}
        
        # Find the enabled account
        for account_id, account_config in platform_config.items():
            if account_id == 'enable':
                continue
            return account_config
        
        return {}
    
    def get_platform_accounts(self, platform: str) -> list:
        """Get all accounts for a platform"""
        if not self.config or 'accounts' not in self.config:
            return []
        
        platform_config = self.config['accounts'].get(platform, {})
        if not platform_config or not platform_config.get('enable'):
            return []
        
        accounts = []
        for account_id, account_config in platform_config.items():
            if account_id == 'enable':
                continue
            accounts.append(str(account_id))
        
        return sorted(accounts)
    
    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config.get('log', {})
    
    def get_account_config(self, platform: str, account_id: str) -> Dict[str, Any]:
        """Get specific account configuration"""
        if not self.config or 'accounts' not in self.config:
            return {}
        
        platform_config = self.config['accounts'].get(platform, {})
        if not platform_config or not platform_config.get('enable'):
            return {}
        
        return platform_config.get(str(account_id), {}) 