# 🐻 HermesPet-Win

让 AI 住在你 Windows 桌面上的小熊伴侣

灵感来自 [basionwang-bot/HermesPet](https://github.com/basionwang-bot/HermesPet)（macOS），这是 Windows 版本。

## ✨ 功能

- 🐻 **像素小熊桌宠** — 在桌面闲逛、眨眼、看鼠标、挥手
- 💬 **AI 对话** — 双击小熊弹出聊天窗口，支持流式输出
- 🤖 **多服务商** — DeepSeek / 智谱 GLM / Kimi / OpenAI / 自定义
- 📍 **系统托盘** — 常驻托盘，右键菜单
- ⚙️ **设置面板** — 傻瓜化配置，一键获取 API Key
- 📜 **档案法律知识库** — 小熊漫步时自动弹出81条档案法规知识气泡

## 🚀 快速开始

### 安装依赖

```bash
pip install PyQt6
```

### 启动

```bash
python main.py
```

### 配置 AI

1. 右键系统托盘图标 → 设置
2. 选择服务商（如 DeepSeek）
3. 点击"获取 API Key"链接
4. 粘贴 Key → 保存
5. 双击小熊开始聊天！

## 🎮 交互

| 操作 | 效果 |
|------|------|
| **双击小熊** | 打开聊天窗口 |
| **拖拽小熊** | 移动位置（小熊会挥手） |
| **鼠标靠近** | 小熊看向鼠标 |
| **右键托盘** | 菜单（聊天/设置/退出） |
| **Enter** | 发送消息 |

## 📜 档案法律知识库（81条）

小熊每走几步就会冒出一条档案法律知识气泡，覆盖：

| 分类 | 条数 | 说明 |
|------|------|------|
| 📜 档案法 | 8 | 核心条文 |
| 📋 档案管理 | 6 | 保管期限、库房温湿度、数字化标准 |
| ⚖️ 保密法 | 3 | 涉密档案管理 |
| 🏛️ 档案馆 | 3 | 机构职责 |
| 💡 实用知识 | 6 | 全宗、编研、编目 |
| 🔐 安全提醒 | 3 | 八防、借阅规定 |
| 🎓 高校档案 | 6 | 教育部令第27号 |
| 📚 归档范围 | 5 | 11大类 |
| 🎯 利用开放 | 5 | 数字档案馆、隐私保护 |
| 📊 条件保障 | 5 | 库房、经费、信息化 |
| 🏫 高校特点 | 4 | 学籍、科研知识产权 |
| 🏅 领导人指示 | 22 | 毛泽东/周恩来/邓小平/江泽民/胡锦涛/习近平档案工作指示批示 |
| 📖 名言 | 5 | 档案工作者使命 |

## 📦 打包为 .exe

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "HermesPet" \
  --add-data "assets;assets" --add-data "pet;pet" --add-data "engine;engine" \
  main.py
```

生成 `dist/HermesPet.exe`，约 35MB，双击即用，无需 Python 环境。

## 📁 项目结构

```
HermesPet-Win/
├── main.py                  # 启动入口
├── assets/
│   ├── pet_sprites.py       # 像素小熊帧生成器
│   └── law_tips.py          # 档案法律知识库（81条）
├── pet/
│   ├── desktop_pet.py       # 桌宠核心（状态机+动画+交互）
│   └── bubble.py            # 气泡弹窗
├── engine/
│   ├── ai_engine.py         # AI对话引擎（OpenAI兼容API）
│   ├── chat_window.py       # 聊天窗口（流式输出）
│   ├── settings_window.py   # 设置面板
│   └── config_manager.py    # 配置持久化
└── README.md
```

## 🔧 技术栈

- **Python 3.12+**
- **PyQt6** — UI框架
- **OpenAI 兼容 API** — AI后端
- **零外部图片** — 所有精灵帧代码生成

## 📝 版本

- **v0.4.0** (2026-05-17) — 替换为22条完整领导人指示批示（毛/周/邓/江/胡/习），知识库81条
- **v0.3.0** (2026-05-17) — 新增10条领导人档案工作指示批示（习近平），知识库扩充至69条
- **v0.2.0** (2026-05-17) — 新增59条档案法律知识库（含高校档案），PyInstaller打包
- **v0.1.0** (2026-05-16) — MVP：桌宠漫步 + AI对话 + 多服务商

## 🙏 致谢

- [HermesPet](https://github.com/basionwang-bot/HermesPet) — macOS 原版，核心架构灵感来源
