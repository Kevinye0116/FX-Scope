import os
from typing import Dict, List

from dotenv import load_dotenv
from langchain.schema import SystemMessage
from openai import OpenAI

load_dotenv()

## 基础Agent类
class BaseAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = "qwen-plus"

    def get_system_prompt(self) -> SystemMessage:
        raise NotImplementedError

    def get_tools(self) -> List[Dict]:
        raise NotImplementedError

    async def generate_response(self, messages: List[Dict]) -> str:
        """Generate response using Qwen model"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error generating response: {e}")
            return "抱歉,生成回复时出现错误。请稍后再试。"
        