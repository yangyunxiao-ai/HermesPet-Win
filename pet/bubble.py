"""
气泡弹窗 —— 小熊头顶冒出档案法律知识气泡
"""

from PyQt6.QtWidgets import QWidget, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont


class BubbleWidget(QWidget):
    """气泡弹窗：圆角矩形+小三角指向小熊"""

    def __init__(self, text: str, parent_pet_pos: tuple, parent=None):
        super().__init__(parent)
        self.text = text
        self.parent_pet_pos = parent_pet_pos  # (x, y) 小熊位置

        # 窗口设置
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # 计算尺寸
        self._calc_size()

        # 定位到小熊头顶
        self._position_above_pet()

        # 透明度动画
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

        # 淡入
        self.fade_in = QPropertyAnimation(self.opacity_effect, b'opacity')
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # 淡出
        self.fade_out = QPropertyAnimation(self.opacity_effect, b'opacity')
        self.fade_out.setDuration(400)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.fade_out.finished.connect(self.close)

        # 显示后自动定时关闭
        self.show_timer = QTimer(self)
        self.show_timer.setSingleShot(True)
        self.show_timer.timeout.connect(self._start_fade_out)

        # 上下浮动动画
        self.float_offset = 0
        self.float_timer = QTimer(self)
        self.float_timer.timeout.connect(self._float_tick)
        self.float_tick_count = 0

    def _calc_size(self):
        """根据文字内容计算气泡大小"""
        # 估算文字宽高
        label = QLabel(self.text)
        label.setWordWrap(True)
        label.setFont(QFont('Microsoft YaHei', 9))
        label.setFixedWidth(260)
        label.adjustSize()
        text_h = label.height()

        self.bubble_w = 280
        self.bubble_h = text_h + 30  # 上下padding
        self.setFixedSize(self.bubble_w, self.bubble_h + 16)  # +16 for arrow

    def _position_above_pet(self):
        """定位到小熊头顶"""
        px, py = self.parent_pet_pos
        bx = px - self.bubble_w // 2 + 32  # 小熊中心偏移
        by = py - self.bubble_h - 20  # 小熊头顶上方
        # 确保不超出屏幕
        bx = max(10, min(bx, 2800 - self.bubble_w - 10))
        by = max(10, by)
        self.move(int(bx), int(by))

    def _float_tick(self):
        """轻微上下浮动"""
        self.float_tick_count += 1
        import math
        self.float_offset = int(3 * math.sin(self.float_tick_count * 0.15))
        self._position_above_pet_with_offset()

    def _position_above_pet_with_offset(self):
        """带浮动偏移的重定位"""
        px, py = self.parent_pet_pos
        bx = px - self.bubble_w // 2 + 32
        by = py - self.bubble_h - 20 + self.float_offset
        bx = max(10, min(bx, 2800 - self.bubble_w - 10))
        by = max(10, by)
        self.move(int(bx), int(by))

    def show_bubble(self, duration_ms=5000):
        """显示气泡，duration_ms后自动消失"""
        self.show()
        self.fade_in.start()
        self.show_timer.start(duration_ms)
        self.float_timer.start(50)

    def _start_fade_out(self):
        """开始淡出"""
        self.float_timer.stop()
        self.fade_out.start()

    def update_pet_pos(self, pos: tuple):
        """小熊移动时更新气泡位置"""
        self.parent_pet_pos = pos
        self._position_above_pet_with_offset()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 气泡圆角矩形
        bubble_rect = self.rect().adjusted(0, 0, 0, -16)  # 底部留三角空间
        radius = 12

        # 阴影
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.drawRoundedRect(bubble_rect.adjusted(2, 2, 2, 2), radius, radius)

        # 背景
        painter.setBrush(QColor(255, 253, 248))  # 暖白色
        painter.setPen(QPen(QColor(200, 168, 130), 1.5))  # 棕色边框
        painter.drawRoundedRect(bubble_rect, radius, radius)

        # 小三角（指向下方小熊）
        center_x = self.bubble_w // 2
        tri_y = bubble_rect.height()
        path = QPainterPath()
        path.moveTo(center_x - 8, tri_y)
        path.lineTo(center_x, tri_y + 12)
        path.lineTo(center_x + 8, tri_y)
        painter.setBrush(QColor(255, 253, 248))
        painter.setPen(QPen(QColor(200, 168, 130), 1.5))
        painter.drawPath(path)

        # 顶部小装饰线
        painter.setPen(QPen(QColor(196, 168, 130), 3))
        painter.drawLine(10, 3, self.bubble_w - 10, 3)

        # 文字
        painter.setPen(QColor(80, 60, 40))
        painter.setFont(QFont('Microsoft YaHei', 9))
        text_rect = bubble_rect.adjusted(14, 14, -14, -10)
        painter.drawText(text_rect, Qt.TextFlag.TextWordWrap, self.text)

        painter.end()
