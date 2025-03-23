"""
DeepSearch模块 - 基于LangGraph和智谱AI的研究报告生成系统

该模块包含：
- graph.py: LangGraph工作流定义和网络搜索功能
- llm.py: 智谱AI接口和工具定义
"""

# 导入适配器模块以确保正确设置路径
try:
    from .deepsearch_adapter import build_graph, init_llm, ZhipuAIChat
    # 将关键函数和类暴露给上层模块
    __all__ = ['build_graph', 'init_llm', 'ZhipuAIChat']
except Exception as e:
    import logging
    logger = logging.getLogger("django")
    logger.error(f"导入deepsearch适配器失败: {e}")

__version__ = "0.1.0" 