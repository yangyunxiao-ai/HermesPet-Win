"""
像素小熊精灵帧生成器 —— 用代码生成所有动画帧，无需外部图片
熊的设计：16x16像素，棕色系，参考HermesPet的Clawd风格
"""

from PyQt6.QtGui import QImage, QColor, QPainter
from PyQt6.QtCore import Qt

# 像素颜色定义
COLORS = {
    'body':       QColor(139, 90, 43),     # 棕色身体
    'body_dark':  QColor(119, 70, 30),     # 深棕色轮廓
    'belly':      QColor(205, 170, 125),   # 浅棕色肚子
    'eye':        QColor(30, 30, 30),      # 黑色眼睛
    'eye_white':  QColor(255, 255, 255),   # 眼白
    'nose':       QColor(60, 30, 20),      # 鼻子
    'blush':      QColor(255, 150, 150),   # 腮红
    'ear_inner':  QColor(205, 140, 100),   # 耳朵内侧
    'transparent': QColor(0, 0, 0, 0),     # 透明
}

SCALE = 4  # 每个逻辑像素放大为4x4实际像素
SPRITE_W = 16
SPRITE_H = 16
REAL_W = SPRITE_W * SCALE
REAL_H = SPRITE_H * SCALE


def _pixel(painter, x, y, color):
    """画一个逻辑像素（放大后）"""
    painter.fillRect(x * SCALE, y * SCALE, SCALE, SCALE, color)


def _create_image():
    return QImage(REAL_W, REAL_H, QImage.Format.Format_ARGB32)


def _draw_body(painter):
    """画身体基础轮廓（所有帧共用）"""
    # 耳朵
    for pos in [(3, 1), (4, 1), (5, 1), (10, 1), (11, 1), (12, 1),
                (3, 2), (4, 2), (5, 2), (10, 2), (11, 2), (12, 2)]:
        _pixel(painter, *pos, COLORS['body_dark'])
    for pos in [(4, 2), (5, 2), (10, 2), (11, 2)]:
        _pixel(painter, *pos, COLORS['ear_inner'])

    # 头部
    for y in range(3, 8):
        for x in range(3, 13):
            _pixel(painter, x, y, COLORS['body'])

    # 肚子
    for y in range(8, 12):
        for x in range(5, 11):
            _pixel(painter, x, y, COLORS['body'])
    for y in range(9, 11):
        for x in range(6, 10):
            _pixel(painter, x, y, COLORS['belly'])

    # 脚
    for pos in [(5, 12), (6, 12), (9, 12), (10, 12)]:
        _pixel(painter, *pos, COLORS['body_dark'])


def _draw_face(painter, eye_state='open', look='center'):
    """画面部表情"""
    # 鼻子
    _pixel(painter, 7, 5, COLORS['nose'])
    _pixel(painter, 8, 5, COLORS['nose'])

    # 嘴巴
    _pixel(painter, 7, 6, COLORS['body_dark'])
    _pixel(painter, 8, 6, COLORS['body_dark'])

    # 眼睛
    if eye_state == 'open':
        if look == 'center':
            _pixel(painter, 5, 4, COLORS['eye_white'])
            _pixel(painter, 6, 4, COLORS['eye'])
            _pixel(painter, 9, 4, COLORS['eye'])
            _pixel(painter, 10, 4, COLORS['eye_white'])
        elif look == 'left':
            _pixel(painter, 4, 4, COLORS['eye_white'])
            _pixel(painter, 5, 4, COLORS['eye'])
            _pixel(painter, 8, 4, COLORS['eye'])
            _pixel(painter, 9, 4, COLORS['eye_white'])
        elif look == 'right':
            _pixel(painter, 6, 4, COLORS['eye'])
            _pixel(painter, 7, 4, COLORS['eye_white'])
            _pixel(painter, 10, 4, COLORS['eye_white'])
            _pixel(painter, 11, 4, COLORS['eye'])
    elif eye_state == 'closed':
        _pixel(painter, 5, 4, COLORS['body_dark'])
        _pixel(painter, 6, 4, COLORS['body_dark'])
        _pixel(painter, 9, 4, COLORS['body_dark'])
        _pixel(painter, 10, 4, COLORS['body_dark'])

    # 腮红
    _pixel(painter, 4, 5, COLORS['blush'])
    _pixel(painter, 11, 5, COLORS['blush'])


def generate_idle_frames():
    """生成待机动画帧（微微呼吸）"""
    frames = []

    # 帧1：正常
    img = _create_image()
    p = QPainter(img)
    p.fillRect(0, 0, REAL_W, REAL_H, COLORS['transparent'])
    _draw_body(p)
    _draw_face(p, 'open', 'center')
    p.end()
    frames.append(img)

    # 帧2：眨眼
    img = _create_image()
    p = QPainter(img)
    p.fillRect(0, 0, REAL_W, REAL_H, COLORS['transparent'])
    _draw_body(p)
    _draw_face(p, 'closed', 'center')
    p.end()
    frames.append(img)

    # 帧3：睁眼（同帧1）
    frames.append(frames[0].copy())

    return frames


