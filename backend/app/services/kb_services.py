from config import BASE_DIR, settings
from openai import OpenAI
import numpy as np
import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings


KB_DIR = BASE_DIR / 'data' / 'kb'
CHROMA_DIR = BASE_DIR / 'data' / 'chroma'

# 嵌入模型走 SiliconFlow 的 API（OpenAI 兼容 /embeddings 接口）
# 不再本地跑 sentence-transformers：免费容器(512MB)装不下 torch+模型，
# API 方式云端/本地行为一致，且向量维度固定 1024
EMBEDDING_MODEL = 'BAAI/bge-m3'

_client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)


class ApiEmbeddingFunction(EmbeddingFunction[Documents]):
    """ 自定义 ChromaDB 嵌入函数：批量文本 → 调嵌入 API → 返回向量列表
    chromadb 1.x 的协议要求实现 name / get_config / build_from_config，
    用于把嵌入函数的配置持久化到集合元数据里，重启后能校验一致性
    """

    def __init__(self, model: str = EMBEDDING_MODEL):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        res = _client.embeddings.create(model=self.model, input=input)
        # 按 index 排序防止返回乱序；再 做 L2 归一化（归一化后 L2 排序等价于余弦相似度）
        vecs = [item.embedding for item in sorted(res.data, key=lambda x: x.index)]
        arr = np.asarray(vecs, dtype=float)
        norm = np.linalg.norm(arr, axis=1, keepdims=True)
        return (arr / np.maximum(norm, 1e-12)).tolist()

    @staticmethod
    def name() -> str:
        return 'siliconflow_bge_m3'

    def get_config(self) -> dict:
        return {'model': self.model}

    @staticmethod
    def build_from_config(config: dict) -> 'ApiEmbeddingFunction':
        return ApiEmbeddingFunction(model=config.get('model', EMBEDDING_MODEL))


_collection = None  # 用于存储 ChromaDB 的集合对象

_embedding_fn = None  # 向量化模型
def get_embedding_fn():
    """ 向量模型的懒加载 """
    global _embedding_fn
    if _embedding_fn is not None:
        return _embedding_fn

    _embedding_fn = ApiEmbeddingFunction()
    return _embedding_fn


def get_collection() -> Collection:
    """ 向量库的初始化 """
    global _collection
    # 如果数据库表内容在之前已经加载过就可以直接使用，节省资源和运行时间
    if _collection is not None:
        return _collection

    # 加载项目所需路径，如果不存在就自动创建
    KB_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    # 初始化 ChromaDB 客户端
    # 设置向量数据库保存的路径
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    # 创建向量数据库表
    col = client.get_or_create_collection(
        name='lab_kb', embedding_function=get_embedding_fn()
    )

    if col.count() == 0:
        ids = []   # 存储片段的id
        docs = []  # 文本内容
        metas = []   # 元数据

        # 加载需要进行向量化的文档
        for path in sorted(KB_DIR.glob('*.md')):  # KB_DIR 路径下的全部 .md 文件
            text = path.read_text(encoding='UTF-8').strip()
            if not text:
                continue

            docs.append(text)
            ids.append(path.stem)
            metas.append({'source': path.name})

        if docs:  # 添加到数据表中
            col.add(ids=ids, documents=docs, metadatas=metas)

    _collection = col
    return col

def warmup():
    """ 服务启动前的预热，防止在用户提问时才开始初始化，导致等待时间过长 """
    col = get_collection()
    # 说明此时向量数据库中已经存储了数据
    if col.count() > 0:
        col.query(query_texts=['预热'], n_results=1)


# 通过搜索向量数据库查询与问题匹配的句子
def search(query: str):
    """ 检索向量数据库 """
    col = get_collection()

    if col.count() == 0:
        return ''

    # 单次最多查询top-n
    limit = min(5, col.count())
    res = col.query(query_texts=[query], n_results=limit)
    docs = (res.get('documents') or [[]])[0]
    metas = (res.get('metadatas') or [[]])[0]
    distances = (res.get('distances') or [[]])[0]

    score_parts = []
    for doc, metas, distance in zip(docs, metas, distances):
        # chromadb 默认计算的都是L2距离，值越小越相似，cos也是距离 = 1 - cos相似度
        score = 1 / (1 + distance)

        if score < 0.5:
            continue

        name = metas.get('source') or ''
        score_parts.append({'score': score, 'content': f'{name}\n{doc}'})

    # print('==='*20,score_parts)
    # 将分数从高到低排序
    score_parts.sort(key=lambda x:x['score'], reverse=True)
    # 返回分数前二的内容
    final_parts = [item['content'] for item in score_parts[:2]]
    return '\n\n'.join(final_parts)
