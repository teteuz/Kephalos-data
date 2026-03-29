"""
LLM客户端封装
统一使用OpenAI格式调用
"""

import json
import re
from typing import Optional, Dict, Any, List
from openai import OpenAI

from ..config import Config

# Modelos do OpenRouter que suportam response_format json_object
JSON_MODE_SUPPORTED_MODELS = [
    "openai/", "anthropic/", "google/gemini", "mistralai/mistral-large",
    "mistralai/mixtral", "qwen/qwen", "deepseek/deepseek-chat"
]

def supports_json_mode(model: str) -> bool:
    """Verifica se o modelo suporta response_format json_object"""
    for prefix in JSON_MODE_SUPPORTED_MODELS:
        if prefix in model:
            return True
    return False


class LLMClient:
    """LLM客户端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Só adiciona response_format se o modelo suportar
        if response_format and supports_json_mode(self.model):
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        # Injeta instrução JSON no prompt quando modelo não suporta json_object
        if not supports_json_mode(self.model):
            messages = messages.copy()
            last_msg = messages[-1]
            messages[-1] = {
                "role": last_msg["role"],
                "content": last_msg["content"] + "\n\nIMPORTANT: Respond ONLY with valid JSON. No explanation, no markdown, no code blocks."
            }

        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )

        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(f"LLM返回的JSON格式无效: {cleaned_response}")