def generate_walk_frames():
    """生成行走动画帧（左右脚交替）"""
    frames = []

    # 帧1：左脚前
    img = _create_image()
    p = QPainter(img)
    p.fillRect(0, 0, REAL_W, REAL_H, COLORS['transparent'])
    _draw_body(p)
    _draw_face(p, 'open', 'center')
    # 左脚前移
    p.fillRect(5 * SCALE, 12 * SCALE, SCALE, SCALE, COLORS['transparent'])
    _pixel(p, 4, 12, COLORS['body_dark'])
    p.end()
    frames.append(img)

    # 帧2：右脚前
    img = _create_image()
    p = QPainter(img)
    p.fillRect(0, 0, REAL_W, REAL_H, COLORS['transparent'])
    _draw_body(p)
    _draw_face(p, 'open', 'center')
    # 右脚前移
    p.fillRect(10 * SCALE, 12 * SCALE, SCALE, SCALE, COLORS['transparent'])
    _pixel(p, 11, 12, COLORS['body_dark'])
    p.end()
    frames.append(img)

    return frames


def generate_look_left_frames():
    """生成向左看帧"""
    img = _create_image()
    p = QPainter(img)
    p.fillRect(0, 0, REAL_W, REAL_H, COLORS['transparent'])
    _draw_body(p)
    _draw_face(p, 'open', 'left')
    p.end()
    return [img]


def generate_look_right_frames():
    """生成向右看帧"""
    img = _create_image()
    p = QPainter(img)
    p.fillRect(0, 0, REAL_W, REAL_H, COLORS['transparent'])
    _draw_body(p)
    _draw_face(p, 'open', 'right')
    p.end()
    return [img]


def generate_wave_frames():
    """生成挥手动画帧"""
    frames = []

    # 帧1：正常站立
    img = _create_image()
    p = QPainter(img)
    p.fillRect(0, 0, REAL_W, REAL_H, COLORS['transparent'])
    _draw_body(p)
    _draw_face(p, 'open', 'center')
    p.end()
    frames.append(img)

    # 帧2：右手举起
    img = _create_image()
    p = QPainter(img)
    p.fillRect(0, 0, REAL_W, REAL_H, COLORS['transparent'])
    _draw_body(p)
    _draw_face(p, 'open', 'center')
    # 右手举起来
    _pixel(p, 12, 3, COLORS['body'])
    _pixel(p, 13, 2, COLORS['body'])
    p.end()
    frames.append(img)

    # 帧3：挥手
    img = _create_image()
    p = QPainter(img)
    p.fillRect(0, 0, REAL_W, REAL_H, COLORS['transparent'])
    _draw_body(p)
    _draw_face(p, 'open', 'center')
    _pixel(p, 13, 1, COLORS['body'])
    _pixel(p, 12, 2, COLORS['body'])
    p.end()
    frames.append(img)

    # 帧4：同帧2
    frames.append(frames[1].copy())

    return frames


def generate_sleep_frames():
    """生成睡觉动画帧"""
    frames = []

    # 帧1：闭眼
    img = _create_image()
    p = QPainter(img)
    p.fillRect(0, 0, REAL_W, REAL_H, COLORS['transparent'])
    _draw_body(p)
    _draw_face(p, 'closed', 'center')
    # Zzz
    _pixel(p, 13, 2, QColor(100, 150, 255))
    _pixel(p, 14, 1, QColor(100, 150, 255))
    _pixel(p, 15, 0, QColor(100, 150, 255))
    p.end()
    frames.append(img)

    # 帧2：Zzz变大
    img = _create_image()
    p = QPainter(img)
    p.fillRect(0, 0, REAL_W, REAL_H, COLORS['transparent'])
    _draw_body(p)
    _draw_face(p, 'closed', 'center')
    _pixel(p, 14, 1, QColor(100, 150, 255))
    _pixel(p, 15, 0, QColor(100, 150, 255))
    p.end()
    frames.append(img)

    return frames


def generate_all_sprites():
    """生成所有精灵帧"""
    return {
        'idle': generate_idle_frames(),
        'walk': generate_walk_frames(),
        'look_left': generate_look_left_frames(),
        'look_right': generate_look_right_frames(),
        'wave': generate_wave_frames(),
        'sleep': generate_sleep_frames(),
    }


if __name__ == '__main__':
    # 测试：保存所有帧为PNG
    import os
    sprites = generate_all_sprites()
    for anim_name, frames in sprites.items():
        os.makedirs(f'sprites_{anim_name}', exist_ok=True)
        for i, frame in enumerate(frames):
            frame.save(f'sprites_{anim_name}/frame_{i:02d}.png')
    print(f"✅ 已生成 {sum(len(f) for f in sprites.values())} 帧")
