"""
DeepSearch 工具 - 使用deepsearch模块的功能实现深度搜索
此文件是连接FX-Scope与deepsearch模块的桥梁
"""
import os
import logging
import asyncio
import uuid
import sys
from typing import Optional, Dict, Any, Literal
from typing_extensions import TypedDict

# 获取logger实例
logger = logging.getLogger("django")

# 导入deepsearch模块
try:
    # 导入langgraph
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import END
    from langgraph.types import Command
    
    # 导入deepsearch适配器
    from chatbot.deepsearch import build_graph, init_llm
    
    # 标记是否成功导入
    DEEPSEARCH_AVAILABLE = True
    logger.info("成功导入deepsearch模块")
except ImportError as e:
    logger.error(f"导入deepsearch模块失败: {e}")
    logger.error(f"当前Python路径: {sys.path}")
    logger.error("请确保已将chinese-open-deep-research中的llm.py和graph.py正确复制到chatbot/deepsearch/目录")
    DEEPSEARCH_AVAILABLE = False

class DeepSearchAssistant:
    """深度搜索助手，直接使用deepsearch模块中的功能"""
    
    def __init__(self):
        """初始化深度搜索助手"""
        try:
            if not DEEPSEARCH_AVAILABLE:
                self.initialized = False
                logger.error("DeepSearch模块不可用，无法初始化")
                return
                
            # 初始化LangGraph组件
            self.memory = MemorySaver()
            self.graph = build_graph.compile(checkpointer=self.memory)
            
            # 标记初始化状态
            self.initialized = True
            logger.info("DeepSearch助手初始化成功")
                
        except Exception as e:
            logger.error(f"初始化DeepSearch助手失败: {str(e)}")
            self.initialized = False

    async def search(self, query: str) -> str:
        """
        执行深度搜索并返回完整研究报告
        
        参数:
            query: 搜索查询
            
        返回:
            str: 完整的研究报告
        """
        if not self.initialized:
            return "【深度搜索】引擎未能正确初始化，无法执行深度搜索。正在使用备用方法回答您的问题。"
            
        try:
            logger.info(f"执行深度搜索: {query}")
            
            # 创建新线程ID并保存到实例变量
            thread_id = str(uuid.uuid4())
            thread = {"configurable": {"thread_id": thread_id}}
            
            # 步骤1: 首先生成研究计划 - 发送初始主题
            logger.info("生成研究计划...")
            command = {"topic": query}
            logger.info(f"研究计划命令: {command}")
            
            # 直接使用graph模块生成研究计划
            sections_display = ""
            async for event in self.graph.astream(command, thread, stream_mode="updates"):
                logger.info(f"事件类型: {list(event.keys())}")
                
                if '__interrupt__' in event:
                    interrupt_value = event['__interrupt__'][0].value
                    sections_display = interrupt_value
                    break
            
            if not sections_display or (isinstance(sections_display, str) and sections_display.startswith("【")):
                logger.error("研究计划生成失败")
                return "【深度搜索】生成研究计划失败。正在使用备用方法回答您的问题。"
            
            plan = sections_display
            logger.info("研究计划生成成功，继续生成完整报告...")
            
            # 步骤2: 自动批准研究计划，跳过人工反馈阶段
            # 模拟chinese-open-deep-research的human_feedback函数返回为True的情况
            # 在graph.py中，当feedback为True时，会启动build_section_with_web_research节点
            
            # 创建Command对象，resume=True表示继续执行图
            # 直接使用空的Command(resume=True)而不添加额外参数
            logger.info("使用resume=True命令继续执行图")
            resume_command = Command(resume=True)
            
            # 使用LangGraph继续执行以生成完整报告
            final_report = ""
            try:
                async for event in self.graph.astream(resume_command, thread, stream_mode="updates"):
                    # 记录事件类型，帮助调试
                    keys = list(event.keys())
                    logger.info(f"事件类型: {keys}")
                    
                    # 跟踪章节生成进度
                    if 'build_section_with_web_research' in event:
                        section_event = event['build_section_with_web_research']
                        if 'completed_sections' in section_event and section_event['completed_sections']:
                            section = section_event['completed_sections'][0]
                            logger.info(f"生成章节: {section.name}")
                    
                    # 获取最终报告
                    if 'compile_final_report' in event:
                        final_event = event['compile_final_report']
                        if 'final_report' in final_event:
                            final_report = final_event['final_report']
                            logger.info("生成最终报告成功")
                            break
            except Exception as e:
                logger.error(f"生成完整报告过程中出错: {str(e)}", exc_info=True)
                return f"【深度搜索】在生成报告过程中出现错误: {str(e)}\n\n{plan}"
            
            # 返回结果
            if final_report:
                logger.info(f"成功生成最终报告: {len(final_report)}字符")
                return final_report
            else:
                logger.warning("未能生成最终报告，返回研究计划")
                return f"【注意：仅返回研究计划】\n\n{plan}"
                
        except Exception as e:
            logger.error(f"DeepSearch执行失败: {str(e)}", exc_info=True)
            return f"【深度搜索】在执行搜索时遇到技术问题: {str(e)}\n\n我将使用基本知识回答您的问题。"
            
    async def quick_search(self, query: str) -> str:
        """
        执行快速搜索，只返回研究计划
        
        参数:
            query: 搜索查询
            
        返回:
            str: 研究计划
        """
        if not self.initialized:
            return "【深度搜索】引擎未能正确初始化，无法执行深度搜索。"
            
        try:
            logger.info(f"执行快速搜索: {query}")
            
            # 创建新线程ID
            thread_id = str(uuid.uuid4())
            thread = {"configurable": {"thread_id": thread_id}}
            
            # 设置主题
            command = {"topic": query}
            logger.info(f"使用命令: {command}")
            
            # 直接使用graph模块生成研究计划
            sections_display = ""
            async for event in self.graph.astream(command, thread, stream_mode="updates"):
                logger.info(f"事件类型: {list(event.keys())}")
                
                if '__interrupt__' in event:
                    interrupt_value = event['__interrupt__'][0].value
                    sections_display = interrupt_value
                    break
            
            if sections_display:
                logger.info("研究计划生成成功")
                return sections_display
            else:
                logger.warning("研究计划生成失败")
                return "【深度搜索】无法生成研究计划，请尝试使用其他关键词。"
                
        except Exception as e:
            logger.error(f"快速搜索执行失败: {str(e)}", exc_info=True)
            return f"【深度搜索】在执行快速搜索时遇到技术问题: {str(e)}"