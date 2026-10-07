"""编排模块（T6 选做，本项目选 T7，故此处仅保留 T7 评估辅助路由）。

按问题等级路由到不同链路：
- L1/L2：直接 top-k 检索 + 生成
- L3/L4：先查询改写，再检索，再生成
"""
from typing import List

from langchain_core.documents import Document

from src.config import get_llm
from src.generate import generate_answer
from src.retriever import HybridRetriever


def rewrite_query(question: str) -> str:
    """用 LLM 把口语化问题改写为检索友好形式。"""
    llm = get_llm()
    prompt = (
        f"请把下面的问题改写为适合检索的、包含关键术语的查询，只输出改写后的查询：\n\n{question}"
    )
    return llm.invoke(prompt).content.strip()


def route_and_answer(question: str, level: str, retriever: HybridRetriever,
                     k: int = 5) -> dict:
    """按等级路由。"""
    if level in {"L3", "L4"}:
        query = rewrite_query(question)
        results = retriever.search(query, k=k)
    else:
        query = question
        results = retriever.search(question, k=k)
    docs = [doc for doc, _ in results]
    answer = generate_answer(question, docs)
    return {
        "question": question,
        "level": level,
        "rewritten_query": query,
        "retrieved_chunk_ids": [d.metadata.get("chunk_id") for d in docs],
        "answer": answer,
    }