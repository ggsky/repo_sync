import sys
import os
import threading
import subprocess
try:
    from PyQt5.QtWidgets import (
        QApplication, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
        QRadioButton, QPushButton, QButtonGroup, QGroupBox, QMessageBox, 
        QLineEdit, QScrollArea, QFileDialog, QFormLayout, QCheckBox, QTextEdit,
        QComboBox, QDialog, QDialogButtonBox, QGridLayout, QToolButton, QListWidget, QListWidgetItem
    )
    from PyQt5.QtCore import Qt, pyqtSignal, QObject
    HAS_QT = True
except ImportError:
    HAS_QT = False
    print("PyQt5 not installed, GUI mode not available")

from repo_sync import RepoSync, __version__
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values
import json
import uuid

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
            if i == 0:
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
        enabled_account = "default"
        env_values = dotenv_values(find_dotenv())
        for account in accounts:
            if account != "default" and env_values.get(f"{platform}_{account}_enabled", "").lower() == "true":
                enabled_account = account
                break
        
        # 添加账户到下拉框，启用的账户放在最前面
        if enabled_account in accounts:
            accounts.remove(enabled_account)
            self.account_combo.addItem(f"{enabled_account} (启用中)")
            
        for account in accounts:
            self.account_combo.addItem(account)
        
        # 默认选择启用的账户
        self.account_combo.setCurrentIndex(0)

    def get_platform_accounts(self, platform):
        # 读取.env文件中的所有配置
        env_values = dotenv_values(find_dotenv())
        accounts = set()
        
        # 默认账户
        accounts.add("default")
        
        # 查找带有账户名的配置
        prefix = f"{platform}_"
        for key in env_values.keys():
            if key.startswith(prefix) and "_" in key[len(prefix):]:
                account_name = key[len(prefix):].split("_")[0]
                if account_name != "default" and account_name != "":
                    accounts.add(account_name)
        
        return sorted(list(accounts))

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
        load_dotenv()
        token_key = f"{pf}_{account}_token" if account != "default" else f"{pf}_token"
        if not os.getenv(token_key):
            QMessageBox.warning(self, "Warning", f"Please configure {pf} token for account '{account}' in Settings tab first.")
            return
            
        # 构建命令
        cmd = [sys.executable, "-m", "repo_sync"]
        cmd.append(op)
        cmd.extend(["-p", pf])
        cmd.extend(["-repo_path", repo_path])
        
        # 如果不是默认账户，需要设置环境变量
        env = os.environ.copy()
        if account != "default":
            # 读取账户配置
            env_values = dotenv_values(find_dotenv())
            for key, value in env_values.items():
                if key.startswith(f"{pf}_{account}_"):
                    field = key[len(f"{pf}_{account}_"):]
                    env[f"{pf}_{field}"] = value
        
        # 执行命令
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.result_text.append(f"Running: {' '.join(cmd)}\n")
        
        # 在新线程中执行命令
        self.process_thread = threading.Thread(
            target=self.run_process,
            args=(cmd, env)
        )
        self.process_thread.daemon = True
        self.process_thread.start()

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

# 添加账户对话框
class AddAccountDialog(QDialog):
    def __init__(self, platform, parent=None):
        super().__init__(parent)
        self.platform = platform
        self.setWindowTitle(f"Add {platform.capitalize()} Account")
        self.resize(400, 200)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        self.account_name = QLineEdit()
        form_layout.addRow("Account Name:", self.account_name)
        
        # 根据平台添加相应字段
        self.fields = {}
        platform_fields = {
            "github": ["username", "token", "private"],
            "gitlab": ["host", "username", "token", "private"],
            "gitee": ["username", "token", "private"],
            "gitcode": ["username", "token", "private"],
            "git.yoq.me": ["username", "token", "private"],
            "coding": ["username", "token", "project", "private"],
            "aliyun": ["compoanyid", "group_id", "username", "token", "private"],
            "cnb": ["username", "token", "private"]
        }
        
        for field in platform_fields.get(platform, ["username", "token"]):
            if field == "private":
                widget = QCheckBox()
                widget.setChecked(True)
            else:
                widget = QLineEdit()
                if field in ["token", "password"]:
                    widget.setEchoMode(QLineEdit.Password)
            
            self.fields[field] = widget
            form_layout.addRow(f"{field.capitalize()}:", widget)
        
        layout.addLayout(form_layout)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_account_data(self):
        data = {"name": self.account_name.text()}
        for field, widget in self.fields.items():
            if isinstance(widget, QCheckBox):
                data[field] = widget.isChecked()
            else:
                data[field] = widget.text()
        return data

