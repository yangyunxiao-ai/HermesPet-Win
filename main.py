"""
HermesPet-Win 主程序入口
让AI住在你Windows桌面上的小熊伴侣 🐻

启动：python main.py
"""

import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt

from pet.desktop_pet import DesktopPet
from engine.ai_engine import AIEngine
from engine.chat_window import ChatWindow
from engine.settings_window import SettingsWindow
from engine.config_manager import ConfigManager


def _draw_px(painter, x, y, color):
    """画单像素点（PyQt6兼容）"""
    painter.setPen(color)
    painter.drawPoint(x, y)


def create_bear_icon():
    """生成托盘图标（像素小熊16x16）"""
    pm = QPixmap(16, 16)
    pm.fill(QColor(0, 0, 0, 0))
    p = QPainter(pm)
    # 简易像素熊图标
    brown = QColor(139, 90, 43)
    dark = QColor(119, 70, 30)
    belly = QColor(205, 170, 125)
    eye = QColor(30, 30, 30)
    # 头
    for x in range(4, 12):
        for y in range(3, 9):
            _draw_px(p, x, y, brown)
    # 耳朵
    _draw_px(p, 4, 2, dark); _draw_px(p, 5, 2, dark)
    _draw_px(p, 10, 2, dark); _draw_px(p, 11, 2, dark)
    # 肚子
    for x in range(6, 10):
        for y in range(6, 8):
            _draw_px(p, x, y, belly)
    # 眼睛
    _draw_px(p, 5, 5, eye); _draw_px(p, 10, 5, eye)
    # 鼻子
    _draw_px(p, 7, 6, dark); _draw_px(p, 8, 6, dark)
    p.end()
    return QIcon(pm)


class HermesPetApp:
    """HermesPet 主应用"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出

        # 配置
        self.config = ConfigManager()
        cfg = self.config.load()

        # AI引擎
        self.ai_engine = AIEngine(
            provider_id=cfg.get('provider_id', 'deepseek'),
            api_key=cfg.get('api_key', ''),
            model=cfg.get('model', ''),
        )

        # 桌宠
        self.pet = DesktopPet()
        self.pet.double_clicked = False

        # 聊天窗口（延迟创建）
        self.chat_window = None

        # 设置窗口
        self.settings_window = None

        # 系统托盘
        self._setup_tray()

        # 连接信号
        self._connect_signals()

    def _setup_tray(self):
        """设置系统托盘"""
        icon = create_bear_icon()
        self.tray = QSystemTrayIcon(icon, self.app)
        self.tray.setToolTip('🐻 HermesPet 桌面伴侣')

        # 托盘菜单
        menu = QMenu()

        show_chat_action = QAction('💬 打开对话', self.app)
        show_chat_action.triggered.connect(self._show_chat)
        menu.addAction(show_chat_action)

        show_pet_action = QAction('🐻 显示小熊', self.app)
        show_pet_action.triggered.connect(self._show_pet)
        menu.addAction(show_pet_action)

        menu.addSeparator()

        settings_action = QAction('⚙️ 设置', self.app)
        settings_action.triggered.connect(self._show_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        quit_action = QAction('❌ 退出', self.app)
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

        # 首次启动提示
        self.tray.showMessage(
            '🐻 HermesPet',
            '小熊已来到你的桌面！双击小熊开始聊天~',
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def _connect_signals(self):
        """连接双击信号等"""
        # 用定时器检查双击（简单实现）
        self.check_timer = self.app
        # 每次pet被双击时打开聊天
        self.pet.mouseDoubleClickEvent = self._on_pet_double_click

    def _on_pet_double_click(self, event):
        """双击小熊 → 打开聊天"""
        self._show_chat()
        # 让小熊挥手
        from pet.desktop_pet import PetState
        self.pet.state = PetState.WAVE
        self.pet.frame_index = 0

    def _on_tray_activated(self, reason):
        """托盘图标点击"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_chat()

    def _show_chat(self):
        """显示聊天窗口"""
        if self.chat_window is None or not self.chat_window.isVisible():
            self.chat_window = ChatWindow(self.ai_engine)
        self.chat_window.show_and_focus()

    def _show_pet(self):
        """显示小熊"""
        self.pet.show()

    def _show_settings(self):
        """显示设置"""
        if self.settings_window is not None and self.settings_window.isVisible():
            self.settings_window.raise_()
            return
        self.settings_window = SettingsWindow(self.ai_engine, self.config)
        if self.settings_window.exec() == SettingsWindow.DialogCode.Accepted:
            # 保存后刷新聊天窗口模型显示
            if self.chat_window:
                self.chat_window.model_label.setText(self.chat_window._model_text())

    def _quit(self):
        """退出应用"""
        self.tray.hide()
        self.app.quit()

    def run(self):
        """启动应用"""
        return self.app.exec()


def main():
    # 修复Windows终端编码（PyInstaller --windowed 模式下 stdout/stderr 可能为 None）
    if sys.stdout:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.stderr:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    app = HermesPetApp()
    sys.exit(app.run())


if __name__ == '__main__':
    main()
