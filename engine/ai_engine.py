"""
AI 对话引擎 —— 接 OpenAI 兼容 API（DeepSeek/智谱/Kimi/OpenAI）
支持流式输出 + 多服务商预设
"""

import json
import urllib.request
import urllib.error


# 服务商预设（借鉴HermesPet的ProviderPreset设计）
PROVIDERS = {
    'deepseek': {
        'name': 'DeepSeek',
        'base_url': 'https://api.deepseek.com/v1',
        'default_model': 'deepseek-v4-pro',
        'fast_model': 'deepseek-v4-flash',
        'deep_model': 'deepseek-v4-pro',
        'signup_url': 'https://platform.deepseek.com/api_keys',
    },
    'zhipu': {
        'name': '智谱 GLM',
        'base_url': 'https://open.bigmodel.cn/api/paas/v4',
        'default_model': 'glm-5',
        'fast_model': 'glm-5-turbo',
        'deep_model': 'glm-5.1',
        'signup_url': 'https://open.bigmodel.cn/usercenter/apikeys',
    },
    'moonshot': {
        'name': 'Moonshot Kimi',
        'base_url': 'https://api.moonshot.cn/v1',
        'default_model': 'kimi-k2.5',
        'fast_model': 'kimi-k2',
        'deep_model': 'kimi-k2.6',
        'signup_url': 'https://platform.moonshot.cn/console/api-keys',
    },
    'openai': {
        'name': 'OpenAI',
        'base_url': 'https://api.openai.com/v1',
        'default_model': 'gpt-5.4',
        'fast_model': 'gpt-5.4-mini',
        'deep_model': 'gpt-5.5',
        'signup_url': 'https://platform.openai.com/api-keys',
    },
    'custom': {
        'name': '自定义',
        'base_url': '',
        'default_model': '',
        'fast_model': '',
        'deep_model': '',
        'signup_url': '',
    },
}

SYSTEM_PROMPT = """你是 HermesPet 桌面伴侣的小熊助手。你住在用户的桌面上，陪他工作。

特点：
- 温暖可爱，但不过度卖萌
- 回答简洁实用，像一个靠谱的朋友
- 可以用颜文字表达情绪 (ᵔᴥᵔ)
- 擅长：日常问答、技术问题、写作辅助、聊天陪伴
- 用中文回答

当你想让用户做选择时，用编号列表：
1. 选项A
2. 选项B
3. 选项C
"""


class AIEngine:
    """AI对话引擎"""

    def __init__(self, provider_id='deepseek', api_key='', model=''):
        self.provider_id = provider_id
        self.api_key = api_key
        self.model = model
        self.messages = []  # 对话历史

    @property
    def provider(self):
        return PROVIDERS.get(self.provider_id, PROVIDERS['custom'])

    @property
    def base_url(self):
        return self.provider['base_url']

    @property
    def effective_model(self):
        if self.model:
            return self.model
        return self.provider.get('default_model', '')

    def set_provider(self, provider_id: str):
        """切换服务商"""
        self.provider_id = provider_id
        self.model = ''  # 重置模型，用新服务商的默认

    def clear_history(self):
        """清空对话历史"""
        self.messages.clear()

    def chat(self, user_message: str) -> str:
        """发送消息并获取完整回复（非流式）"""
        self.messages.append({'role': 'user', 'content': user_message})

        all_messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
        ] + self.messages

        payload = json.dumps({
            'model': self.effective_model,
            'messages': all_messages,
            'stream': False,
            'max_tokens': 2048,
        }).encode('utf-8')

        url = f"{self.base_url}/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }

        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                reply = data['choices'][0]['message']['content']
                self.messages.append({'role': 'assistant', 'content': reply})
                return reply
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            return f"❌ API错误 {e.code}: {body[:200]}"
        except Exception as e:
            return f"❌ 请求失败: {str(e)[:200]}"

    def chat_stream(self, user_message: str):
        """流式输出（生成器，逐chunk返回文本）"""
        self.messages.append({'role': 'user', 'content': user_message})

        all_messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
        ] + self.messages

        payload = json.dumps({
            'model': self.effective_model,
            'messages': all_messages,
            'stream': True,
            'max_tokens': 2048,
        }).encode('utf-8')

        url = f"{self.base_url}/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }

        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')

        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                full_reply = ''
                buffer = ''
                while True:
                    chunk = resp.read(1024)
                    if not chunk:
                        break
                    buffer += chunk.decode('utf-8', errors='replace')

                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if not line or not line.startswith('data: '):
                            continue
                        data_str = line[6:]  # 去掉 "data: "
                        if data_str == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data.get('choices', [{}])[0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                full_reply += content
                                yield content
                        except json.JSONDecodeError:
                            continue

                if full_reply:
                    self.messages.append({'role': 'assistant', 'content': full_reply})

        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            yield f"❌ API错误 {e.code}: {body[:200]}"
        except Exception as e:
            yield f"❌ 请求失败: {str(e)[:200]}"

    def is_configured(self) -> bool:
        """是否已配置好API"""
        return bool(self.api_key and self.base_url and self.effective_model)
