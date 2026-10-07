"""生成模块：提示模板与答案生成。"""
from typing import List

from langchain_core.documents import Document

from src.config import get_llm

RAG_PROMPT = """你是一个严谨的问答助手。请只依据下面提供的上下文回答问题。

要求：
1. 如果上下文中没有答案，明确说“根据提供的资料无法回答”。
2. 不要编造上下文之外的事实。
3. 回答尽量简洁，可以引用片段编号。

上下文：
{context}

问题：{question}

答案："""


def format_context(docs: List[Document]) -> str:
    """把召回片段拼成上下文，带 chunk_id 方便溯源。"""
    parts = []
    for i, doc in enumerate(docs, start=1):
        cid = doc.metadata.get("chunk_id", f"chunk{i}")
        parts.append(f"[{cid}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def generate_answer(question: str, docs: List[Document],
                    temperature: float = 0.0) -> str:
    """基于召回片段生成答案。"""
    llm = get_llm(temperature=temperature)
    prompt = RAG_PROMPT.format(context=format_context(docs), question=question)
    return llm.invoke(prompt).content


def generate_bare(question: str, temperature: float = 0.0) -> str:
    """不接检索，直接问 LLM，用于 T1 对照。"""
    llm = get_llm(temperature=temperature)
    return llm.invoke(question).content