class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
            
            # 账户管理区域
            account_group = QGroupBox("账户管理")
            account_layout = QVBoxLayout()
            
            # 账户列表
            accounts_list_layout = QHBoxLayout()
            
            # 左侧：账户列表
            self.account_lists = {}
            account_list = QListWidget()
            account_list.setMinimumWidth(200)
            account_list.itemClicked.connect(lambda item, p=platform: self.select_account(p, item))
            account_list.setStyleSheet("""
                QListWidget::item:selected { background-color: #a6d8ff; }
                QListWidget::item[enabled="true"] { font-weight: bold; color: #0066cc; }
            """)
            accounts_list_layout.addWidget(account_list)
            self.account_lists[platform] = account_list
            
            # 右侧：账户详情
            account_details = QWidget()
            account_form = QFormLayout()
            account_details.setLayout(account_form)
            accounts_list_layout.addWidget(account_details, 1)
            
            account_layout.addLayout(accounts_list_layout)
            
            # 账户操作按钮
            buttons_layout = QHBoxLayout()
            add_btn = QPushButton("添加账户")
            add_btn.clicked.connect(lambda checked=False, p=platform: self.add_account(p))
            delete_btn = QPushButton("删除账户")
            delete_btn.clicked.connect(lambda checked=False, p=platform: self.delete_account(p))
            enable_btn = QPushButton("设为启用")
            enable_btn.clicked.connect(lambda checked=False, p=platform: self.enable_account(p))
            
            buttons_layout.addWidget(add_btn)
            buttons_layout.addWidget(delete_btn)
            buttons_layout.addWidget(enable_btn)
            buttons_layout.addStretch()
            
            account_layout.addLayout(buttons_layout)
            account_group.setLayout(account_layout)
            page_layout.addWidget(account_group)
            
            # 保存页面引用
            self.platform_pages[platform] = {
                "page": page,
                "form": account_form,
                "details": account_details
            }
            
            page.setLayout(page_layout)
            self.platform_tabs.addTab(page, platform.capitalize())
        
        layout.addWidget(self.platform_tabs)
        
        # 保存按钮
        self.save_btn = QPushButton("保存设置")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
        
        # 加载设置
        self.load_settings()
        
        # 连接标签页变更事件
        self.platform_tabs.currentChanged.connect(self.tab_changed)

    def tab_changed(self, index):
        try:
            # 使用有序字典确保顺序一致性
            platforms = list(self.platform_configs.keys())
            if index < 0 or index >= len(platforms):
                return
            platform = platforms[index]
            self.update_account_details(platform)
        except Exception as e:
            print(f"Error in tab_changed: {e}")

    def load_settings(self):
        # 读取.env文件
        env_values = dotenv_values(find_dotenv())
        
        # 为每个平台加载账户
        for platform in self.platform_configs.keys():
            account_list = self.account_lists[platform]
            account_list.clear()
            
            # 查找该平台的所有账户
            accounts = self.get_platform_accounts(platform, env_values)
            
            # 添加到列表
            for account in accounts:
                item = QListWidgetItem(account)
                # 标记默认账户
                if account == "default":
                    item.setData(Qt.UserRole, "default")
                    # 检查是否有其他账户被设为启用
                    is_enabled = True
                    for other_account in accounts:
                        if other_account != "default" and self.is_account_enabled(platform, other_account, env_values):
                            is_enabled = False
                            break
                    item.setData(Qt.UserRole + 1, is_enabled)
                else:
                    item.setData(Qt.UserRole, account)
                    item.setData(Qt.UserRole + 1, self.is_account_enabled(platform, account, env_values))
                
                # 设置启用状态的显示
                if item.data(Qt.UserRole + 1):
                    item.setData(Qt.UserRole + 2, "true")
                    item.setText(f"{account} (启用中)")
                
                account_list.addItem(item)
            
            # 选择第一个账户
            if account_list.count() > 0:
                account_list.setCurrentRow(0)
                self.select_account(platform, account_list.item(0))

    def is_account_enabled(self, platform, account, env_values=None):
        """检查账户是否被设为启用"""
        if env_values is None:
            env_values = dotenv_values(find_dotenv())
        
        if account == "default":
            # 默认账户，检查是否有其他账户被设为启用
            for key in env_values.keys():
                if key.startswith(f"{platform}_") and "_enabled" in key and env_values[key].lower() == "true":
                    return False
            return True
        else:
            # 其他账户，检查是否有enabled标记
            return env_values.get(f"{platform}_{account}_enabled", "").lower() == "true"

    def get_platform_accounts(self, platform, env_values=None):
        if env_values is None:
            env_values = dotenv_values(find_dotenv())
        
        accounts = set()
        # 默认账户
        accounts.add("default")
        
        # 查找带有账户名的配置
        prefix = f"{platform}_"
        for key in env_values.keys():
            if key.startswith(prefix) and "_" in key[len(prefix):]:
                account_name = key[len(prefix):].split("_")[0]
                if account_name != "default" and account_name != "":
                    accounts.add(account_name)
        
        return sorted(list(accounts))

    def select_account(self, platform, item):
        if not item:
            return
        
        account = item.data(Qt.UserRole)
        form = self.platform_pages[platform]["form"]
        
        # 清空表单
        while form.rowCount() > 0:
            form.removeRow(0)
        
        # 读取账户配置
        env_values = dotenv_values(find_dotenv())
        
        # 创建表单项
        self.field_widgets = {}
        for field in self.platform_configs[platform]:
            key = f"{platform}_{account}_{field}" if account != "default" else f"{platform}_{field}"
            value = env_values.get(key, "")
            
            if field == "private":
                widget = QCheckBox()
                widget.setChecked(value.lower() != "false")
            else:
                widget = QLineEdit()
                if field in ["token", "password"]:
                    widget.setEchoMode(QLineEdit.Password)
                widget.setText(value)
            
            self.field_widgets[key] = widget
            form.addRow(f"{field.capitalize()}:", widget)

    def add_account(self, platform):
        dialog = AddAccountDialog(platform, self)
        if dialog.exec_() == QDialog.Accepted:
            account_data = dialog.get_account_data()
            account_name = account_data["name"]
            
            if not account_name:
                QMessageBox.warning(self, "Warning", "Account name cannot be empty.")
                return
            
            # 更新.env文件
            env_file = find_dotenv()
            if not env_file:
                env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            
            for field, value in account_data.items():
                if field == "name":
                    continue
                
                key = f"{platform}_{account_name}_{field}"
                if isinstance(value, bool):
                    value = str(value).lower()
                
                set_key(env_file, key, value)
            
            # 重新加载设置
            self.load_settings()
            
            # 选择新账户
            account_list = self.account_lists[platform]
            for i in range(account_list.count()):
                if account_list.item(i).data(Qt.UserRole) == account_name:
                    account_list.setCurrentRow(i)
                    self.select_account(platform, account_list.item(i))
                    break

    def delete_account(self, platform):
        account_list = self.account_lists[platform]
        current_item = account_list.currentItem()
        
        if not current_item:
            return
            
        account = current_item.data(Qt.UserRole)
        
        if account == "default":
            QMessageBox.warning(self, "Warning", "Cannot delete the default account.")
            return
        
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete the account '{account}' for {platform}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 删除.env中的相关配置
            env_file = find_dotenv()
            env_values = dotenv_values(env_file)
            
            prefix = f"{platform}_{account}_"
            keys_to_remove = [k for k in env_values.keys() if k.startswith(prefix)]
            
            # 重写.env文件，排除要删除的键
            with open(env_file, 'w') as f:
                for k, v in env_values.items():
                    if k not in keys_to_remove:
                        f.write(f"{k}={v}\n")
            
            # 重新加载设置
            self.load_settings()

    def enable_account(self, platform):
        account_list = self.account_lists[platform]
        current_item = account_list.currentItem()
        
        if not current_item:
            return
            
        account = current_item.data(Qt.UserRole)
        
        # 读取账户配置
        env_file = find_dotenv()
        env_values = dotenv_values(env_file)
        
        # 先清除所有账户的启用状态
        for key in list(env_values.keys()):
            if key.startswith(f"{platform}_") and key.endswith("_enabled"):
                del env_values[key]
        
        # 设置当前账户为启用
        if account != "default":
            set_key(env_file, f"{platform}_{account}_enabled", "true")
            
            # 将账户配置复制到默认配置
            account_config = {}
            prefix = f"{platform}_{account}_"
            for key, value in env_values.items():
                if key.startswith(prefix):
                    field = key[len(prefix):]
                    if field != "enabled":  # 不复制enabled标记
                        account_config[field] = value
            
            # 更新默认配置
            for field, value in account_config.items():
                default_key = f"{platform}_{field}"
                set_key(env_file, default_key, value)
        
        QMessageBox.information(
            self, 
            "Success", 
            f"Account '{account}' has been enabled for {platform}."
        )
        
        # 重新加载设置
        self.load_settings()

    def update_account_details(self, platform):
        account_list = self.account_lists[platform]
        current_item = account_list.currentItem()
        
        if current_item:
            self.select_account(platform, current_item)

    def save_settings(self):
        env_file = find_dotenv()
        if not env_file:
            env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        
        # 保存当前显示的账户配置
        platform = list(self.platform_configs.keys())[self.platform_tabs.currentIndex()]
        account_list = self.account_lists[platform]
        current_item = account_list.currentItem()
        
        if current_item and hasattr(self, 'field_widgets'):
            account = current_item.data(Qt.UserRole)
            
            for key, widget in self.field_widgets.items():
                if key.startswith(f"{platform}_{account}"):
                    if isinstance(widget, QCheckBox):
                        value = str(widget.isChecked()).lower()
                    else:
                        value = widget.text().strip()
                    
                    if value:
                        set_key(env_file, key, value)
        
        QMessageBox.information(self, "Success", "Settings saved successfully!")
        
        # 如果修改的是启用的账户，更新默认配置
        if current_item and current_item.data(Qt.UserRole + 1):
            self.enable_account(platform)

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
        layout.addWidget(QLabel("- 配置信息保存在.env文件中"))
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