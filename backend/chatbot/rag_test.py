import os
import logging
from data.docstore import ForexKnowledgeBase

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_load_docs():
    try:
        # 初始化知识库
        kb = ForexKnowledgeBase()
        
        # 获取文档目录路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        docs_path = os.path.join(current_dir, "data", "forex_docs")
        
        # 打印目录信息
        logger.info(f"文档目录路径: {docs_path}")
        logger.info(f"目录是否存在: {os.path.exists(docs_path)}")
        
        # 加载文档
        kb.load_documents(docs_path)
        
        # 测试检索
        query = "什么是外汇风险？"
        results = kb.similarity_search(query)
        
        logger.info("检索结果:")
        for i, result in enumerate(results, 1):
            logger.info(f"结果 {i}: {result}")
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        logger.exception("详细错误信息：")

if __name__ == "__main__":
    test_load_docs()