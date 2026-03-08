import sys
import os
import json
import zipfile
import shutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                             QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                             QMenuBar, QMenu, QAction, QFileDialog, QMessageBox,
                             QHeaderView, QDialog, QPushButton, QLineEdit, QScrollArea, QGroupBox, QComboBox, QRadioButton, QButtonGroup, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from res_manager import Resources_Manager


APP_STYLESHEET = """
QWidget {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 13px;
}
QMainWindow, QDialog {
    background-color: #f6f8fb;
}
QGroupBox {
    border: 1px solid #d7dce5;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 12px;
    background-color: #ffffff;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}
QLineEdit, QTextEdit, QComboBox, QTableWidget {
    border: 1px solid #cdd4df;
    border-radius: 6px;
    padding: 6px;
    background-color: #ffffff;
}
QPushButton {
    background-color: #3f7cff;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
    min-height: 16px;
}
QPushButton:hover {
    background-color: #3068de;
}
QPushButton:disabled {
    background-color: #b7c4e4;
    color: #e8ecf7;
}
QHeaderView::section {
    background-color: #edf2ff;
    color: #273245;
    border: none;
    border-bottom: 1px solid #d6deee;
    padding: 8px;
    font-weight: 600;
}
"""


def build_section(title):
    group = QGroupBox(title)
    layout = QVBoxLayout()
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(10)
    group.setLayout(layout)
    return group, layout


class NextWindow(QDialog):
    """next窗口"""
    def __init__(self, next_data, execute_data, project_dir, res_manager, parent=None):
        super().__init__(parent)
        self.next_data = next_data
        self.execute_data = execute_data
        self.project_dir = project_dir
        self.res_manager = res_manager
        self.setWindowTitle("next设置")
        self.setFixedSize(800, 850)
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        self.setStyleSheet(APP_STYLESHEET)

        path_group, path_layout = build_section("剧情走向")
        execute_group, execute_layout = build_section("结束后执行")
        choice_group, choice_layout = build_section("选项分支")
        
        # 单选按钮组
        self.radio_group = QButtonGroup(self)
        
        # 直接结束
        self.radio_end = QRadioButton("直接结束")
        self.radio_group.addButton(self.radio_end, 0)
        path_layout.addWidget(self.radio_end)
        
        # execute单选按钮组
        self.execute_radio_group = QButtonGroup(self)
        
        # 不执行
        self.execute_null_radio = QRadioButton("不执行")
        self.execute_radio_group.addButton(self.execute_null_radio, 0)
        execute_layout.addWidget(self.execute_null_radio)
        
        # 执行Java代码
        self.execute_java_radio = QRadioButton("执行Java代码输入注册名")
        self.execute_radio_group.addButton(self.execute_java_radio, 1)
        execute_layout.addWidget(self.execute_java_radio)
        
        # Java代码输入框
        java_layout = QHBoxLayout()
        java_layout.addSpacing(30)
        self.java_input = QLineEdit()
        self.java_input.setPlaceholderText("示例: your_mod:script_name")
        java_layout.addWidget(self.java_input)
        execute_layout.addLayout(java_layout)
        
        # 执行指令
        self.execute_command_radio = QRadioButton("执行指令 换行就为一条指令")
        self.execute_radio_group.addButton(self.execute_command_radio, 2)
        execute_layout.addWidget(self.execute_command_radio)
        
        # 指令文本输入框
        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText("每行一条命令，例如:\n/say hello")
        self.command_input.setFixedSize(700, 300)
        execute_layout.addWidget(self.command_input)
        
        # 接着下一节
        self.radio_next = QRadioButton("接着下一节")
        self.radio_group.addButton(self.radio_next, 1)
        path_layout.addWidget(self.radio_next)
        
        # 下一节情节的输入和选择框
        next_scene_layout = QHBoxLayout()
        next_scene_label = QLabel("下一节情节:")
        next_scene_label.setFixedWidth(80)
        self.next_scene_input = QLineEdit()
        self.next_scene_combo = QComboBox()
        self.next_scene_combo.setEditable(False)
        self.next_scene_combo.setFixedWidth(150)
        self.next_scene_combo.addItem("")
        # 加载text目录下的json文件
        self.load_text_files()
        self.next_scene_combo.currentTextChanged.connect(
            lambda text: self.next_scene_input.setText(text)
        )
        next_scene_layout.addWidget(next_scene_label)
        next_scene_layout.addWidget(self.next_scene_input, 3)
        next_scene_layout.addWidget(self.next_scene_combo, 1)
        path_layout.addLayout(next_scene_layout)
        
        # 选项分支
        self.radio_branch = QRadioButton("选项分支")
        self.radio_group.addButton(self.radio_branch, 2)
        choice_layout.addWidget(self.radio_branch)
        
        # 四个选项组
        self.option_inputs = []
        self.option_scene_inputs = []
        self.option_scene_combos = []
        for i in range(4):
            # 选项文本
            option_layout = QHBoxLayout()
            option_label = QLabel(f"选项文本:")
            option_label.setFixedWidth(80)
            option_input = QLineEdit()
            self.option_inputs.append(option_input)
            option_layout.addWidget(option_label)
            option_layout.addWidget(option_input)
            choice_layout.addLayout(option_layout)
            
            # 下一节情节
            option_scene_layout = QHBoxLayout()
            option_scene_label = QLabel(f"下一节情节:")
            option_scene_label.setFixedWidth(80)
            option_scene_input = QLineEdit()
            option_scene_combo = QComboBox()
            option_scene_combo.setEditable(False)
            option_scene_combo.setFixedWidth(150)
            option_scene_combo.addItem("")
            self.load_text_files_to_combo(option_scene_combo)
            option_scene_combo.currentTextChanged.connect(
                lambda text, inp=option_scene_input: self.on_text_file_selected(text, inp)
            )
            self.option_scene_inputs.append(option_scene_input)
            self.option_scene_combos.append(option_scene_combo)
            option_scene_layout.addWidget(option_scene_label)
            option_scene_layout.addWidget(option_scene_input, 3)
            option_scene_layout.addWidget(option_scene_combo, 1)
            choice_layout.addLayout(option_scene_layout)
            
            # 空行分隔
            if i < 3:
                choice_layout.addSpacing(10)

        layout.addWidget(path_group)
        layout.addWidget(execute_group)
        layout.addWidget(choice_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self.accept_and_save)
        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(btn_ok)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # 连接单选按钮信号
        self.radio_group.buttonClicked.connect(self.on_radio_changed)
        self.execute_radio_group.buttonClicked.connect(self.on_radio_changed)
        self.on_radio_changed()
    
    def load_text_files(self):
        """加载text目录下的json文件"""
        self.load_text_files_to_combo(self.next_scene_combo)
    
    def load_text_files_to_combo(self, combo):
        """加载text目录下的json文件到指定的下拉框，使用res_manager.get_list"""
        if not self.res_manager:
            return
        
        text_list = self.res_manager.get_list("all_data")
        for file_name in text_list:
            combo.addItem(file_name)
    
    def on_text_file_selected(self, filename, input_field):
        """文本文件选择回调，使用save_id转换"""
        if filename:
            input_field.setText(filename)
    
    def on_radio_changed(self):
        """单选按钮变化时更新控件状态"""
        checked_id = self.radio_group.checkedId()
        # 启用/禁用下一节情节控件
        next_enabled = (checked_id == 1)
        self.next_scene_input.setEnabled(next_enabled)
        self.next_scene_combo.setEnabled(next_enabled)
        # 启用/禁用选项分支控件
        branch_enabled = (checked_id == 2)
        for inp in self.option_inputs:
            inp.setEnabled(branch_enabled)
        for inp in self.option_scene_inputs:
            inp.setEnabled(branch_enabled)
        for combo in self.option_scene_combos:
            combo.setEnabled(branch_enabled)
        
        # 处理execute单选按钮的状态
        end_enabled = (checked_id == 0)
        self.execute_null_radio.setEnabled(end_enabled)
        self.execute_java_radio.setEnabled(end_enabled)
        self.execute_command_radio.setEnabled(end_enabled)
        
        if end_enabled:
            execute_checked_id = self.execute_radio_group.checkedId()
            java_enabled = (execute_checked_id == 1)
            command_enabled = (execute_checked_id == 2)
            self.java_input.setEnabled(java_enabled)
            self.command_input.setEnabled(command_enabled)
        else:
            self.java_input.setEnabled(False)
            self.command_input.setEnabled(False)
    
    def load_data(self):
        """加载数据"""
        if not self.next_data or not isinstance(self.next_data, dict):
            self.radio_end.setChecked(True)
        else:
            next_type = self.next_data.get("type", "end")
            next_data_list = self.next_data.get("data", [])
            
            if next_type == "end":
                self.radio_end.setChecked(True)
            elif next_type == "next":
                self.radio_next.setChecked(True)
                # 从data第一个元素获取refer
                if isinstance(next_data_list, list) and len(next_data_list) > 0:
                    first_item = next_data_list[0]
                    if isinstance(first_item, dict) and "refer" in first_item:
                        refer = first_item["refer"]
                        # 如果refer包含"text/"，只取后面的文件名
                        if "text/" in refer:
                            refer = refer.split("text/")[-1]
                        self.next_scene_input.setText(refer)
            elif next_type == "choice":
                self.radio_branch.setChecked(True)
                # 加载选项，不超过4个
                if isinstance(next_data_list, list):
                    for i, item in enumerate(next_data_list):
                        if i < 4 and isinstance(item, dict):
                            self.option_inputs[i].setText(str(item.get("text", "")))
                            refer = str(item.get("refer", ""))
                            self.option_scene_inputs[i].setText(refer)
            else:
                self.radio_end.setChecked(True)
        
        # 加载execute数据
        if not self.execute_data or not isinstance(self.execute_data, dict):
            self.execute_null_radio.setChecked(True)
            return
        
        execute_type = self.execute_data.get("type", "null")
        execute_data_list = self.execute_data.get("data", [])
        
        if execute_type == "null" or execute_type is None:
            self.execute_null_radio.setChecked(True)
        elif execute_type == "java":
            self.execute_java_radio.setChecked(True)
            if isinstance(execute_data_list, list) and len(execute_data_list) > 0:
                self.java_input.setText(str(execute_data_list[0]))
        else:
            self.execute_command_radio.setChecked(True)
            if isinstance(execute_data_list, list):
                self.command_input.setText("\n".join(str(x) for x in execute_data_list))
    
    def accept_and_save(self):
        """保存并关闭"""
        checked_id = self.radio_group.checkedId()
        if checked_id == 0:
            # 直接结束
            self.next_data = {"type": "end", "data": []}
        elif checked_id == 1:
            # 接着下一节
            refer = self.next_scene_input.text().strip()
            self.next_data = {
                "type": "next",
                "data": [{"refer": refer}]
            }
        elif checked_id == 2:
            # 选项分支
            data_list = []
            for i, inp in enumerate(self.option_inputs):
                refer = self.option_scene_inputs[i].text().strip()
                text = inp.text().strip()
                if text:
                    data_list.append({
                        "text": text,
                        "refer": refer
                    })
            self.next_data = {
                "type": "choice",
                "data": data_list
            }
        
        # 保存execute数据
        execute_checked_id = self.execute_radio_group.checkedId()
        if execute_checked_id == 0:
            # 不执行
            self.execute_data = {
                "type": "null",
                "data": []
            }
        elif execute_checked_id == 1:
            # 执行Java代码
            java_value = self.java_input.text().strip()
            self.execute_data = {
                "type": "java",
                "data": [java_value] if java_value else []
            }
        else:
            # 执行指令
            command_text = self.command_input.toPlainText()
            commands = [line.strip() for line in command_text.split("\n") if line.strip()]
            self.execute_data = {
                "type": "command",
                "data": commands
            }
        
        self.accept()


