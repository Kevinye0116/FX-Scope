from typing import List
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
import logging
from dotenv import load_dotenv
from langchain.schema import Document

load_dotenv()

# 获取logger实例
logger = logging.getLogger("django")

# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 获取chatbot目录
CHATBOT_DIR = os.path.dirname(CURRENT_DIR)

class ForexKnowledgeBase:
    def __init__(self):
        try:
            # 使用阿里云 DashScope Embedding
            self.embeddings = DashScopeEmbeddings(
                model="text-embedding-v2",  # 阿里云的 embedding 模型
                dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
                max_retries=6
            )
            self.vector_store = None
            # 使用绝对路径指向 backend/chatbot/data/chroma_db
            self.persist_directory = os.path.join(CURRENT_DIR, "chroma_db")
            
            # 确保存储目录存在
            os.makedirs(self.persist_directory, exist_ok=True)
            
        except Exception as e:
            logger.error(f"初始化 ForexKnowledgeBase 失败: {str(e)}")
            raise
        
    def load_documents(self, docs_dir: str):
        """加载文档并创建向量存储"""
        try:
            if not os.path.exists(docs_dir):
                raise FileNotFoundError(f"文档目录不存在: {docs_dir}")
            
            logger.info(f"开始加载文档从: {docs_dir}")
            # 修改 DirectoryLoader 的配置，明确指定编码为 UTF-8
            loader = DirectoryLoader(
                docs_dir, 
                glob="**/*.txt", 
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"}  # 明确指定 UTF-8 编码
            )
            
            try:
                documents = loader.load()
            except Exception as e:
                logger.error(f"加载文档时出错: {str(e)}")
                # 尝试手动加载文件
                documents = []
                for file in os.listdir(docs_dir):
                    if file.endswith('.txt'):
                        file_path = os.path.join(docs_dir, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                text = f.read()
                                documents.append(Document(
                                    page_content=text,
                                    metadata={"source": file_path}
                                ))
                            logger.info(f"成功加载文件: {file}")
                        except Exception as e:
                            logger.error(f"读取文件 {file} 失败: {str(e)}")
            
            if not documents:
                raise ValueError(f"在 {docs_dir} 中没有找到任何文档")
            
            logger.info(f"找到 {len(documents)} 个文档")
            
            # 分割文档
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=len,
                separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
            )
            splits = text_splitter.split_documents(documents)
            logger.info(f"文档分割完成，共 {len(splits)} 个片段")
            
            # 创建向量存储
            self.vector_store = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            logger.info("向量存储创建成功")
            
        except Exception as e:
            logger.error(f"加载文档失败: {str(e)}")
            raise
    
    def similarity_search(self, query: str, k: int = 3) -> List[str]:
        """检索相关文档片段"""
        try:
            if not self.vector_store:
                logger.warning("向量存储未初始化")
                return []
            
            docs = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in docs]
            
        except Exception as e:
            logger.error(f"相似度搜索失败: {str(e)}")
            return []