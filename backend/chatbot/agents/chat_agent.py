import os
import logging

from .base import BaseAgent
from .prompts.system_prompts import FOREX_AGENT_PROMPT
from .tools.forex_tools import forex_tools, get_forex_history, get_forex_price, fetch_forex_news_from_exa
from .tools.deep_search import DeepSearchAssistant
from ..data.docstore import ForexKnowledgeBase

# 获取logger实例
logger = logging.getLogger("django")

# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 获取backend/chatbot目录的路径
CHATBOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))


class ForexChatAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.conversation_history = []
        self.tools = forex_tools
        self.knowledge_base = ForexKnowledgeBase()
        self.deep_search = DeepSearchAssistant()
        
        # 构建文档目录的路径 (指向 backend/chatbot/data/forex_docs)
        docs_path = os.path.join(os.path.dirname(CURRENT_DIR), "data", "forex_docs")
        # 确保目录存在
        os.makedirs(docs_path, exist_ok=True)
        # 初始化时加载文档
        self.knowledge_base.load_documents(docs_path)

    def get_system_prompt(self):
        # 将工具信息添加到系统提示中
        tools_description = """
        可用工具：
        1. GetForexPrice - 获取货币对的实时价格, 使用方法:GetForexPrice(pair)，例如 GetForexPrice("AUDUSD")
        2. GetForexHistory - 获取货币对的历史数据, 使用方法:GetForexHistory(pair)，例如 GetForexHistory("AUDUSD")
        3. DeepSearch - 生成深入的市场研究报告, 使用方法:DeepSearch(query)，例如 DeepSearch("请分析最近USD/CNY的交易风险")
        4. GetForexNews - 获取货币对的最新新闻, 使用方法:GetForexNews(query)，例如 GetForexNews("请分析最近USD/CNY的交易风险")
        """
        prompt = FOREX_AGENT_PROMPT + "\n" + tools_description
        return {"role": "system", "content": prompt}

    def get_tools(self):
        return self.tools

    async def chat(self, message: str, use_deep_search: bool = False) -> str:
        # 添加消息到历史记录
        self.conversation_history.append({"role": "user", "content": message})
        try:
            # 如果启用了深度搜索，则使用DeepSearch
            if use_deep_search:
                logger.info(f"使用DeepSearch进行查询: {message}")
                try:
                    # 使用完整搜索模式，生成研究报告
                    deep_search_result = await self.deep_search.search(message)
                    logger.info("DeepSearch查询完成")
                    
                    # 构建包含DeepSearch结果的上下文
                    context = f"深度搜索结果:\n{deep_search_result}\n\n"
                    
                    # 添加系统提示
                    system_prompt = self.get_system_prompt()
                    system_prompt["content"] += f"\n\n{context}"
                    
                    # 指示模型先提供分析建议，再附上完整报告
                    user_message = f"{message}\n\n请先基于深度搜索报告提供简洁的分析和建议（不超过500字），然后在回复的末尾用'---完整研究报告---'作为分隔符，附上较完整的研究报告原文。确保报告格式完整，保留完整章节、内容、参考资料，适当减少同质化的案例。"
                    
                    # 构建消息
                    messages = [system_prompt, {"role": "user", "content": user_message}]
                    return await self.generate_response(messages)
                except Exception as e:
                    logger.error(f"DeepSearch执行失败: {str(e)}", exc_info=True)
                    # 如果DeepSearch失败，告知用户并回退到普通搜索
                    error_message = f"【深度搜索】功能执行失败: {str(e)}\n\n我将使用常规方式回答您的问题。\n\n"
                    regular_response = await self._regular_chat(message)
                    return error_message + regular_response
            else:
                # 使用普通搜索
                return await self._regular_chat(message)
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return f"抱歉，处理请求时出现错误：{str(e)}"
            
            
    async def _regular_chat(self, message: str) -> str:
        """使用常规方式处理聊天请求"""
        try:
            # 获取并存储新闻，但不直接使用返回值
            await fetch_forex_news_from_exa(message)
            
            # 重新加载文档以确保包含最新新闻
            docs_path = os.path.join(os.path.dirname(CURRENT_DIR), "data", "forex_docs")
            self.knowledge_base.load_documents(docs_path)
            
            # 检索相关文档（包括新闻）
            relevant_docs = self.knowledge_base.similarity_search(message)
            
            # 构建上下文，只用检索到的文档
            context = '\n'.join(relevant_docs)
            
            currency_pair = self._extract_currency_pair(message)
            if currency_pair:
                try:
                    price_data = get_forex_price(currency_pair)
                    if "error" in price_data:
                        logger.warning(f"获取价格数据失败: {price_data['error']}")
                        return f"抱歉，获取 {currency_pair} 的价格数据时出现问题，但我仍可以回答其他相关问题。"
                    
                    history_data = get_forex_history(currency_pair)
                    if "error" in history_data:
                        logger.warning(f"获取历史数据失败: {history_data['error']}")
                        return f"抱歉，获取 {currency_pair} 的历史数据时出现问题，但我仍可以回答其他相关问题。"

                    # 构建隐藏的市场数据上下文
                    market_context = {
                        "current_price": price_data.get("price"),
                        "daily_change": price_data.get("change"),
                        "change_percent": price_data.get("change_percent"),
                        "previous_close": price_data.get("previous_close"),
                        "month_high": history_data.get("highest"),
                        "month_low": history_data.get("lowest"),
                        "month_avg": history_data.get("average"),
                    }

                    # 将数据添加到系统提示中
                    system_prompt = self.get_system_prompt()
                    # 添加检索到的文档、新闻和市场数据到系统提示中
                    system_prompt["content"] += f"\n\n相关知识和新闻：\n{context}\n\n当前分析所需数据：{market_context}"
                    messages = [system_prompt, {"role": "user", "content": message}]
                except Exception as e:
                    logger.error(f"获取数据时出错：{str(e)}")
                    messages = [
                        self.get_system_prompt(),
                        {"role": "user", "content": message},
                    ]
            else:
                system_prompt = self.get_system_prompt()
                # 仅添加检索到的文档到系统提示中
                system_prompt["content"] += f"\n\n相关知识：\n{context}"
                messages = [system_prompt, {"role": "user", "content": message}]

            return await self.generate_response(messages)
        except Exception as e:
            logger.error(f"Regular chat error: {str(e)}")
            return f"抱歉，处理请求时出现错误：{str(e)}"

    def _extract_currency_pair(self, message: str) -> str:
        # 扩展货币对列表
        pairs = [
            "AUD/USD",
            "EUR/USD",
            "GBP/USD",
            "USD/JPY",
            "USD/CHF",
            "CNY/USD",
            "CNY/EUR",
            "CNY/GBP",
            "CNY/SGD",
            "HKD/GBP",
        ]
        for pair in pairs:
            if pair in message:
                return pair.replace("/", "")
        return None
