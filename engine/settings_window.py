"""
设置窗口 —— 配置AI后端（服务商+API Key+模型）
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QGroupBox, QFormLayout, QTextEdit,
    QDialog
)
from PyQt6.QtCore import Qt

from engine.ai_engine import PROVIDERS


class SettingsWindow(QDialog):
    """设置窗口"""

    def __init__(self, ai_engine, config_manager, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.config = config_manager

        self.setWindowTitle('⚙️ HermesPet 设置')
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Dialog)
        self.setMinimumSize(400, 480)
        self.resize(440, 520)

        self._setup_ui()
        self._load_config()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── AI 后端设置 ──
        ai_group = QGroupBox('🤖 AI 后端')
        ai_layout = QFormLayout()
        ai_layout.setSpacing(10)

        # 服务商选择
        self.provider_combo = QComboBox()
        for pid, p in PROVIDERS.items():
            self.provider_combo.addItem(p['name'], pid)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        ai_layout.addRow('服务商：', self.provider_combo)

        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText('粘贴你的 API Key...')
        ai_layout.addRow('API Key：', self.api_key_input)

        # 获取Key链接
        self.key_link = QLabel()
        self.key_link.setOpenExternalLinks(True)
        self.key_link.setStyleSheet('color: #4a90d9; font-size: 11px;')
        ai_layout.addRow('', self.key_link)

        # Base URL
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText('OpenAI 兼容 API Base URL')
        ai_layout.addRow('Base URL：', self.base_url_input)

        # 模型
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText('留空使用默认模型')
        ai_layout.addRow('模型：', self.model_input)

        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        # ── 桌宠设置 ──
        pet_group = QGroupBox('🐻 桌宠')
        pet_layout = QFormLayout()
        pet_layout.setSpacing(10)

        # 行走速度
        self.speed_combo = QComboBox()
        self.speed_combo.addItem('悠闲漫步', 30)
        self.speed_combo.addItem('正常走动', 50)
        self.speed_combo.addItem('活泼跑动', 80)
        pet_layout.addRow('行走速度：', self.speed_combo)

        pet_group.setLayout(pet_layout)
        layout.addWidget(pet_group)

        # ── 按钮 ──
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton('💾 保存')
        save_btn.setFixedSize(100, 36)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton('取消')
        cancel_btn.setFixedSize(80, 36)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        # ── 关于 ──
        about_label = QLabel(
            'HermesPet-Win v0.1.0 🐻\n'
            '让AI住在你桌面上的小熊伴侣\n'
            '灵感来自 basionwang-bot/HermesPet'
        )
        about_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_label.setStyleSheet('color: #999; font-size: 11px; margin-top: 8px;')
        layout.addWidget(about_label)

        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #faf8f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0dcd5;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
            QLineEdit, QComboBox {
                background-color: #ffffff;
                border: 1px solid #e0dcd5;
                border-radius: 6px;
                padding: 6px 10px;
                min-height: 24px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #c4a882;
            }
            QPushButton {
                background-color: #c4a882;
                color: white;
                border: none;
                border-radius: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b39772;
            }
        """)

    def _on_provider_changed(self, index):
        """服务商切换"""
        pid = self.provider_combo.currentData()
        provider = PROVIDERS.get(pid, {})

        self.base_url_input.setText(provider.get('base_url', ''))
        self.model_input.setPlaceholderText(f"默认: {provider.get('default_model', '')}")

        signup = provider.get('signup_url', '')
        if signup:
            self.key_link.setText(f'<a href="{signup}">🔑 点击获取 API Key</a>')
        else:
            self.key_link.setText('')

        # 自定义时启用URL输入
        self.base_url_input.setEnabled(pid == 'custom')

    def _load_config(self):
        """加载配置"""
        cfg = self.config.load()

        # 服务商
        pid = cfg.get('provider_id', 'deepseek')
        idx = self.provider_combo.findData(pid)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)

        self.api_key_input.setText(cfg.get('api_key', ''))
        self.base_url_input.setText(cfg.get('base_url', PROVIDERS.get(pid, {}).get('base_url', '')))
        self.model_input.setText(cfg.get('model', ''))

        # 速度
        speed = cfg.get('walk_speed', 40)
        for i in range(self.speed_combo.count()):
            if self.speed_combo.itemData(i) == speed:
                self.speed_combo.setCurrentIndex(i)
                break

        self._on_provider_changed(self.provider_combo.currentIndex())

    def _on_save(self):
        """保存配置"""
        pid = self.provider_combo.currentData()
        provider = PROVIDERS.get(pid, {})

        self.config.save({
            'provider_id': pid,
            'api_key': self.api_key_input.text().strip(),
            'base_url': self.base_url_input.text().strip() or provider.get('base_url', ''),
            'model': self.model_input.text().strip(),
            'walk_speed': self.speed_combo.currentData(),
        })

        # 同步到AI引擎
        self.ai_engine.set_provider(pid)
        self.ai_engine.api_key = self.api_key_input.text().strip()
        self.ai_engine.model = self.model_input.text().strip()

        self.accept()
