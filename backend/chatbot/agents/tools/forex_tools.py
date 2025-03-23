from typing import Dict
import os
import yfinance as yf
from langchain.tools import Tool
from exa_py import Exa
from dotenv import load_dotenv
from openai import OpenAI
import json
import re
from asyncio import run
import asyncio
from datetime import datetime

load_dotenv()

# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 获取agents目录
AGENTS_DIR = os.path.dirname(CURRENT_DIR)
# 获取chatbot目录
CHATBOT_DIR = os.path.dirname(AGENTS_DIR)

ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

def get_forex_price(pair: str) -> Dict:
    """获取货币对的实时价格"""
    if not isinstance(pair, str) or len(pair) != 6:
        return {"error": "无效的货币对格式"}
    
    try:
        ticker = yf.Ticker(f"{pair}=X")
        info = ticker.info
        return {
            "price": info.get("regularMarketPrice"),
            "previous_close": info.get("regularMarketPreviousClose"),
            "change": info.get("regularMarketChange"),
            "change_percent": info.get("regularMarketChangePercent"),
        }
    except Exception as e:
        return {"error": str(e)}


def get_forex_history(pair: str, period: str = "1mo") -> Dict:
    """获取货币对的历史数据"""
    try:
        ticker = yf.Ticker(f"{pair}=X")
        history = ticker.history(period=period)
        return {
            "latest": history.iloc[-1].to_dict(),
            "highest": history["High"].max(),
            "lowest": history["Low"].min(),
            "average": history["Close"].mean(),
        }
    except Exception as e:
        return {"error": str(e)}

async def process_forex_query(query: str) -> list:
    """将用户复杂的外汇风险分析问题分解为多个从不同角度出发的网络搜索查询"""
    client = OpenAI(
        api_key=DASHSCOPE_API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    system_prompt = """
    现在是2025年。
    你是一个专业且有洞察力的外汇风险分析助手，你的任务是将用户复杂的外汇风险分析问题分解为多个从不同角度出发的网络搜索查询，以便获取更全面和深入的分析信息。

    请仔细阅读并深入理解用户提出的问题，识别出问题中涉及的核心货币对以及用户想要分析的风险类型。

    基于你的理解，将用户的问题分解为4个清晰且相互独立的搜索查询语句，每个查询语句应侧重于一个不同的分析角度。你可以考虑以下角度，但不限于此：

    * **宏观经济角度：** 关注影响货币对所在国家或地区的关键经济指标，例如通货膨胀、利率、GDP增长、就业数据、制造业和服务业PMI、消费者信心指数、零售销售、贸易平衡等。搜索查询可以围绕这些指标的最新数据、预测以及潜在影响展开。
    * **货币政策角度：** 关注相关国家中央银行的货币政策动向，例如利率决议、量化宽松/紧缩政策、央行官员讲话、货币政策报告等。搜索查询可以关注政策变化、市场预期及其对汇率的影响。
    * **政治与地缘政治角度：** 关注可能影响货币对的政治事件和地缘政治风险，例如选举、政治动荡、国际关系、贸易争端、制裁、冲突等。搜索查询可以关注事件的最新进展及其对汇率的潜在冲击。
    * **市场情绪与预期角度：** 关注市场对该货币对的整体情绪、投资者的风险偏好以及未来的预期。搜索查询可以关注市场分析报告、投资者情绪调查、资金流向等。
    * **突发事件角度：** 考虑可能对汇率产生意外影响的突发事件，例如自然灾害、金融危机、公共卫生事件等。搜索查询可以关注最新的相关新闻和分析。

    请用JSON格式返回这些从不同角度出发的搜索查询语句。你可以根据判断，选择最适合每个查询语句的语言（中文或英文）。

    示例：

    用户问题：分析一下未来一个月英镑兑美元的风险。

    输出：
    {
    "search_queries": [
        "UK inflation rate and Bank of England monetary policy outlook", 
        "Political stability in the UK and its impact on GBP/USD", 
        "Market sentiment towards GBP/USD next month", 
        "Upcoming economic data releases in the US and their potential effect on GBP/USD"
    ]
    }
    """
    response = client.chat.completions.create(
        model="qwen-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
    )
    pattern = re.compile(r'```json(.*?)```', re.S)
    match = re.search(pattern, response.choices[0].message.content)
    try:
        if match:
            dic = json.loads(match.group(1))
            return dic["search_queries"]
        else:
            return {"error": "qwen-turbo无法解析JSON格式"}
    except Exception as e:
        return {"error": str(e)}
    
async def get_recent_forex_news(query: str) -> list:
    """针对query，获取货币对的最近新闻"""
    exa = Exa(api_key=EXA_API_KEY)
    result = exa.search_and_contents(
        query=query,
        num_results = 6,
        text = True,
        type = "neural",
        use_autoprompt = True,
        start_published_date = "2024-09-01T16:00:00.000Z",
        end_published_date = "2025-04-03T15:59:59.999Z"
    )
    results = result.results
    pagelist = []
    for result in results:
        page = [0, 0, 0, 0]
        page[0] = result.title
        page[1] = result.published_date
        page[2] = result.author
        page[3] = result.text
        pagelist.append(page)
    return pagelist

def write_to_rag_doc(page: list):
    """写入RAG文档"""
    

async def fetch_forex_news_from_exa(usermessage: str) -> list:
    """发送usermessage到exa，获取exa的分析结果,并写入RAG文档"""
    # 创建异步任务列表（一次性创建所有请求）
    queries = await process_forex_query(usermessage)
    tasks = [get_recent_forex_news(query) for query in queries]
    
    # 使用asyncio.gather并发执行所有任务
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # 合并结果并过滤错误
    allpages = []
    error_log = []
    for result in results:
        if isinstance(result, Exception):
            error_log.append(str(result))
            continue   
        unique_news = []
        for news in result:
            unique_news.append(news)
        
        allpages.extend(unique_news)

    # 构建路径确保能找到目录
    forex_docs_dir = os.path.join(CHATBOT_DIR, "data", "forex_docs")
    # 确保目录存在
    os.makedirs(forex_docs_dir, exist_ok=True)
    
    # 写入RAG文档
    for pagedata in range(len(allpages)):
        title = allpages[pagedata][0] 
        publishedDate = allpages[pagedata][1]
        author = allpages[pagedata][2]
        text = allpages[pagedata][3]
        file_path = os.path.join(forex_docs_dir, f"news{pagedata}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n### {author}\n{text} --- {publishedDate}\n\n")
    # 记录错误日志
    if error_log:
        print(f"API请求错误：{error_log}")

    return allpages


forex_tools = [
    Tool(
        name="GetForexPrice",
        func=get_forex_price,
        description="获取货币对的实时价格信息",
    ),
    Tool(
        name="GetForexHistory",
        func=get_forex_history,
        description="获取货币对的历史价格数据",
    ),
    Tool(
        name="GetRecentForexNews",
        func=fetch_forex_news_from_exa,
        description="获取货币对的最近新闻",
    ),
]


if __name__ == "__main__":
    asyncio.run(fetch_forex_news_from_exa("分析一下未来一个月人民币兑美元的风险。"))
