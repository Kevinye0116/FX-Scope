"""
测试DeepSearch功能 - 直接使用deepsearch模块
"""
import os
import sys
import asyncio
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)  # 添加backend目录到Python路径
sys.path.insert(0, current_dir)  # 添加chatbot目录到Python路径

# 检查deepsearch目录是否存在
deepsearch_dir = os.path.join(current_dir, "deepsearch")
if os.path.exists(deepsearch_dir):
    logger.info(f"找到deepsearch目录: {deepsearch_dir}")
    # 检查关键文件
    if os.path.exists(os.path.join(deepsearch_dir, "llm.py")):
        logger.info("找到llm.py文件")
    else:
        logger.error("未找到llm.py文件")
    if os.path.exists(os.path.join(deepsearch_dir, "graph.py")):
        logger.info("找到graph.py文件")
    else:
        logger.error("未找到graph.py文件")
else:
    logger.error(f"deepsearch目录不存在: {deepsearch_dir}")
    logger.error("请确保已将chinese-open-deep-research中的llm.py和graph.py复制到chatbot/deepsearch/目录")

# 尝试直接导入deepsearch模块进行测试
try:
    logger.info("尝试直接导入deepsearch模块...")
    from deepsearch import llm, graph
    logger.info("成功导入deepsearch模块")
except ImportError as e:
    logger.error(f"导入deepsearch模块失败: {e}")
    logger.warning("继续尝试导入DeepSearchAssistant...")

# 导入DeepSearchAssistant
try:
    from chatbot.agents.tools.deep_search import DeepSearchAssistant
    logger.info("成功导入DeepSearchAssistant")
except Exception as e:
    logger.error(f"导入DeepSearchAssistant失败: {e}")
    sys.exit(1)

async def test_deep_search():
    """测试DeepSearch功能"""
    try:
        # 初始化DeepSearchAssistant
        logger.info("初始化DeepSearchAssistant...")
        assistant = DeepSearchAssistant()
        logger.info("DeepSearchAssistant初始化成功")
        
        # 测试快速搜索
        query = "美欧贸易关系紧张对美元汇率风险的影响"
        logger.info(f"执行快速搜索: {query}")
        
        # 执行快速搜索并获取研究计划
        plan = await assistant.quick_search(query)
        logger.info("快速搜索完成")
        logger.info(f"研究计划:\n{plan}")
        
        # 测试完整搜索 (可选，耗时较长)
        perform_full_search = input("是否要执行完整搜索生成完整报告？(y/n): ").lower() == 'y'
        if perform_full_search:
            logger.info(f"执行完整搜索: {query}")
            result = await assistant.search(query)
            logger.info("完整搜索完成")
            # 显示结果的前200个字符
            logger.info(f"搜索结果 (前200字符):\n{result[:200]}...")
            logger.info(f"结果总长度: {len(result)} 字符")
            
            # 将完整报告保存到文件
            report_file = os.path.join(current_dir, "deep_search_report.md")
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(result)
            logger.info(f"完整报告已保存到: {report_file}")
        
        return True
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    logger.info("开始测试DeepSearch功能...")
    logger.info(f"Python路径: {sys.path}")
    
    try:
        result = asyncio.run(test_deep_search())
        if result:
            logger.info("测试成功完成")
        else:
            logger.error("测试失败")
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    except Exception as e:
        logger.error(f"运行测试时出错: {e}")
        
    logger.info("测试结束") 