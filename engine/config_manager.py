"""
配置管理 —— 保存/加载用户设置到本地JSON文件
"""

import json
import os

CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.hermespet-win')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

DEFAULT_CONFIG = {
    'provider_id': 'deepseek',
    'api_key': '',
    'base_url': 'https://api.deepseek.com/v1',
    'model': '',
    'walk_speed': 40,
}


class ConfigManager:
    """配置管理器"""

    def load(self) -> dict:
        """加载配置"""
        if not os.path.exists(CONFIG_FILE):
            return DEFAULT_CONFIG.copy()
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 合并默认值（新增字段不会丢失）
            cfg = DEFAULT_CONFIG.copy()
            cfg.update(data)
            return cfg
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG.copy()

    def save(self, config: dict):
        """保存配置"""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
