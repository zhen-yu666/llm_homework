"""检索后优化：规则重排、Cross-Encoder 重排、上下文压缩。"""
from typing import List, Tuple

from langchain_core.documents import Document

from src.config import get_llm
"""检索后优化：规则重排、Cross-Encoder 重排、上下文压缩。"""
import re
from typing import List, Tuple

from langchain_core.documents import Document

from src.config import get_llm

def rule_rerank(results: List[Tuple[Document, float]],
                prefer_sources: List[str] = None) -> List[Tuple[Document, float]]:
    """基于规则的重排：优先来源、按 chunk_id 稳定排序。"""
    prefer_sources = prefer_sources or []
    def key(item):
        doc, score = item
        src = doc.metadata.get("source", "")
        prefer = 0 if any(s in src for s in prefer_sources) else 1
        return (prefer, -score)
    return sorted(results, key=key)


def cross_encoder_rerank(query: str, results: List[Tuple[Document, float]],
                         top_k: int = 3, model_name: str = "BAAI/bge-reranker-base"):
    """基于 Cross-Encoder 的重排。首次调用会下载模型。"""
    from sentence_transformers import CrossEncoder
    model = CrossEncoder(model_name)
    pairs = [(query, doc.page_content) for doc, _ in results]
    scores = model.predict(pairs)
    ranked = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
    return [(doc, float(s)) for (doc, _), s in ranked[:top_k]]


def llm_judge_rerank(query: str, results: List[Tuple[Document, float]],
                     top_k: int = 3) -> List[Tuple[Document, float]]:
    """按课件 9.4.4 JudgeRank 思路，用 LLM 对每个片段打相关性分。"""
    llm = get_llm()
    scored = []
    for doc, _ in results:
        prompt = (
            f"问题：{query}\n\n片段：{doc.page_content[:800]}\n\n"
            "请判断该片段与问题的相关性，输出 0-10 的整数分数，只输出数字。"
        )
        try:
            s = llm.invoke(prompt).content.strip()
            score = float(re.findall(r"\d+", s)[0]) if re.findall(r"\d+", s) else 0
        except Exception:
            score = 0
        scored.append((doc, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def compress_context(query: str, results: List[Tuple[Document, float]],
                     top_k: int = 3) -> List[Document]:
    """基于 LLM 的上下文压缩：只保留与问题相关的句子。"""
    llm = get_llm()
    compressed = []
    for doc, _ in results[:top_k]:
        prompt = (
            f"问题：{query}\n\n以下片段中，只保留与问题直接相关的句子，"
            f"不要添加任何解释：\n\n{doc.page_content}"
        )
        try:
            text = llm.invoke(prompt).content.strip()
        except Exception:
            text = doc.page_content
        compressed.append(Document(page_content=text, metadata=doc.metadata))
    return compressed


import re  # noqa: E402