class FileEditorWindow(QMainWindow):
    """文件编辑窗口"""
    def __init__(self, file_path,res_manager, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.json_data = {}
        self.data_input_fields = {}
        self.right_input_fields = {}
        self.project_dir = parent.current_project_dir
        
        # 初始化资源管理器
        self.res_manager = res_manager
        
        self.init_ui()
        self.setStyleSheet(APP_STYLESHEET)
        self.load_json_data()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(f"编辑文件 - {self.file_name}")
        self.setFixedSize(1600, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧面板 (2/3)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_widget = QWidget()
        self.left_layout = QVBoxLayout(left_widget)
        left_scroll.setWidget(left_widget)
        main_layout.addWidget(left_scroll, 2)
        
        # 右侧面板 (1/3)
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_widget = QWidget()
        self.right_layout = QVBoxLayout(right_widget)
        right_scroll.setWidget(right_widget)
        main_layout.addWidget(right_scroll, 1)
        
        # 保存按钮
        save_button = QPushButton("保存文件")
        save_button.clicked.connect(self.save_json_data)
        self.right_layout.addWidget(save_button)
        
        # 图片预览框
        self.preview_label = QLabel("图片预览")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.preview_label.setMinimumHeight(300)
        self.right_layout.addWidget(self.preview_label)
        
        self.right_layout.addStretch()
    
    def load_json_data(self):
        """加载JSON文件数据"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            self.populate_left_panel()
            self.populate_right_panel()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载文件失败: {str(e)}")
    
    def populate_left_panel(self):
        """填充左侧面板：data列表"""
        # 清空左侧布局
        while self.left_layout.count() > 0:
            item = self.left_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
        
        self.data_input_fields.clear()
        self.expand_widgets = {}
        
        # 添加标题
        title_label = QLabel("Data 列表")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.left_layout.addWidget(title_label)
        
        # 遍历data列表
        data_list = self.json_data.get("data", [])
        for idx, item in enumerate(data_list):
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            
            # 第一行：text、展开按钮、新建按钮和删除按钮
            top_layout = QHBoxLayout()
            
            # text字段
            text_label = QLabel("内容:")
            text_label.setFixedWidth(80)
            text_input = QLineEdit(str(item.get("text", "")))
            self.data_input_fields[(idx, "text")] = text_input
            top_layout.addWidget(text_label)
            top_layout.addWidget(text_input)
            
            # 展开/收起按钮
            expand_btn = QPushButton("展开")
            expand_btn.setCheckable(True)
            expand_btn.clicked.connect(lambda checked, i=idx, btn=expand_btn: self.toggle_expand(i, btn))
            top_layout.addWidget(expand_btn)
            
            # 在这个下面新建按钮
            new_btn = QPushButton("在这个下面新建")
            new_btn.clicked.connect(lambda checked, i=idx: self.add_data_element_below(i))
            top_layout.addWidget(new_btn)
            
            # 删除此节按钮
            delete_btn = QPushButton("删除此节")
            delete_btn.clicked.connect(lambda checked, i=idx: self.delete_data_element(i))
            top_layout.addWidget(delete_btn)
            
            item_layout.addLayout(top_layout)
            
            # 展开区域（默认隐藏）
            expand_widget = QWidget()
            expand_layout = QVBoxLayout(expand_widget)
            expand_widget.setVisible(False)
            self.expand_widgets[idx] = expand_widget
            
            # background字段
            bg_layout = QHBoxLayout()
            bg_label = QLabel("背景:")
            bg_label.setFixedWidth(80)
            bg_input = QLineEdit(str(item.get("background", "")))
            self.data_input_fields[(idx, "background")] = bg_input
            bg_layout.addWidget(bg_label)
            bg_layout.addWidget(bg_input, 3)
            
            # background下拉选择框
            bg_combo = QComboBox()
            bg_combo.setEditable(False)
            bg_combo.setFixedWidth(400)
            bg_combo.addItem("")
            bg_list = self.res_manager.get_list("background")
            for bg in bg_list:
                bg_combo.addItem(bg)
            bg_combo.currentTextChanged.connect(lambda text, inp=bg_input: self.convert_and_set_filename(text, inp, "background"))
            bg_layout.addWidget(bg_combo, 1)
            
            # 背景预览按钮
            bg_preview_btn = QPushButton("预览")
            bg_preview_btn.clicked.connect(lambda checked, inp=bg_input: self.preview_image(inp.text(), "background"))
            bg_layout.addWidget(bg_preview_btn)
            expand_layout.addLayout(bg_layout)
            
            # sound字段
            sound_layout = QHBoxLayout()
            sound_label = QLabel("语音:")
            sound_label.setFixedWidth(80)
            sound_input = QLineEdit(str(item.get("sound", "")))
            self.data_input_fields[(idx, "sound")] = sound_input
            sound_layout.addWidget(sound_label)
            sound_layout.addWidget(sound_input, 3)
            
            # sound下拉选择框
            sound_combo = QComboBox()
            sound_combo.setEditable(False)
            sound_combo.setFixedWidth(400)
            sound_combo.addItem("")
            voice_list = self.res_manager.get_list("voice")
            for voice in voice_list:
                sound_combo.addItem(voice)
            sound_combo.currentTextChanged.connect(lambda text, inp=sound_input: self.convert_and_set_filename(text, inp, "voice"))
            sound_layout.addWidget(sound_combo, 1)
            expand_layout.addLayout(sound_layout)
            
            # character字段
            character = item.get("character", {})
            
            # character.image
            char_image_layout = QHBoxLayout()
            char_image_label = QLabel("角色图片:")
            char_image_label.setFixedWidth(80)
            char_image_input = QLineEdit(str(character.get("image", "")))
            self.data_input_fields[(idx, "character.image")] = char_image_input
            char_image_layout.addWidget(char_image_label)
            char_image_layout.addWidget(char_image_input, 3)
            
            # character.image下拉选择框
            char_combo = QComboBox()
            char_combo.setEditable(False)
            char_combo.setFixedWidth(400)
            char_combo.addItem("")
            char_list = self.res_manager.get_list("character")
            for char in char_list:
                char_combo.addItem(char)
            char_combo.currentTextChanged.connect(lambda text, inp=char_image_input: self.convert_and_set_filename(text, inp, "character"))
            char_image_layout.addWidget(char_combo, 1)
            
            # 角色图片预览按钮
            char_preview_btn = QPushButton("预览")
            char_preview_btn.clicked.connect(lambda checked, inp=char_image_input: self.preview_image(inp.text(), "character"))
            char_image_layout.addWidget(char_preview_btn)
            expand_layout.addLayout(char_image_layout)
            
            # character.x
            char_x_layout = QHBoxLayout()
            char_x_label = QLabel("角色X坐标:")
            char_x_label.setFixedWidth(80)
            char_x_input = QLineEdit(str(character.get("x", "")))
            self.data_input_fields[(idx, "character.x")] = char_x_input
            char_x_layout.addWidget(char_x_label)
            char_x_layout.addWidget(char_x_input)
            expand_layout.addLayout(char_x_layout)
            
            # character.y
            char_y_layout = QHBoxLayout()
            char_y_label = QLabel("角色Y坐标:")
            char_y_label.setFixedWidth(80)
            char_y_input = QLineEdit(str(character.get("y", "")))
            self.data_input_fields[(idx, "character.y")] = char_y_input
            char_y_layout.addWidget(char_y_label)
            char_y_layout.addWidget(char_y_input)
            expand_layout.addLayout(char_y_layout)
            
            # character.circle
            char_circle_layout = QHBoxLayout()
            char_circle_label = QLabel("角色图片缩放（未实现）:")
            char_circle_label.setFixedWidth(80)
            char_circle_input = QLineEdit(str(character.get("circle", "")))
            self.data_input_fields[(idx, "character.circle")] = char_circle_input
            char_circle_layout.addWidget(char_circle_label)
            char_circle_layout.addWidget(char_circle_input)
            expand_layout.addLayout(char_circle_layout)
            
            # 特殊渲染设置按钮
            render_btn = QPushButton("特殊渲染设置")
            render_btn.clicked.connect(lambda checked, i=idx: self.open_render_settings(i))
            render_btn.setEnabled(False)
            expand_layout.addWidget(render_btn)
            
            item_layout.addWidget(expand_widget)
            self.left_layout.addWidget(item_widget)
        
        self.left_layout.addStretch()
    
    def get_image_path(self, filename, resource_type):
        """根据文件名和资源类型获取完整的图片路径"""
        if not self.project_dir or not filename:
            return None
        
        dir_mapping = {
            "background": "assets/galmc_api/texture/background",
            "character": "assets/galmc_api/texture/character",
            "cg": "assets/galmc_api/texture/cg"
        }
        
        # 如果已经是完整路径，直接返回
        if os.path.isabs(filename):
            return filename
        
        # 从save_id的路径中提取文件名
        if "/" in filename:
            filename = filename.split("/")[-1]
        
        if resource_type in dir_mapping:
            full_path = os.path.join(self.project_dir, dir_mapping[resource_type], filename)
            if os.path.exists(full_path):
                return full_path
        return None
    
    def convert_and_set_filename(self, filename, input_field, resource_type):
        """
        转换文件名并设置到文本输入框
        使用res_manager.save_id进行转换
        """
        if filename:
            converted_filename = self.res_manager.save_id(resource_type, filename)
            input_field.setText(converted_filename)
    
    def save_current_inputs(self):
        """保存当前所有输入框的内容到json_data"""
        for (idx, field), input_field in self.data_input_fields.items():
            value = input_field.text()
            if idx < len(self.json_data.get("data", [])):
                if "." in field:
                    # 嵌套字段，如 character.image
                    parts = field.split(".")
                    obj = self.json_data["data"][idx]
                    for part in parts[:-1]:
                        if part not in obj:
                            obj[part] = {}
                        obj = obj[part]
                    obj[parts[-1]] = value
                    
                    # 如果是character.image，获取图片尺寸并设置image_x和image_y
                    if field == "character.image" and value:
                        image_path = self.get_image_path(value, "character")
                        if image_path and os.path.exists(image_path):
                            pixmap = QPixmap(image_path)
                            if not pixmap.isNull():
                                if "character" not in self.json_data["data"][idx]:
                                    self.json_data["data"][idx]["character"] = {}
                                self.json_data["data"][idx]["character"]["image_x"] = pixmap.width()
                                self.json_data["data"][idx]["character"]["image_y"] = pixmap.height()
                else:
                    # 直接字段
                    self.json_data["data"][idx][field] = value
    
    def toggle_expand(self, index, button):
        """切换展开/收起状态"""
        # 先保存当前输入
        self.save_current_inputs()
        if index in self.expand_widgets:
            is_expanded = button.isChecked()
            self.expand_widgets[index].setVisible(is_expanded)
            button.setText("收起" if is_expanded else "展开")
    
    def add_data_element_below(self, index):
        """在指定索引下面添加新元素"""
        # 先保存当前输入
        self.save_current_inputs()
        
        new_element = {
            "text": "",
            "character": {
                "image": "",
                "image_x": 0,
                "image_y": 0,
                "circle": 1.0,
                "x": 660,
                "y": 0
            },
            "background": "",
            "sound": "null",
            "render_execute": {
                "type": "normal",
                "data": ""
            }
        }
        
        if "data" not in self.json_data:
            self.json_data["data"] = []
        
        self.json_data["data"].insert(index + 1, new_element)
        self.populate_left_panel()
    
    def open_render_settings(self, index):
        """打开特殊渲染设置窗口（占位功能）"""
        QMessageBox.information(self, "提示", f"打开元素 {index} 的特殊渲染设置窗口的功能待实现")
    
    def preview_image(self, filename, image_type):
        """在图片框中显示预览图片"""
        if not hasattr(self, 'preview_label') or self.preview_label is None:
            return
        
        if not filename or not self.project_dir:
            self.preview_label.setText("图片预览\n（无图片）")
            self.preview_label.setPixmap(QPixmap())
            return
        
        # 从完整路径中提取原始文件名

        
        # 确定图片目录
        if image_type == "background":
            image_dir = os.path.join(self.project_dir, "assets/galmc_api/")
        elif image_type == "character":
            image_dir = os.path.join(self.project_dir, "assets/galmc_api/texture/character")
            if "/" in filename:
                filename = filename.split("/")[-1]
            if "\\" in filename:
                filename = filename.split("\\")[-1]
        else:
            self.preview_label.setText("图片预览\n（无效类型）")
            self.preview_label.setPixmap(QPixmap())
            return
        
        image_path = os.path.join(image_dir, filename)

        if os.path.exists(image_path):
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # 缩放图片以适应预览框
                    scaled_pixmap = pixmap.scaled(
                        self.preview_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.preview_label.setPixmap(scaled_pixmap)
                else:
                    self.preview_label.setText("图片预览\n（无法加载图片）")
                    self.preview_label.setPixmap(QPixmap())
            except Exception as e:
                print(str(e))
                self.preview_label.setText("图片预览\n（加载出错）")
                self.preview_label.setPixmap(QPixmap())
        else:
            self.preview_label.setText("图片预览\n（文件不存在）")
            self.preview_label.setPixmap(QPixmap())

    
    def delete_data_element(self, index):
        """删除指定索引的data元素"""
        # 先保存当前输入
        self.save_current_inputs()
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除此节吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if "data" in self.json_data and index < len(self.json_data["data"]):
                del self.json_data["data"][index]
                self.populate_left_panel()
    
    def populate_right_panel(self):
        """填充右侧面板"""
        # 清空右侧布局（保留保存按钮、预览标签和stretch）
        # 先取出保存按钮、预览标签和stretch
        save_button = None
        preview_label = None
        stretch_item = None
        items_to_keep = []
        while self.right_layout.count() > 0:
            item = self.right_layout.takeAt(0)
            if item.widget():
                if isinstance(item.widget(), QPushButton) and item.widget().text() == "保存文件":
                    save_button = item.widget()
                elif hasattr(self, 'preview_label') and item.widget() is self.preview_label:
                    preview_label = item.widget()
                else:
                    item.widget().deleteLater()
            elif item.spacerItem():
                stretch_item = item.spacerItem()
            elif item.layout():
                self.clear_layout(item.layout())
        
        self.right_input_fields.clear()
        
        # 添加标题
        title_label = QLabel("文件属性")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.right_layout.addWidget(title_label)
        
        # 添加文件名修改选项
        filename_layout = QHBoxLayout()
        filename_label = QLabel("文件名:")
        filename_label.setFixedWidth(80)
        self.filename_input = QLineEdit(self.file_name)
        rename_btn = QPushButton("重命名")
        rename_btn.clicked.connect(self.rename_file)
        filename_layout.addWidget(filename_label)
        filename_layout.addWidget(self.filename_input)
        filename_layout.addWidget(rename_btn)
        self.right_layout.addLayout(filename_layout)
        
        # 处理 render_execute
        self.add_key_value_to_right("render_execute", self.json_data.get("render_execute", ""))
        
        # 处理 start_music 下的 music（类似左边栏语音的设计）
        start_music = self.json_data.get("start_music", {})
        if "music" in start_music:
            music_layout = QHBoxLayout()
            music_label = QLabel("音乐:")
            music_label.setFixedWidth(150)
            music_input = QLineEdit(str(start_music["music"]))
            self.right_input_fields["start_music.music"] = music_input
            music_layout.addWidget(music_label)
            music_layout.addWidget(music_input, 3)
            
            # music下拉选择框
            music_combo = QComboBox()
            music_combo.setEditable(False)
            music_combo.setFixedWidth(150)
            music_combo.addItem("")
            music_list = self.res_manager.get_list("musics")
            for music in music_list:
                music_combo.addItem(music)
            music_combo.currentTextChanged.connect(
                lambda text, inp=music_input: self.convert_and_set_filename(text, inp, "musics")
            )
            music_layout.addWidget(music_combo, 1)
            self.right_layout.addLayout(music_layout)
        
        # 处理特殊键：next, execute, resources
        chinese_key={
            "next":"下一节设置",
            "execute":"结束后执行",
            "resources":"额外资源",
        }
        
        special_keys = ["next", "execute", "resources"]
        for key in special_keys:
            if key in self.json_data:
                btn_layout = QHBoxLayout()
                btn_label = QLabel(f"{chinese_key[key] or key}:")
                btn = QPushButton(f"打开 {key} 窗口")
                btn.clicked.connect(lambda checked, k=key: self.open_special_window(k))
                btn_layout.addWidget(btn_label)
                btn_layout.addWidget(btn)
                self.right_layout.addLayout(btn_layout)
        
        # 重新添加保存按钮
        if save_button:
            self.right_layout.addWidget(save_button)
        
        # 重新添加预览标签
        if preview_label:
            self.right_layout.addWidget(preview_label)
        elif hasattr(self, 'preview_label'):
            self.right_layout.addWidget(self.preview_label)
        
        # 重新添加stretch
        if stretch_item:
            self.right_layout.addItem(stretch_item)
    
    def rename_file(self):
        """重命名文件"""
        new_filename = self.filename_input.text().strip()
        if not new_filename:
            QMessageBox.warning(self, "错误", "文件名不能为空")
            return
        
        if not new_filename.endswith(".json"):
            new_filename += ".json"
        
        if new_filename == self.file_name:
            QMessageBox.information(self, "提示", "文件名未改变")
            return
        
        new_file_path = os.path.join(os.path.dirname(self.file_path), new_filename)
        
        if os.path.exists(new_file_path):
            reply = QMessageBox.question(
                self, 
                "确认", 
                f"文件 {new_filename} 已存在，是否覆盖？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        try:
            os.rename(self.file_path, new_file_path)
            self.file_path = new_file_path
            self.file_name = new_filename
            self.setWindowTitle(f"编辑文件 - {self.file_name}")
            QMessageBox.information(self, "成功", f"文件已重命名为 {new_filename}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"重命名文件失败: {str(e)}")
        self.res_manager.reset()
    
    def add_key_value_to_right(self, key, value):
        """添加键值对到右侧面板"""
        h_layout = QHBoxLayout()
        chinese_key={
            "render_execute":"特殊渲染设置",
            "start_music.music":"音乐"
        }
        key_label = QLabel(f"{chinese_key[key] or key}")
        key_label.setFixedWidth(150)
        value_input = QLineEdit(str(value))
        self.right_input_fields[key] = value_input
        h_layout.addWidget(key_label)
        h_layout.addWidget(value_input)
        self.right_layout.addLayout(h_layout)
    
    def edit_data_element(self, index):
        """编辑data列表中的元素（占位功能）"""
        QMessageBox.information(self, "提示", f"编辑元素 {index} 的功能待实现")
    
    def open_special_window(self, key):
        """打开特殊窗口"""
        if key == "next":
            # 打开next窗口
            next_data = self.json_data.get(key, {})
            execute_data = self.json_data.get("execute", {})
            dialog = NextWindow(next_data, execute_data, self.project_dir, self.res_manager, self)
            if dialog.exec_() == QDialog.Accepted:
                self.json_data[key] = dialog.next_data
                self.json_data["execute"] = dialog.execute_data
        else:
            QMessageBox.information(self, "提示", f"打开 {key} 窗口的功能待实现")
    
    def replace_empty_strings_with_null(self, data):
        """递归将数据中的空字符串替换为"null"字符串"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and value.strip() == "":
                    data[key] = "null"
                else:
                    self.replace_empty_strings_with_null(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str) and item.strip() == "":
                    data[i] = "null"
                else:
                    self.replace_empty_strings_with_null(item)
    
    def save_json_data(self):
        """保存JSON数据到文件"""
        try:
            # 更新data列表
            data_list = self.json_data.get("data", [])
            for (idx, field), input_widget in self.data_input_fields.items():
                if idx < len(data_list):
                    if "." in field:
                        # 处理嵌套字段，如 character.image
                        keys = field.split(".")
                        current = data_list[idx]
                        for k in keys[:-1]:
                            if k not in current:
                                current[k] = {}
                            current = current[k]
                        value = input_widget.text()
                        current[keys[-1]] = value
                        
                        # 如果是character.image，获取图片尺寸并设置image_x和image_y
                        if field == "character.image" and value:
                            image_path = self.get_image_path(value, "character")
                            if image_path and os.path.exists(image_path):
                                pixmap = QPixmap(image_path)
                                if not pixmap.isNull():
                                    if "character" not in data_list[idx]:
                                        data_list[idx]["character"] = {}
                                    data_list[idx]["character"]["image_x"] = pixmap.width()
                                    data_list[idx]["character"]["image_y"] = pixmap.height()
                    else:
                        data_list[idx][field] = input_widget.text()
            
            # 更新右侧字段
            for key, input_widget in self.right_input_fields.items():
                if "." in key:
                    # 处理嵌套键，如 start_music.music
                    keys = key.split(".")
                    current = self.json_data
                    for k in keys[:-1]:
                        if k not in current:
                            current[k] = {}
                        current = current[k]
                    current[keys[-1]] = input_widget.text()
                else:
                    self.json_data[key] = input_widget.text()
            
            # 如果类型为cg，遍历data列表，将character.image_x和image_y设置为background图片的长宽
            if self.json_data.get("type") == "cg":
                for item in data_list:
                    background = item.get("background", "")
                    if background and background != "null":
                        # 根据路径判断是background还是cg
                        if "texture/background/" in background:
                            resource_type = "background"
                        else:
                            resource_type = "cg"
                        image_path = self.get_image_path(background, resource_type)
                        if image_path and os.path.exists(image_path):
                            pixmap = QPixmap(image_path)
                            if not pixmap.isNull():
                                if "character" not in item:
                                    item["character"] = {}
                                item["character"]["image_x"] = pixmap.width()
                                item["character"]["image_y"] = pixmap.height()
            
            # 如果有音乐文件，更新length参数
            if "start_music" in self.json_data and isinstance(self.json_data["start_music"], dict):
                music_id = self.json_data["start_music"].get("music", "")
                if music_id and music_id != "null" and self.res_manager:
                    length = self.res_manager.get_music_length(music_id)
                    self.json_data["start_music"]["length"] = length
            
            # 复制数据以避免修改原始数据
            data_to_save = json.loads(json.dumps(self.json_data))
            
            # 将空字符串替换为"null"
            self.replace_empty_strings_with_null(data_to_save)
            
            # 保存到文件
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存文件失败: {str(e)}")
    
    def clear_layout(self, layout):
        """递归清空布局"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())


class MainWindow(QMainWindow):
    character = {}
    def __init__(self):
        super().__init__()
        self.current_project_dir = None  # 当前打开的项目目录
        self.current_directory = "text"  # 当前显示的目录
        self.init_ui()
        self.setStyleSheet(APP_STYLESHEET)
        self.create_menu()

    def init_ui(self):
        """初始化主窗口界面"""
        self.setWindowTitle("GalMC 项目制作管理器")
        self.setFixedSize(1280, 720)
        self.setMinimumSize(1100, 680)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # 左侧区域 (比例1:3)
        left_widget = QWidget()
        self.left_layout = QVBoxLayout(left_widget)
        # 存储配置文件数据和输入框
        self.config_data = {}
        self.input_fields = {}
        self.load_config_data()
        main_layout.addWidget(left_widget, 1)

        # 右侧区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 新建文件按钮
        self.new_file_button = QPushButton("新建文件")
        self.new_file_button.clicked.connect(self.on_new_file_clicked)
        self.new_file_button.setEnabled(False)  # 初始禁用
        button_layout.addWidget(self.new_file_button)
        
        # 文本按钮
        self.text_button = QPushButton("文本")
        self.text_button.clicked.connect(self.on_text_button_clicked)
        self.text_button.setEnabled(False)  # 初始禁用
        button_layout.addWidget(self.text_button)
        
        # CG按钮
        self.cg_button = QPushButton("CG")
        self.cg_button.clicked.connect(self.on_cg_button_clicked)
        self.cg_button.setEnabled(False)  # 初始禁用
        button_layout.addWidget(self.cg_button)
        
        right_layout.addLayout(button_layout)

        # 文件表格
        self.file_table = QTableWidget()
        self.file_table.setAlternatingRowColors(True)
        self.file_table.setColumnCount(2)
        self.file_table.setHorizontalHeaderLabels(["文件名", "描述"])
        self.file_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.file_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.file_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.file_table.doubleClicked.connect(self.on_file_double_clicked)
        self.file_table.setEnabled(False)
        self.file_table.verticalHeader().setVisible(False)
        right_layout.addWidget(self.file_table)

        main_layout.addWidget(right_widget, 3)

    def create_menu(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        # 打开目录
        self.open_dir_action = QAction("打开目录", self)
        self.open_dir_action.triggered.connect(self.open_directory)
        file_menu.addAction(self.open_dir_action)

        # 导入资源子菜单
        self.import_menu = QMenu("导入资源", self)

        self.import_bg_action = QAction("导入背景", self)
        self.import_bg_action.triggered.connect(lambda: self.import_resource("背景"))
        self.import_bg_action.setEnabled(False)
        self.import_menu.addAction(self.import_bg_action)

        self.import_cg_action = QAction("导入CG", self)
        self.import_cg_action.triggered.connect(lambda: self.import_resource("CG"))
        self.import_cg_action.setEnabled(False)
        self.import_menu.addAction(self.import_cg_action)

        self.import_char_action = QAction("导入人物", self)
        self.import_char_action.triggered.connect(lambda: self.import_resource("人物"))
        self.import_char_action.setEnabled(False)
        self.import_menu.addAction(self.import_char_action)

        self.import_voice_action = QAction("导入语音", self)
        self.import_voice_action.triggered.connect(lambda: self.import_resource("语音"))
        self.import_voice_action.setEnabled(False)
        self.import_menu.addAction(self.import_voice_action)

        self.import_music_action = QAction("导入音乐", self)
        self.import_music_action.triggered.connect(lambda: self.import_resource("音乐"))
        self.import_music_action.setEnabled(False)
        self.import_menu.addAction(self.import_music_action)

        self.import_menu.setEnabled(False)
        file_menu.addMenu(self.import_menu)

        # 打包导出
        self.export_action = QAction("打包导出", self)
        self.export_action.triggered.connect(self.package_export)
        self.export_action.setEnabled(False)
        file_menu.addAction(self.export_action)

    def open_directory(self):
        """打开目录并初始化项目结构"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择项目目录")
        if dir_path:
            self.current_project_dir = dir_path
            self.init_project_structure(dir_path)
            self.load_config_data()
            self.load_file_list()
            self.enable_all_features(True)
            self.res = Resources_Manager(dir_path)
    
    def enable_all_features(self, enabled):
        """启用或禁用所有功能"""
        # 启用/禁用按钮
        self.new_file_button.setEnabled(enabled)
        self.text_button.setEnabled(enabled)
        self.cg_button.setEnabled(enabled)
        
        # 启用/禁用文件表格
        self.file_table.setEnabled(enabled)
        
        # 启用/禁用菜单
        self.import_menu.setEnabled(enabled)
        self.import_bg_action.setEnabled(enabled)
        self.import_cg_action.setEnabled(enabled)
        self.import_char_action.setEnabled(enabled)
        self.import_voice_action.setEnabled(enabled)
        self.import_music_action.setEnabled(enabled)
        self.export_action.setEnabled(enabled)
        
        # 启用/禁用左侧栏输入框
        for key, input_field in self.input_fields.items():
            input_field.setEnabled(enabled)

    def init_project_structure(self, root_dir):
        """
        检查并创建项目目录结构和配置文件
        """
        # 定义需要创建的目录列表（相对于根目录）
        dirs = [
            "assets/galmc_api/data/text",
            "assets/galmc_api/data/execute",
            "assets/galmc_api/texture/cg",
            "assets/galmc_api/texture/character",
            "assets/galmc_api/texture/background",
            "assets/galmc_api/sounds/character",
            "assets/galmc_api/sounds/music",
            "assets/galmc_api/data/cg",
            "assets/galmc_api/texture/gui",
        ]

        # 创建目录
        for d in dirs:
            full_path = os.path.join(root_dir, d)
            os.makedirs(full_path, exist_ok=True)

        # 创建 config.json（如果不存在）
        config_path = os.path.join(root_dir, "config.json")
        if not os.path.exists(config_path):
            default_config = {
                "name": "New Project"
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)

        # 创建 assets/galmc_api/sound.json（如果不存在）
        sound_path = os.path.join(root_dir, "assets/galmc_api/sounds.json")
        if not os.path.exists(sound_path):
            with open(sound_path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)  # 空对象
        
        # 复制必要文件
        self.copy_required_files(root_dir)
    
    def copy_required_files(self, root_dir):
        """复制必要的文件到项目目录"""
        import shutil
        
        # 程序所在目录的assets路径
        program_assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        
        # 复制 pack.mcmeta 到项目目录
        pack_mcmeta_src = os.path.join(program_assets_dir, "pack.mcmeta")
        if os.path.exists(pack_mcmeta_src):
            pack_mcmeta_dst = os.path.join(root_dir, "pack.mcmeta")
            if not os.path.exists(pack_mcmeta_dst):
                shutil.copy2(pack_mcmeta_src, pack_mcmeta_dst)
        
        # 复制 air.png 到 assets/galmc_api/texture/character/
        air_png_src = os.path.join(program_assets_dir, "air.png")
        if os.path.exists(air_png_src):
            air_png_dst = os.path.join(root_dir, "assets/galmc_api/texture/character/air.png")
            if not os.path.exists(air_png_dst):
                shutil.copy2(air_png_src, air_png_dst)
        
        # 复制 text.png 到 assets/galmc_api/texture/gui/
        text_png_src = os.path.join(program_assets_dir, "text.png")
        if os.path.exists(text_png_src):
            text_png_dst = os.path.join(root_dir, "assets/galmc_api/texture/gui/text.png")
            if not os.path.exists(text_png_dst):
                shutil.copy2(text_png_src, text_png_dst)


    def load_file_list(self, directory="text"):
        """加载指定目录下的 JSON 文件到表格"""
        if not self.current_project_dir:
            return

        # 更新当前目录
        self.current_directory = directory

        target_dir = os.path.join(self.current_project_dir, f"assets/galmc_api/data/{directory}")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        # 清空表格
        self.file_table.setRowCount(0)

        # 遍历所有 .json 文件
        for file_name in os.listdir(target_dir):
            if file_name.endswith(".json"):
                file_path = os.path.join(target_dir, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    description = data.get("author", "")
                except Exception as e:
                    description = f"读取失败: {str(e)}"

                # 添加一行
                row = self.file_table.rowCount()
                self.file_table.insertRow(row)

                # 文件名列
                name_item = QTableWidgetItem(file_name)
                name_item.setData(Qt.UserRole, file_path)  # 存储完整路径便于双击
                self.file_table.setItem(row, 0, name_item)

                # 描述列
                desc_item = QTableWidgetItem(description)
                self.file_table.setItem(row, 1, desc_item)

    def on_file_double_clicked(self, index):
        """双击表格项，打开编辑窗口"""
        if not self.current_project_dir:
            QMessageBox.warning(self, "错误", "请先打开项目目录")
            return
        row = index.row()
        file_name_item = self.file_table.item(row, 0)
        if file_name_item:
            file_path = file_name_item.data(Qt.UserRole)
            # 打开文件编辑窗口
            editor = FileEditorWindow(file_path,self.res,self)
            editor.show()

    def on_new_file_clicked(self):
        """新建文件按钮点击事件"""
        if not self.current_project_dir:
            QMessageBox.warning(self, "错误", "请先打开项目目录")
            return
        
        # 根据当前目录确定源文件和目标目录
        if self.current_directory == "text":
            source_file = os.path.join(os.path.dirname(__file__), "assets", "example_text.json")
            target_dir = os.path.join(self.current_project_dir, "assets/galmc_api/data/text")
            file_name = "example_text.json"
        elif self.current_directory == "cg":
            source_file = os.path.join(os.path.dirname(__file__), "assets", "example_cg.json")
            target_dir = os.path.join(self.current_project_dir, "assets/galmc_api/data/cg")
            file_name = "example_cg.json"
        else:
            QMessageBox.warning(self, "错误", "当前目录不支持新建文件")
            return
        
        # 确保目标目录存在
        os.makedirs(target_dir, exist_ok=True)
        
        # 检查源文件是否存在
        if not os.path.exists(source_file):
            QMessageBox.warning(self, "错误", f"样例文件不存在: {source_file}")
            return
        
        # 复制文件
        try:
            import shutil
            target_file = os.path.join(target_dir, file_name)
            shutil.copy2(source_file, target_file)
            
            # 重新加载文件列表
            self.load_file_list(self.current_directory)
            
            # 打开样例文本编辑框
            editor = FileEditorWindow(target_file,self.res,self)
            editor.show()
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"创建文件失败: {str(e)}")

        self.res.reset()
    
    def on_cg_button_clicked(self):
        """CG按钮点击事件，显示assets\galmc_api\data\cg目录下的文件"""
        self.res.reset()
        self.load_file_list("cg")
    
    def on_text_button_clicked(self):
        """文本按钮点击事件，显示assets\galmc_api\data\text目录下的文件"""
        self.res.reset()
        self.load_file_list("text")

    def import_resource(self, resource_type):
        """导入资源"""
        # 根据资源类型确定文件过滤器
        file_filters = {
            "背景": "图片文件 (*.png)",
            "CG": "图片文件 (*.png)",
            "人物": "图片文件 (*.png)",
            "语音": "音频文件 (*.ogg)",
            "音乐": "音频文件 (*.ogg)"
        }
        
        # 打开文件选择框（可多选）
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter(file_filters.get(resource_type, "所有文件 (*.*)"))
        file_dialog.setWindowTitle(f"选择{resource_type}文件")
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            selected_files = file_dialog.selectedFiles()
            if not selected_files:
                return
            
            # 确定目标文件夹路径
            target_dir = self.get_target_directory(resource_type)
            if not target_dir:
                QMessageBox.warning(self, "错误", "无法确定目标文件夹路径")
                return
            
            # 确保目标文件夹存在
            os.makedirs(target_dir, exist_ok=True)
            
            # 复制文件
            imported_count = 0
            failed_count = 0
            
            for file_path in selected_files:
                try:
                    # 获取文件名
                    file_name = os.path.basename(file_path)
                    # 目标文件路径
                    dest_path = os.path.join(target_dir, file_name)
                    
                    # 复制文件
                    import shutil
                    shutil.copy2(file_path, dest_path)
                    imported_count += 1
                except Exception as e:
                    print(f"复制文件失败 {file_path}: {str(e)}")
                    failed_count += 1
            
            # 显示结果
            if imported_count > 0:
                QMessageBox.information(self, "成功", f"成功导入 {imported_count} 个{resource_type}文件")
            if failed_count > 0:
                QMessageBox.warning(self, "错误", f"有 {failed_count} 个文件导入失败")

            self.res.reset()
    
    def get_target_directory(self, resource_type):
        """根据资源类型获取目标文件夹路径"""
        # 确定基础路径
        if self.current_project_dir:
            base_path = self.current_project_dir
        else:
            # 默认路径为程序所在目录的test文件夹
            base_path = os.path.join(os.path.dirname(__file__), "test")
        
        # 根据资源类型确定子路径
        dir_mapping = {
            "背景": "assets/galmc_api/texture/background",
            "CG": "assets/galmc_api/texture/cg",
            "人物": "assets/galmc_api/texture/character",
            "语音": "assets/galmc_api/sounds/character",
            "音乐": "assets/galmc_api/sounds/music"
        }
        
        sub_path = dir_mapping.get(resource_type)
        if not sub_path:
            return None
        
        return os.path.join(base_path, sub_path)

    def load_config_data(self):
        """加载config.json数据到左侧区域"""
        # 清空左侧布局
        while self.left_layout.count() > 0:
            widget = self.left_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        
        # 清空输入框字典
        self.input_fields.clear()
        
        # 如果没有打开目录，显示提示
        if not self.current_project_dir:
            hint_label = QLabel("请先打开项目目录")
            hint_label.setAlignment(Qt.AlignCenter)
            hint_label.setStyleSheet("color: gray; font-size: 14px;")
            self.left_layout.addWidget(hint_label)
            self.left_layout.addStretch()
            return
        
        # 确定config.json路径
        config_path = os.path.join(self.current_project_dir, "config.json")
        
        # 读取config.json
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    self.config_data = json.load(f)
            else:
                # 如果文件不存在，使用默认配置
                self.config_data = {
                    "name": "New Project"
                }
        except Exception as e:
            QMessageBox.warning(self, "错误", f"读取config.json失败: {str(e)}")
            self.config_data = {
                "name": "New Project"
            }
        
        chinese_config={
            "name": "项目名称（必填）"
        }
        
        # 显示键值对
        for key, value in self.config_data.items():
            # 创建水平布局
            h_layout = QHBoxLayout()
            
            # 键标签
            key_label = QLabel(f"{chinese_config.get(key, key)}:")
            key_label.setFixedWidth(80)
            h_layout.addWidget(key_label)
            
            # 值输入框
            input_field = QLineEdit(str(value))
            self.input_fields[key] = input_field
            h_layout.addWidget(input_field)
            
            # 添加到左侧布局
            self.left_layout.addLayout(h_layout)
        
        # 添加保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_config_data)
        self.left_layout.addWidget(save_button)
        
        # 添加大的只读文本输入框
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMinimumHeight(500)
        self.info_text.setText("作者的温馨提示：\n"
        "1.项目为测试版，不稳定，请严格按照标准填写参数，否则会导致崩溃性错误\n"
        "2.修改GUI请直接替换assets/galmc_api/texture/gui/text.png，设计按钮位置时请务必按照此软件目录下asset/ui.png的位置\n"
        "3.请格外注意填写的路径是否正确\n"
        "4.此程序依旧为测试版，不稳定，不建议整一下太离谱的操作\n"
        "5.对于“特殊渲染设置”“额外资源”等为未实现功能不要动否则会引起崩溃\n"
        "6.修改CG鉴赏请在assets/galmc_api/texture/gui/cg_background.png添加你的背景图，若要修改打开CG的物品材质请新建文件在assets/galmc_api/textures/open_cg.png\n"
        "7.若要实现特殊功能请自行编写Java代码，我将会不断完善扩展功能\n"
        "8.关于对话页面的触发，目前只有指令触发和自行编写Java代码，未来将会加入自动触发的判断"
        )
        self.left_layout.addWidget(self.info_text)
    
        
        # 添加拉伸
        self.left_layout.addStretch()
    
    def save_config_data(self):
        """保存配置数据到config.json"""
        if not self.current_project_dir:
            QMessageBox.warning(self, "错误", "请先打开项目目录")
            return
        
        # 确定config.json路径
        config_path = os.path.join(self.current_project_dir, "config.json")
        
        # 更新配置数据
        for key, input_field in self.input_fields.items():
            self.config_data[key] = input_field.text()
        
        # 保存到文件
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            
            # 更新pack.mcmeta的pack.description
            pack_mcmeta_path = os.path.join(self.current_project_dir, "pack.mcmeta")
            if os.path.exists(pack_mcmeta_path):
                with open(pack_mcmeta_path, "r", encoding="utf-8") as f:
                    pack_data = json.load(f)
                
                # 更新description为项目名称
                if "pack" in pack_data:
                    pack_data["pack"]["description"] = self.config_data.get("name", "")
                else:
                    pack_data["pack"] = {"description": self.config_data.get("name", "")}
                
                with open(pack_mcmeta_path, "w", encoding="utf-8") as f:
                    json.dump(pack_data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "成功", "配置已保存到config.json")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败: {str(e)}")
    
    def package_export(self):
        """打包导出项目目录"""
        if not self.current_project_dir:
            QMessageBox.warning(self, "错误", "请先打开项目目录")
            return
        
        # 选择导出文件路径
        default_name = os.path.basename(self.current_project_dir) + ".zip"
        export_path, _ = QFileDialog.getSaveFileName(
            self,
            "选择导出文件",
            default_name,
            "ZIP 文件 (*.zip)"
        )
        
        if not export_path:
            return
        
        try:

            
            # 获取项目名称（目录名）
            project_name = os.path.basename(self.current_project_dir)
            
            # 创建zip文件
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 遍历项目目录下的所有文件
                for root, dirs, files in os.walk(self.current_project_dir):
                    for file in files:
                        # 获取文件的完整路径
                        file_path = os.path.join(root, file)
                        # 计算在zip中的相对路径
                        arcname = os.path.relpath(file_path, self.current_project_dir)
                        # 添加到zip文件
                        zipf.write(file_path, arcname)
            
            QMessageBox.information(self, "成功", f"项目已成功导出到:\n{export_path}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
