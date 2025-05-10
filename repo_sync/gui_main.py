import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QRadioButton, QPushButton, QButtonGroup, QGroupBox, QMessageBox, 
    QLineEdit, QScrollArea, QFileDialog, QFormLayout, QCheckBox
)
from PyQt5.QtCore import Qt
from repo_sync import RepoSync, __version__
from dotenv import load_dotenv, set_key, find_dotenv
import json

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
        
        # run按钮
        self.run_btn = QPushButton("run it")
        self.run_btn.clicked.connect(self.run_repo_sync)
        layout.addWidget(self.run_btn, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def choose_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.path_edit.setText(path)

    def run_repo_sync(self):
        repo_path = self.path_edit.text().strip()
        if not repo_path:
            QMessageBox.warning(self, "Warning", "Please select a local path.")
            return
            
        op_id = self.op_buttons.checkedId()
        pf_id = self.pf_buttons.checkedId()
        op = ["create", "push", "pull", "clone", "delete"][op_id]
        pf = self.platforms[pf_id]
        
        # 检查平台配置
        load_dotenv()
        if not os.getenv(f"{pf}_token"):
            QMessageBox.warning(self, "Warning", f"Please configure {pf} token in Settings tab first.")
            return
            
        params = {
            "command": op,
            "platform": pf,
            "repo_path": repo_path,
            f"{pf}_token": os.getenv(f"{pf}_token"),
            f"{pf}_username": os.getenv(f"{pf}_username"),
            f"{pf}_private": os.getenv(f"{pf}_private", "true")
        }
        
        try:
            rs = RepoSync(params)
            rs.run()
            QMessageBox.information(self, "Success", f"Operation '{op}' on '{pf}' finished.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.form_layout = QFormLayout()
        
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
        
        self.config_widgets = {}
        for platform, fields in self.platform_configs.items():
            group = QGroupBox(platform.capitalize())
            group_layout = QFormLayout()
            
            platform_widgets = {}
            for field in fields:
                if field == "private":
                    widget = QCheckBox()
                    widget.setChecked(True)
                else:
                    widget = QLineEdit()
                    if field in ["token", "password"]:
                        widget.setEchoMode(QLineEdit.Password)
                
                field_name = f"{platform}_{field}"
                platform_widgets[field_name] = widget
                group_layout.addRow(f"{field.capitalize()}:", widget)
            
            self.config_widgets.update(platform_widgets)
            group.setLayout(group_layout)
            self.form_layout.addRow(group)
        
        # 保存按钮
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        
        content.setLayout(self.form_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        layout.addWidget(self.save_btn, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def load_settings(self):
        load_dotenv()
        for field_name, widget in self.config_widgets.items():
            value = os.getenv(field_name)
            if isinstance(widget, QCheckBox):
                widget.setChecked(value != "false")
            elif value:
                widget.setText(value)

    def save_settings(self):
        env_file = find_dotenv()
        if not env_file:
            env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        
        for field_name, widget in self.config_widgets.items():
            if isinstance(widget, QCheckBox):
                value = str(widget.isChecked()).lower()
            else:
                value = widget.text().strip()
            
            if value:
                set_key(env_file, field_name, value)
        
        QMessageBox.information(self, "Success", "Settings saved successfully!")

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
        self.setLayout(layout)

class RepoSyncMainWindow(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('repo_sync tools v1.12')
        self.resize(800, 600)
        self.main_tab = MainTab()
        self.addTab(self.main_tab, '主界面')
        self.settings_tab = SettingsTab()
        self.addTab(self.settings_tab, '设置')
        self.about_tab = AboutTab()
        self.addTab(self.about_tab, '关于')

def main():
    app = QApplication(sys.argv)
    window = RepoSyncMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 