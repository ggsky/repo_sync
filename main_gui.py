#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2023/04/27 02:55:59
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   repo_sync GUI入口

打包说明：
使用PyInstaller可以将此应用打包为单个可执行文件：
1. 安装必要的包: 
   pip install pyinstaller
   pip install -e .  # 以开发模式安装当前包

2. 打包命令: 
   pyinstaller --onefile --windowed --icon=icon.ico --add-data "repo_sync/config.yml;repo_sync" main_gui.py
   (如果有图标文件，可以通过--icon参数指定)

3. 打包后的可执行文件将位于dist目录中

注意：确保在打包前先安装repo_sync包，这样PyInstaller才能正确找到所有依赖。
'''
import sys
import os
import threading
import subprocess
import yaml
try:
    from PyQt5.QtWidgets import (
        QApplication, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
        QRadioButton, QPushButton, QButtonGroup, QGroupBox, QMessageBox, 
        QLineEdit, QScrollArea, QFileDialog, QFormLayout, QCheckBox, QTextEdit,
        QComboBox, QDialog, QDialogButtonBox, QGridLayout, QToolButton, QListWidget, QListWidgetItem,
        QSpacerItem
    )
    from PyQt5.QtCore import Qt, pyqtSignal, QObject
    HAS_QT = True
except ImportError:
    HAS_QT = False
    print("PyQt5 not installed, GUI mode not available")

# 直接导入repo_sync模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from repo_sync.repo_sync import RepoSync
    from repo_sync.version import __version__
    from repo_sync.utils.config_reader import ConfigReader
except ImportError:
    print("无法导入repo_sync模块，尝试直接导入...")
    try:
        from repo_sync import RepoSync
        from version import __version__
        from utils.config_reader import ConfigReader
    except ImportError:
        print("导入repo_sync模块失败，请确保repo_sync已正确安装")
        __version__ = "未知"
        
        # 创建一个空的RepoSync类作为替代
        class RepoSync:
            def __init__(self, params):
                self.params = params
            def run(self):
                print("RepoSync模块未找到，无法执行操作")

# 确保config.yml文件存在
def ensure_config_file():
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yml')
    if not os.path.exists(config_file):
        # 创建空的config.yml文件
        default_config = {
            'accounts': {
                'github': {
                    'enable': 1,
                    '1': {
                        'username': '',
                        'token': '',
                        'private': True
                    }
                }
            },
            'log': {
                'level': 'debug',
                'file': '/tmp/repo_sync.log',
                'max_size': '100MB',
                'max_backups': 3,
                'max_age': 7,
                'console_formatter': {
                    'level': 'debug',
                    'format': '%(asctime)s - %(levelname)s - %(message)s'
                },
                'file_formatter': {
                    'level': 'debug',
                    'format': '%(asctime)s - %(levelname)s - %(message)s'
                }
            }
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False)
    return config_file

class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 确保config.yml文件存在
        ensure_config_file()
        # 初始化account_lists字典
        self.account_lists = {}
        self.config_reader = ConfigReader()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建平台选择标签页
        self.platform_tabs = QTabWidget()
        
        # 平台配置
        self.platform_configs = {
            "github": ["username", "token", "private"],
            "gitlab": ["host", "username", "token", "private"],
            "gitee": ["username", "token", "private"],
            "gitcode": ["username", "token", "private"],
            "git.yoq.me": ["username", "token", "private"],
            "coding": ["username", "token", "project", "private"],
            "aliyun": ["compoanyid", "group_id", "username", "token", "private"],
            "cnb": ["username", "token", "private"]
        }
        
        # 为每个平台创建标签页
        self.platform_pages = {}
        for platform in self.platform_configs.keys():
            page = QWidget()
            page_layout = QVBoxLayout()
            page_layout.setSpacing(15)  # 增加垂直间距
            
            # 创建水平布局，使账户列表和账户详情并排显示
            accounts_details_layout = QHBoxLayout()
            accounts_details_layout.setSpacing(20)  # 增加水平间距
            
            # 账户列表
            account_group = QGroupBox("Accounts")
            account_layout = QVBoxLayout()
            account_layout.setSpacing(10)  # 增加垂直间距
            
            account_list = QListWidget()
            account_list.setMinimumWidth(200)  # 设置最小宽度
            self.account_lists[platform] = account_list
            account_list.currentItemChanged.connect(lambda current, previous, p=platform: self.select_account(p, current))
            
            account_buttons = QHBoxLayout()
            add_btn = QPushButton("Add Account")
            add_btn.clicked.connect(lambda checked, p=platform: self.add_account(p))
            delete_btn = QPushButton("Delete Account")
            delete_btn.clicked.connect(lambda checked, p=platform: self.delete_account(p))
            enable_btn = QPushButton("Enable Account")
            enable_btn.clicked.connect(lambda checked, p=platform: self.enable_account(p))
            
            account_buttons.addWidget(add_btn)
            account_buttons.addWidget(delete_btn)
            account_buttons.addWidget(enable_btn)
            
            account_layout.addWidget(account_list)
            account_layout.addLayout(account_buttons)
            account_group.setLayout(account_layout)
            
            # 账户详情表单
            form_group = QGroupBox("Account Details")
            form_layout = QFormLayout()
            form_layout.setSpacing(10)  # 增加表单项之间的间距
            form_group.setLayout(form_layout)
            
            # 将账户列表和账户详情添加到水平布局中
            accounts_details_layout.addWidget(account_group, 1)  # 1是伸缩因子
            accounts_details_layout.addWidget(form_group, 2)     # 2是伸缩因子，使表单区域更宽
            
            # 添加水平布局到页面布局
            page_layout.addLayout(accounts_details_layout)
            
            # 保存按钮
            save_btn = QPushButton("Save Settings")
            save_btn.clicked.connect(self.save_settings)
            page_layout.addWidget(save_btn)
            
            page.setLayout(page_layout)
            self.platform_pages[platform] = {
                "form": form_layout
            }
            
            self.platform_tabs.addTab(page, platform)
        
        layout.addWidget(self.platform_tabs)
        self.setLayout(layout)
        
        # 加载设置
        self.load_settings()

    def load_settings(self):
        # 为每个平台加载账户
        for platform in self.platform_configs.keys():
            account_list = self.account_lists[platform]
            account_list.clear()
            
            # 获取该平台的所有账户
            accounts = self.config_reader.get_platform_accounts(platform)
            
            # 获取启用的账户ID
            enabled_account = str(self.config_reader.config['accounts'].get(platform, {}).get('enable', '1'))
            
            # 添加到列表
            for account in accounts:
                item = QListWidgetItem(account)
                # 如果是启用的账户，设置背景色以突出显示
                if account == enabled_account:
                    item.setBackground(Qt.green)
                    item.setText(f"{account} (启用中)")
                account_list.addItem(item)
            
            # 选择第一个账户
            if account_list.count() > 0:
                account_list.setCurrentRow(0)
                self.select_account(platform, account_list.item(0))

    def select_account(self, platform, item):
        if not item:
            return
        
        account = item.text()
        # 如果账户名包含 "(启用中)" 后缀，去掉后缀
        if " (启用中)" in account:
            account = account.split(" (")[0]
            
        form = self.platform_pages[platform]["form"]
        
        # 清空表单
        while form.rowCount() > 0:
            form.removeRow(0)
        
        # 获取账户配置
        account_config = self.config_reader.get_account_config(platform, account)
        
        # 创建表单项
        self.field_widgets = {}
        for field in self.platform_configs[platform]:
            value = account_config.get(field, "")
            
            if field == "private":
                widget = QCheckBox()
                widget.setChecked(value if isinstance(value, bool) else value.lower() != "false")
            else:
                widget = QLineEdit()
                if field in ["token", "password"]:
                    widget.setEchoMode(QLineEdit.Password)
                widget.setText(str(value))
            
            self.field_widgets[field] = widget
            form.addRow(f"{field.capitalize()}:", widget)

    def add_account(self, platform):
        dialog = AddAccountDialog(platform, self)
        if dialog.exec_() == QDialog.Accepted:
            account_data = dialog.get_account_data()
            account_name = account_data["name"]
            
            if not account_name:
                QMessageBox.warning(self, "Warning", "Account name cannot be empty.")
                return
            
            # 更新config.yml文件
            config = self.config_reader.config
            if platform not in config['accounts']:
                config['accounts'][platform] = {'enable': 1}
            
            # 添加新账户
            config['accounts'][platform][account_name] = {
                field: value for field, value in account_data.items() if field != 'name'
            }
            
            # 保存配置
            with open(self.config_reader.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            # 重新加载设置
            self.config_reader = ConfigReader()
            self.load_settings()
            
            # 选择新账户
            account_list = self.account_lists[platform]
            for i in range(account_list.count()):
                if account_list.item(i).text() == account_name:
                    account_list.setCurrentRow(i)
                    self.select_account(platform, account_list.item(i))
                    break

    def delete_account(self, platform):
        account_list = self.account_lists[platform]
        current_item = account_list.currentItem()
        
        if not current_item:
            return
            
        account = current_item.text()
        # 如果账户名包含 "(启用中)" 后缀，去掉后缀
        if " (启用中)" in account:
            account = account.split(" (")[0]
        
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete the account '{account}' for {platform}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 更新config.yml文件
            config = self.config_reader.config
            if platform in config['accounts'] and account in config['accounts'][platform]:
                del config['accounts'][platform][account]
                
                # 保存配置
                with open(self.config_reader.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False)
                
                # 重新加载设置
                self.config_reader = ConfigReader()
                self.load_settings()

    def enable_account(self, platform):
        account_list = self.account_lists[platform]
        current_item = account_list.currentItem()
        
        if not current_item:
            return
            
        account = current_item.text()
        # 如果账户名包含 "(启用中)" 后缀，去掉后缀
        if " (启用中)" in account:
            account = account.split(" (")[0]
        
        # 更新config.yml文件
        config = self.config_reader.config
        if platform in config['accounts']:
            # 将当前账户设置为启用账户
            config['accounts'][platform]['enable'] = account
            
            # 保存配置
            with open(self.config_reader.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            QMessageBox.information(
                self, 
                "Success", 
                f"Account '{account}' has been enabled for {platform}."
            )
            
            # 重新加载设置
            self.config_reader = ConfigReader()
            self.load_settings()

    def save_settings(self):
        # 保存当前显示的账户配置
        platform = list(self.platform_configs.keys())[self.platform_tabs.currentIndex()]
        account_list = self.account_lists[platform]
        current_item = account_list.currentItem()
        
        if current_item and hasattr(self, 'field_widgets'):
            account = current_item.text()
            # 如果账户名包含 "(启用中)" 后缀，去掉后缀
            if " (启用中)" in account:
                account = account.split(" (")[0]
            
            # 更新config.yml文件
            config = self.config_reader.config
            if platform not in config['accounts']:
                config['accounts'][platform] = {'enable': 1}
            
            # 更新账户配置
            account_config = {}
            for field, widget in self.field_widgets.items():
                if isinstance(widget, QCheckBox):
                    value = widget.isChecked()
                else:
                    value = widget.text().strip()
                if value:
                    account_config[field] = value
            
            config['accounts'][platform][account] = account_config
            
            # 保存配置
            with open(self.config_reader.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")

class AddAccountDialog(QDialog):
    def __init__(self, platform, parent=None):
        super().__init__(parent)
        self.platform = platform
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Add {self.platform} Account")
        layout = QFormLayout()
        layout.setSpacing(10)  # 增加表单项之间的间距
        
        # 账户名称
        self.name_edit = QLineEdit()
        layout.addRow("Account Name:", self.name_edit)
        
        # 其他字段
        self.field_widgets = {}
        platform_configs = {
            "github": ["username", "token", "private"],
            "gitlab": ["host", "username", "token", "private"],
            "gitee": ["username", "token", "private"],
            "gitcode": ["username", "token", "private"],
            "git.yoq.me": ["username", "token", "private"],
            "coding": ["username", "token", "project", "private"],
            "aliyun": ["compoanyid", "group_id", "username", "token", "private"],
            "cnb": ["username", "token", "private"]
        }
        
        for field in platform_configs[self.platform]:
            if field == "private":
                widget = QCheckBox()
                widget.setChecked(True)
            else:
                widget = QLineEdit()
                if field in ["token", "password"]:
                    widget.setEchoMode(QLineEdit.Password)
            
            self.field_widgets[field] = widget
            layout.addRow(f"{field.capitalize()}:", widget)
        
        # 添加一些空间
        layout.addItem(QSpacerItem(20, 20))
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        self.setMinimumWidth(400)  # 设置对话框最小宽度
    
    def get_account_data(self):
        data = {"name": self.name_edit.text().strip()}
        for field, widget in self.field_widgets.items():
            if isinstance(widget, QCheckBox):
                data[field] = widget.isChecked()
            else:
                data[field] = widget.text().strip()
        return data

class MainTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        
        # 路径选择
        path_layout = QHBoxLayout()
        self.path_label = QLabel("Local Path: ")
        self.path_edit = QLineEdit()
        self.path_edit.setText(get_active_explorer_path())
        self.path_btn = QPushButton("Browse...")
        self.path_btn.clicked.connect(self.choose_path)
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.path_btn)
        layout.addLayout(path_layout)
        
        # 操作
        op_group = QGroupBox("Operation:")
        op_layout = QHBoxLayout()
        self.op_buttons = QButtonGroup(self)
        for i, op in enumerate(["create", "push", "pull", "clone", "delete"]):
            btn = QRadioButton(op.capitalize())
            if i == 1:
                btn.setChecked(True)
            self.op_buttons.addButton(btn, i)
            op_layout.addWidget(btn)
        op_group.setLayout(op_layout)
        layout.addWidget(op_group)
        
        # 平台
        pf_group = QGroupBox("Platform:")
        pf_layout = QHBoxLayout()
        self.pf_buttons = QButtonGroup(self)
        self.platforms = ["github", "gitlab", "gitee", "gitcode", "git.yoq.me", "coding", "aliyun", "cnb"]
        for i, pf in enumerate(self.platforms):
            btn = QRadioButton(pf.capitalize())
            if i == 0:
                btn.setChecked(True)
            self.pf_buttons.addButton(btn, i)
            pf_layout.addWidget(btn)
        pf_group.setLayout(pf_layout)
        layout.addWidget(pf_group)
        
        # 账户选择
        account_layout = QHBoxLayout()
        account_layout.addWidget(QLabel("Account:"))
        self.account_combo = QComboBox()
        self.account_combo.setMinimumWidth(200)
        account_layout.addWidget(self.account_combo)
        account_layout.addStretch()
        layout.addLayout(account_layout)
        
        # 按钮区域 (run和cancel)
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("run it")
        self.run_btn.clicked.connect(self.run_repo_sync)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_operation)
        self.cancel_btn.setEnabled(False)
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        # 命令执行结果
        result_group = QGroupBox("Execution Result:")
        result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        self.setLayout(layout)
        
        # 命令执行相关
        self.process = None
        self.command_signals = CommandSignals()
        self.command_signals.output.connect(self.update_output)
        self.command_signals.finished.connect(self.process_finished)
        
        # 初始化配置读取器
        self.config_reader = ConfigReader()
        
        # 平台变更时更新账户列表
        self.pf_buttons.buttonClicked.connect(self.update_account_list)
        self.update_account_list()

    def choose_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.path_edit.setText(path)

    def update_account_list(self):
        self.account_combo.clear()
        pf_id = self.pf_buttons.checkedId()
        platform = self.platforms[pf_id]
        
        # 读取所有账户
        accounts = self.get_platform_accounts(platform)
        
        # 找出启用的账户
        enabled_account = self.get_enabled_account(platform)
        
        # 添加账户到下拉框，启用的账户放在最前面
        if enabled_account in accounts:
            accounts.remove(enabled_account)
            self.account_combo.addItem(f"{enabled_account} (启用中)")
            
            # 设置启用账户的背景颜色为绿色
            model = self.account_combo.model()
            index = model.index(0, 0)
            model.setData(index, Qt.green, Qt.BackgroundRole)
            
        for account in accounts:
            self.account_combo.addItem(account)
        
        # 默认选择启用的账户
        self.account_combo.setCurrentIndex(0)

    def get_platform_accounts(self, platform):
        # 读取config.yml文件中的所有配置
        accounts = set()
        
        # 获取该平台的所有账户
        try:
            platform_accounts = self.config_reader.get_platform_accounts(platform)
            for account in platform_accounts:
                accounts.add(account)
        except Exception as e:
            print(f"Error getting platform accounts: {str(e)}")
        
        # 确保至少有一个默认账户
        if not accounts:
            accounts.add("1")
        
        return sorted(list(accounts))

    def get_enabled_account(self, platform):
        """获取平台的启用账户ID"""
        try:
            if platform in self.config_reader.config['accounts']:
                return str(self.config_reader.config['accounts'][platform].get('enable', '1'))
            return '1'  # 默认返回'1'
        except Exception as e:
            print(f"Error getting enabled account: {str(e)}")
            return '1'  # 出错时默认返回'1'

    def run_repo_sync(self):
        repo_path = self.path_edit.text().strip()
        if not repo_path:
            QMessageBox.warning(self, "Warning", "Please select a local path.")
            return
            
        op_id = self.op_buttons.checkedId()
        pf_id = self.pf_buttons.checkedId()
        op = ["create", "push", "pull", "clone", "delete"][op_id]
        pf = self.platforms[pf_id]
        
        # 获取选择的账户名（去掉可能的"(启用中)"后缀）
        account_text = self.account_combo.currentText()
        account = account_text.split(" (")[0] if " (" in account_text else account_text
        
        # 清空结果区域
        self.result_text.clear()
        
        # 检查平台配置
        account_config = self.config_reader.get_account_config(pf, account)
        if not account_config.get('token'):
            QMessageBox.warning(self, "Warning", f"Please configure {pf} token for account '{account}' in Settings tab first.")
            return
        
        # 构建参数
        args = {
            'command': op,
            'platform': pf,
            'repo_path': repo_path
        }
        
        # 获取启用的账户
        enabled_account = self.get_enabled_account(pf)
        
        # 如果不是启用账户，需要设置环境变量
        if account != enabled_account:
            # 保存原始环境变量
            self.original_env = {}
            for field, value in account_config.items():
                env_var = f"{pf}_{field}"
                if env_var in os.environ:
                    self.original_env[env_var] = os.environ[env_var]
                os.environ[env_var] = str(value)
        
        # 显示执行命令
        cmd_str = f"repo_sync {op} -p {pf} -repo_path {repo_path}"
        self.result_text.append(f"Running: {cmd_str}\n")
        
        # 执行命令
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # 重定向标准输出和标准错误
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = self.OutputRedirector(self.command_signals)
        sys.stderr = self.OutputRedirector(self.command_signals)
        
        # 在新线程中执行命令
        self.process_thread = threading.Thread(
            target=self.run_module,
            args=(args,)
        )
        self.process_thread.daemon = True
        self.process_thread.start()

    def run_module(self, args):
        try:
            # 正确导入repo_sync模块的main函数
            from repo_sync.repo_sync import RepoSync
            self.running = True
            return_code = 0
            try:
                # 直接创建RepoSync实例并运行
                rs = RepoSync(args)
                rs.run()
            except SystemExit as e:
                return_code = e.code if isinstance(e.code, int) else 1
            except Exception as e:
                self.command_signals.output.emit(f"Error: {str(e)}")
                return_code = 1
            finally:
                self.command_signals.finished.emit(return_code)
                # 恢复标准输出和标准错误
                sys.stdout = self.original_stdout
                sys.stderr = self.original_stderr
                # 恢复环境变量
                if hasattr(self, 'original_env'):
                    for var, value in self.original_env.items():
                        os.environ[var] = value
                    delattr(self, 'original_env')
        except Exception as e:
            self.command_signals.output.emit(f"Error: {str(e)}")
            self.command_signals.finished.emit(1)
            # 恢复标准输出和标准错误
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr

    # 输出重定向类
    class OutputRedirector:
        def __init__(self, signals):
            self.signals = signals
            self.buffer = ""
        
        def write(self, text):
            self.buffer += text
            if '\n' in self.buffer:
                lines = self.buffer.split('\n')
                for line in lines[:-1]:
                    self.signals.output.emit(line)
                self.buffer = lines[-1]
        
        def flush(self):
            if self.buffer:
                self.signals.output.emit(self.buffer)
                self.buffer = ""
                
    def run_process(self, cmd, env=None):
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env
            )
            
            # 读取输出
            for line in self.process.stdout:
                self.command_signals.output.emit(line)
            
            self.process.wait()
            self.command_signals.finished.emit(self.process.returncode)
        except Exception as e:
            self.command_signals.output.emit(f"Error: {str(e)}")
            self.command_signals.finished.emit(1)

    def update_output(self, text):
        self.result_text.append(text)
        # 自动滚动到底部
        self.result_text.verticalScrollBar().setValue(
            self.result_text.verticalScrollBar().maximum()
        )

    def process_finished(self, return_code):
        self.process = None
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        if return_code == 0:
            self.result_text.append("\nOperation completed successfully.")
        else:
            self.result_text.append(f"\nOperation failed with return code {return_code}.")

    def cancel_operation(self):
        if self.process:
            self.process.terminate()
            self.result_text.append("\nOperation cancelled by user.")
        else:
            # 直接调用模式下，通过退出标志通知线程结束
            self.running = False
            self.result_text.append("\nOperation cancelled by user.")
            # 恢复标准输出和标准错误
            if hasattr(self, 'original_stdout') and hasattr(self, 'original_stderr'):
                sys.stdout = self.original_stdout
                sys.stderr = self.original_stderr
            # 恢复环境变量
            if hasattr(self, 'original_env'):
                for var, value in self.original_env.items():
                    os.environ[var] = value
                delattr(self, 'original_env')

# Explorer路径获取
try:
    import win32com.client
    def get_active_explorer_path():
        shell = win32com.client.Dispatch("Shell.Application")
        for window in shell.Windows():
            if window.Name in ["文件资源管理器", "Windows Explorer"]:
                return window.Document.Folder.Self.Path
        return os.getcwd()
except ImportError:
    def get_active_explorer_path():
        return os.getcwd()

# 命令执行信号类
class CommandSignals(QObject):
    output = pyqtSignal(str)
    finished = pyqtSignal(int)

class AboutTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"repo_sync tools v{__version__}"))
        layout.addWidget(QLabel("作者: liuyuqi.gov@msn.cn"))
        layout.addWidget(QLabel("GitHub: https://github.com/jianboy/repo_sync"))
        layout.addWidget(QLabel("\n功能说明："))
        layout.addWidget(QLabel("- 支持多个代码托管平台"))
        layout.addWidget(QLabel("- 支持创建/推送/拉取/克隆/删除操作"))
        layout.addWidget(QLabel("- 自动获取资源管理器当前路径"))
        layout.addWidget(QLabel("- 配置信息保存在config.yml文件中"))
        layout.addWidget(QLabel("- 支持每个平台配置多个账户"))
        layout.addWidget(QLabel("- 命令行执行结果实时显示"))
        self.setLayout(layout)

class RepoSyncMainWindow(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('repo_sync tools v1.12')
        self.resize(800, 700)
        self.main_tab = MainTab()
        self.addTab(self.main_tab, '主界面')
        self.settings_tab = SettingsTab()
        self.addTab(self.settings_tab, '设置')
        self.about_tab = AboutTab()
        self.addTab(self.about_tab, '关于')

def main():
    """GUI主入口函数"""
    if not HAS_QT:
        print("PyQt5 not installed. Please install it with: pip install PyQt5")
        print("Running in fallback mode...")
        # 这里可以添加一个简单的命令行界面作为后备
        return
        
    try:
        # 确保config.yml文件存在
        ensure_config_file()
        
        app = QApplication(sys.argv)
        window = RepoSyncMainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting GUI: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 