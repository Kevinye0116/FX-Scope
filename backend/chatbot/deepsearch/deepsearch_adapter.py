"""
DeepSearch适配器模块 - 帮助正确导入deepsearch模块

此模块用于解决导入问题，确保其他模块可以正确导入llm和graph
"""
import os
import sys
import logging

logger = logging.getLogger("django")

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将当前目录添加到Python路径
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    logger.info(f"添加deepsearch目录到Python路径: {current_dir}")

# 检查llm.py和graph.py是否存在
llm_path = os.path.join(current_dir, "llm.py")
graph_path = os.path.join(current_dir, "graph.py")

if not os.path.exists(llm_path):
    logger.error(f"llm.py文件不存在: {llm_path}")
    logger.error("请将chinese-open-deep-research/llm.py复制到此目录")

if not os.path.exists(graph_path):
    logger.error(f"graph.py文件不存在: {graph_path}")
    logger.error("请将chinese-open-deep-research/graph.py复制到此目录")

# 导入langgraph和zhipuai包
try:
    import langgraph
    logger.info("成功导入langgraph包")
except ImportError:
    logger.error("缺少langgraph包，请安装: pip install langgraph")

try:
    import zhipuai
    logger.info("成功导入zhipuai包")
except ImportError:
    logger.error("缺少zhipuai包，请安装: pip install zhipuai")

# 如果llm.py和graph.py都存在，导入它们以便其他模块可以访问
if os.path.exists(llm_path) and os.path.exists(graph_path):
    try:
        from . import llm
        from . import graph
        logger.info("成功导入deepsearch的llm和graph模块")
        
        # 提供一些可能会用到的函数
        build_graph = graph.builder
        init_llm = llm.init_chat_model
        ZhipuAIChat = llm.ZhipuAIChat
    except Exception as e:
        logger.error(f"导入llm或graph模块失败: {e}")
        logger.error("请确认llm.py和graph.py文件内容正确") 