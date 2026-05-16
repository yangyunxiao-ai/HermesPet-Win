"""
聊天窗口 —— 右键/双击小熊弹出，支持流式输出
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QColor

from engine.ai_engine import AIEngine


class StreamWorker(QThread):
    """流式输出工作线程"""
    chunk_received = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, engine: AIEngine, message: str):
        super().__init__()
        self.engine = engine
        self.message = message

    def run(self):
        for chunk in self.engine.chat_stream(self.message):
            self.chunk_received.emit(chunk)
        self.finished.emit()


class ChatWindow(QWidget):
    """聊天窗口"""

    def __init__(self, ai_engine: AIEngine):
        super().__init__()
        self.ai_engine = ai_engine
        self.stream_worker = None

        self.setWindowTitle('🐻 小熊对话')
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Dialog
        )
        self.setMinimumSize(420, 520)
        self.resize(460, 560)

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 标题栏
        title_bar = QHBoxLayout()
        self.title_label = QLabel('🐻 小熊对话')
        self.title_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        title_bar.addWidget(self.title_label)
        title_bar.addStretch()

        # 模型指示
        self.model_label = QLabel(self._model_text())
        self.model_label.setStyleSheet('color: #888; font-size: 11px;')
        title_bar.addWidget(self.model_label)
        layout.addLayout(title_bar)

        # 聊天区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont('Microsoft YaHei', 10))
        self.chat_display.setPlaceholderText('双击小熊开始聊天~ (ᵔᴥᵔ)')
        layout.addWidget(self.chat_display, 1)

        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('输入消息，按 Enter 发送...')
        self.input_field.setFont(QFont('Microsoft YaHei', 10))
        self.input_field.returnPressed.connect(self._on_send)
        input_layout.addWidget(self.input_field, 1)

        self.send_btn = QPushButton('发送')
        self.send_btn.setFixedSize(70, 36)
        self.send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)

        # 欢迎消息
        if not self.ai_engine.is_configured():
            self._append_system_msg(
                '⚠️ 还没配置AI后端，请右键系统托盘图标 → 设置，配置API Key'
            )
        else:
            self._append_bear_msg('嗨！我是你的桌面小熊 (ᵔᴥᵔ) 有什么可以帮你的？')

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #faf8f5;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #e0dcd5;
                border-radius: 8px;
                padding: 8px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #e0dcd5;
                border-radius: 18px;
                padding: 8px 16px;
            }
            QLineEdit:focus {
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
            QPushButton:pressed {
                background-color: #a38662;
            }
            QPushButton:disabled {
                background-color: #d5d0c8;
            }
        """)

    def _model_text(self):
        if self.ai_engine.is_configured():
            return f"🤖 {self.ai_engine.provider['name']} / {self.ai_engine.effective_model}"
        return '⚠️ 未配置'

    def _append_bear_msg(self, text):
        """添加小熊消息"""
        self.chat_display.append(
            f'<div style="margin: 6px 0;"><span style="color: #b39772; font-weight: bold;">🐻 小熊：</span>'
            f'<span style="color: #333;">{text}</span></div>'
        )
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)

    def _append_user_msg(self, text):
        """添加用户消息"""
        self.chat_display.append(
            f'<div style="margin: 6px 0; text-align: right;">'
            f'<span style="color: #555;">{text}</span> '
            f'<span style="color: #4a90d9; font-weight: bold;">:你</span></div>'
        )
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)

    def _append_system_msg(self, text):
        """添加系统消息"""
        self.chat_display.append(
            f'<div style="margin: 6px 0; text-align: center; color: #999; font-size: 12px;">{text}</div>'
        )
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)

    def _on_send(self):
        """发送消息"""
        text = self.input_field.text().strip()
        if not text:
            return

        if not self.ai_engine.is_configured():
            self._append_system_msg('⚠️ 请先配置API Key（右键托盘图标 → 设置）')
            return

        if self.stream_worker and self.stream_worker.isRunning():
            return  # 正在回复中

        # 显示用户消息
        self._append_user_msg(text)
        self.input_field.clear()

        # 开始流式输出
        self._append_bear_msg('')  # 占位
        self.send_btn.setEnabled(False)
        self.input_field.setEnabled(False)

        self.stream_worker = StreamWorker(self.ai_engine, text)
        self.stream_worker.chunk_received.connect(self._on_chunk)
        self.stream_worker.finished.connect(self._on_stream_finished)
        self.stream_worker.start()

    def _on_chunk(self, chunk):
        """收到流式chunk"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(chunk)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def _on_stream_finished(self):
        """流式输出完成"""
        self.chat_display.append('')  # 换行
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

    def show_and_focus(self):
        """显示并聚焦"""
        self.show()
        self.raise_()
        self.activateWindow()
        self.input_field.setFocus()
