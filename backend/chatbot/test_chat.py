import asyncio
import os
import sys
from dotenv import load_dotenv

# 首先加载环境变量
load_dotenv()

# 设置代理和网络环境
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

# 设置详细日志记录
import logging
logging.basicConfig(level=logging.INFO)

# 获取项目根目录，并将其添加到 Python 路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from chatbot.agents.chat_agent import ForexChatAgent
from chatbot.agents.tools.deep_search import DeepSearchAssistant

async def test_chat():
    # 初始化聊天代理
    print("正在初始化聊天代理...")
    agent = ForexChatAgent()
    print("聊天代理初始化完成")
    
    # 只测试基本和DeepSearch功能
    basic_test_messages = [
        "请问今天的美元兑人民币的交易风险如何？"
    ]
    
    # # DeepSearch测试消息 - 使用更具体、与外汇相关的查询
    # deep_search_messages = [
    #     "中国经济增长对人民币汇率的影响趋势"
    # ]
    
    # 测试基本对话功能
    print("\n" + "="*50)
    print("测试基本对话功能")
    print("="*50)
    for message in basic_test_messages:
        await run_test(agent, message)
    
    # # 测试DeepSearch功能
    # print("\n" + "="*50)
    # print("测试DeepSearch功能")
    # print("="*50)
    for message in basic_test_messages:
        print("\n" + "-"*30)
        print(f"测试消息 (不启用DeepSearch): {message}")
        print("-"*30)
        await run_test(agent, message, use_deep_search=False)
        
        # print("\n" + "-"*30)
        # print(f"测试消息 (启用DeepSearch): {message}")
        # print("-"*30)
        # await run_test(agent, message, use_deep_search=True)
        
async def test_direct_deepsearch():
    """直接测试DeepSearch功能，不通过聊天代理"""
    print("\n" + "="*50)
    print("直接测试DeepSearch联网功能")
    print("="*50)
    
    deepsearch = DeepSearchAssistant()
    
    # 测试查询
    test_queries = [
        "美欧贸易关系对美元汇率的影响"
    ]
    
    for query in test_queries:
        print("\n" + "-"*30)
        print(f"测试查询: {query}")
        print("-"*30)
        
        try:
            # 测试快速搜索
            print("执行快速搜索 (仅研究计划)...")
            plan = await deepsearch.quick_search(query)
            print("\n研究计划结果:")
            print(plan[:500] + "..." if len(plan) > 500 else plan)
            
            # 测试完整搜索
            print("\n执行完整搜索 (完整报告)...")
            report = await deepsearch.search(query)
            print("\n完整报告摘要:")
            print(report[:500] + "..." if len(report) > 500 else report)
        except Exception as e:
            print(f"\n错误: {str(e)}")
        
        print("-"*30)

async def run_test(agent, message, use_deep_search=False):
    """运行单个测试用例"""
    if not use_deep_search:
        print("\n普通模式测试:")
    else:
        print("\nDeepSearch模式测试:")
    
    try:
        print(f"发送消息: {message}")
        print("等待回复...")
        response = await agent.chat(message, use_deep_search=use_deep_search)
        print("\n回复:")
        print(response[:500] + "..." if len(response) > 500 else response)
        
        # 简单的响应验证
        if not response or response.strip() == "":
            print("\n警告: 响应为空")
        elif "错误" in response or "抱歉" in response:
            print("\n警告: 响应包含错误信息")
            
        # DeepSearch检查
        if use_deep_search and "深度搜索" not in response and "【深度搜索】" not in response:
            print("\n警告: 启用DeepSearch但响应中未包含深度搜索结果")
            
    except Exception as e:
        print(f"\n错误: {str(e)}")
    
    print("-"*30)

if __name__ == "__main__":
    print("测试开始...")
    
    # 确认API密钥已设置
    dashscope_key = os.getenv("DASHSCOPE_API_KEY_2")
    if not dashscope_key:
        print("错误: 未设置 DASHSCOPE_API_KEY_2 环境变量")
        exit(1)
    else:
        print(f"DASHSCOPE_API_KEY_2已设置: {dashscope_key[:5]}...{dashscope_key[-5:]}")
    
    # 选择要运行的测试
    test_type = input("选择测试类型 (1=聊天代理, 2=直接DeepSearch, 3=两者都测试): ")
    
    if test_type == "1":
        # 运行聊天代理测试
        asyncio.run(test_chat())
    elif test_type == "2":
        # 直接测试DeepSearch
        asyncio.run(test_direct_deepsearch())
    else:
        # 两种测试都运行
        asyncio.run(test_chat())
        asyncio.run(test_direct_deepsearch()) 