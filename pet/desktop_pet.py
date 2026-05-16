"""
桌宠核心 —— 像素小熊在桌面漫步、眨眼、看鼠标、冒气泡
"""

import sys
import math
import random
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QImage, QCursor, QScreen

from assets.pet_sprites import generate_all_sprites, REAL_W, REAL_H
from assets.law_tips import get_random_tip


class PetState:
    """桌宠状态机"""
    IDLE = 'idle'
    WALK_LEFT = 'walk_left'
    WALK_RIGHT = 'walk_right'
    LOOK_LEFT = 'look_left'
    LOOK_RIGHT = 'look_right'
    WAVE = 'wave'
    SLEEP = 'sleep'


class DesktopPet(QWidget):
    """桌宠主窗口 —— 透明、无边框、置顶"""

    # 移动速度（像素/秒）- 提速让小熊更活跃
    WALK_SPEED = 55
    # 空闲多久后睡觉（秒）
    SLEEP_IDLE_THRESHOLD = 180
    # 眨眼间隔（秒）
    BLINK_INTERVAL = (3, 6)
    # 每走多少步冒一次气泡
    BUBBLE_STEP_INTERVAL = (3, 8)
    # 气泡显示时长（毫秒）
    BUBBLE_DURATION = 6000

    def __init__(self):
        super().__init__()

        # 生成精灵
        self.sprites = generate_all_sprites()

        # 状态
        self.state = PetState.IDLE
        self.frame_index = 0
        self.facing_right = True

        # 位置（沿屏幕底部菜单栏下方）
        self._init_position()

        # 行走步数计数器（用于触发气泡）
        self.walk_steps = 0
        self.next_bubble_at = random.randint(*self.BUBBLE_STEP_INTERVAL)

        # 当前气泡
        self.current_bubble = None

        # 动画计时器（30fps）
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_anim_tick)
        self.anim_timer.start(33)

        # 行为计时器（决定下一步做什么）- 缩短间隔，更活跃
        self.behavior_timer = QTimer(self)
        self.behavior_timer.timeout.connect(self._on_behavior_tick)
        self._schedule_next_behavior()

        # 眨眼计时器
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self._on_blink)
        self._schedule_blink()

        # 空闲计时
        self.idle_seconds = 0
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self._on_idle_tick)
        self.idle_timer.start(1000)

        # 鼠标追踪
        self.mouse_pos = QCursor.pos()
        self.mouse_hover = False

        # 拖拽
        self._dragging = False
        self._drag_offset = QPointF()

        # 窗口设置
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool  # 不在任务栏显示
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(REAL_W, REAL_H)
        self.setMouseTracking(True)
        self.show()

    def _init_position(self):
        """初始化位置：屏幕底部中间偏上"""
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.x_pos = geo.width() // 2 - REAL_W // 2
            self.y_pos = geo.height() - REAL_H - 60  # 底部留点空间
        else:
            self.x_pos, self.y_pos = 500, 600
        self.move(int(self.x_pos), int(self.y_pos))

    def _schedule_next_behavior(self):
        """安排下一个行为决策 - 更频繁，更活跃"""
        # 缩短间隔：1-3秒（原来2-5秒）
        interval = random.randint(1000, 3000)
        self.behavior_timer.start(interval)

    def _schedule_blink(self):
        """安排下次眨眼"""
        interval = random.randint(*self.BLINK_INTERVAL) * 1000
        self.blink_timer.start(interval)

    # ── 气泡 ─────────────────────────────────────

    def _show_bubble(self):
        """显示一个档案法律知识气泡"""
        # 关闭旧气泡
        self._close_bubble()

        from pet.bubble import BubbleWidget
        tip = get_random_tip()
        pet_pos = (int(self.x_pos), int(self.y_pos))
        bubble = BubbleWidget(tip, pet_pos)
        bubble.show_bubble(self.BUBBLE_DURATION)
        self.current_bubble = bubble

        # 重置步数
        self.walk_steps = 0
        self.next_bubble_at = random.randint(*self.BUBBLE_STEP_INTERVAL)

    def _close_bubble(self):
        """关闭当前气泡"""
        if self.current_bubble is not None:
            try:
                self.current_bubble.close()
            except Exception:
                pass
            self.current_bubble = None

    def _update_bubble_position(self):
        """小熊移动时更新气泡位置"""
        if self.current_bubble is not None:
            try:
                self.current_bubble.update_pet_pos((int(self.x_pos), int(self.y_pos)))
            except Exception:
                pass

    # ── 动画帧 ─────────────────────────────────────

    def _current_frames(self):
        """获取当前状态对应的帧列表"""
        if self.state == PetState.IDLE:
            return self.sprites['idle']
        elif self.state in (PetState.WALK_LEFT, PetState.WALK_RIGHT):
            return self.sprites['walk']
        elif self.state == PetState.LOOK_LEFT:
            return self.sprites['look_left']
        elif self.state == PetState.LOOK_RIGHT:
            return self.sprites['look_right']
        elif self.state == PetState.WAVE:
            return self.sprites['wave']
        elif self.state == PetState.SLEEP:
            return self.sprites['sleep']
        return self.sprites['idle']

    def _on_anim_tick(self):
        """30fps动画帧更新"""
        frames = self._current_frames()
        if len(frames) > 1:
            self.frame_index = (self.frame_index + 1) % len(frames)

        # 行走时移动
        if self.state == PetState.WALK_LEFT:
            self.x_pos -= self.WALK_SPEED * 0.033
            self._clamp_position()
            self.move(int(self.x_pos), int(self.y_pos))
            # 步数+1
            self.walk_steps += 1
            self._check_bubble_trigger()
            self._update_bubble_position()
        elif self.state == PetState.WALK_RIGHT:
            self.x_pos += self.WALK_SPEED * 0.033
            self._clamp_position()
            self.move(int(self.x_pos), int(self.y_pos))
            # 步数+1
            self.walk_steps += 1
            self._check_bubble_trigger()
            self._update_bubble_position()

        self.update()

    def _check_bubble_trigger(self):
        """检查是否该冒气泡了"""
        if self.walk_steps >= self.next_bubble_at:
            self._show_bubble()
            # 冒泡时停一下，站住显示
            self.state = PetState.IDLE
            self.frame_index = 0

    def _clamp_position(self):
        """限制在屏幕内"""
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.x_pos = max(0, min(self.x_pos, geo.width() - REAL_W))

    def _on_behavior_tick(self):
        """行为决策：下一步做什么 - 更爱走动"""
        self.behavior_timer.stop()

        # 如果鼠标悬停，小熊看向鼠标
        if self.mouse_hover:
            mouse_x = self.mouse_pos.x()
            my_x = self.x() + REAL_W // 2
            if mouse_x < my_x - 10:
                self.state = PetState.LOOK_LEFT
            elif mouse_x > my_x + 10:
                self.state = PetState.LOOK_RIGHT
            else:
                self.state = PetState.IDLE
            self._schedule_next_behavior()
            return

        # 随机行为 - 提高行走概率，小熊更活跃
        roll = random.random()
        if roll < 0.15:
            # 站着不动
            self.state = PetState.IDLE
        elif roll < 0.40:
            # 向左走
            self.state = PetState.WALK_LEFT
            self.facing_right = False
        elif roll < 0.65:
            # 向右走
            self.state = PetState.WALK_RIGHT
            self.facing_right = True
        elif roll < 0.80:
            # 挥手
            self.state = PetState.WAVE
        elif roll < 0.90:
            # 左右看
            self.state = random.choice([PetState.LOOK_LEFT, PetState.LOOK_RIGHT])
        else:
            # 快速跑一段（连续走更久）
            self.state = random.choice([PetState.WALK_LEFT, PetState.WALK_RIGHT])
            self.facing_right = (self.state == PetState.WALK_RIGHT)

        self.frame_index = 0
        self.idle_seconds = 0
        self._schedule_next_behavior()

    def _on_blink(self):
        """触发眨眼"""
        self.blink_timer.stop()
        # 只在idle/look状态眨眼
        if self.state in (PetState.IDLE, PetState.LOOK_LEFT, PetState.LOOK_RIGHT):
            self.frame_index = 1  # 闭眼帧
            self.update()
            # 100ms后恢复
            QTimer.singleShot(100, self._open_eyes)
        self._schedule_blink()

    def _open_eyes(self):
        """睁开眼睛"""
        if self.state in (PetState.IDLE, PetState.LOOK_LEFT, PetState.LOOK_RIGHT):
            self.frame_index = 0
            self.update()

    def _on_idle_tick(self):
        """每秒检查空闲"""
        if self.state == PetState.IDLE:
            self.idle_seconds += 1
            if self.idle_seconds >= self.SLEEP_IDLE_THRESHOLD:
                self.state = PetState.SLEEP
                self.frame_index = 0
        else:
            self.idle_seconds = 0

    # ── 绘制 ─────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)  # 像素风

        frames = self._current_frames()
        if frames and self.frame_index < len(frames):
            img = frames[self.frame_index]

            # 如果朝左，水平翻转
            if not self.facing_right and self.state in (PetState.WALK_LEFT, PetState.WALK_RIGHT):
                img = img.mirrored(True, False)

            painter.drawImage(0, 0, img)

        painter.end()

    # ── 鼠标交互 ─────────────────────────────────

    def enterEvent(self, event):
        """鼠标进入 → 小熊看向鼠标"""
        self.mouse_hover = True
        self.mouse_pos = QCursor.pos()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开"""
        self.mouse_hover = False
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动"""
        self.mouse_pos = event.globalPosition().toPoint()

        if self._dragging:
            new_pos = event.globalPosition() - self._drag_offset
            self.x_pos = new_pos.x()
            self.y_pos = new_pos.y()
            self.move(int(self.x_pos), int(self.y_pos))
            self._update_bubble_position()

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_offset = event.position()
            self.state = PetState.WAVE  # 拖起来时挥手
            self.frame_index = 0
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """释放"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.state = PetState.IDLE
            self.frame_index = 0
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """双击 → 打开聊天窗口（由主程序连接信号）"""
        self.double_clicked = True
        super().mouseDoubleClickEvent(event)

    def closeEvent(self, event):
        """关闭时同时关闭气泡"""
        self._close_bubble()
        super().closeEvent(event)
