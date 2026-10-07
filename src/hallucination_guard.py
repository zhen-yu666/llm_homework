"""T8-1 幻觉治理：先检测再生成（RAG-HAT 思路）。"""
from typing import List, Tuple

from langchain_core.documents import Document

from src.config import get_llm

# 检测提示词：判断召回的片段是否足以回答问题
SUFFICIENCY_PROMPT = """你是一个严谨的幻觉检测器。你的唯一任务是判断下面提供的上下文是否包含足够的信息来准确回答用户的问题。

要求：
1. 如果上下文足以回答问题，只输出："YES"
2. 如果上下文缺少关键信息，或者完全不相关，只输出："NO"
3. 不要尝试回答问题，不要输出任何解释。

上下文：
{context}

问题：{question}

判断结果（YES/NO）："""


def check_sufficiency(question: str, docs: List[Document]) -> bool:
    """用 LLM 判断召回片段是否足以回答问题。

    Returns:
        True 表示信息充足，可以生成；
        False 表示信息不足，应拦截并返回“资料不足”。
    """
    if not docs:
        return False

    llm = get_llm(temperature=0.0)
    # 拼接上下文，控制长度避免超 token 限制
    context = "\n\n".join([d.page_content for d in docs])[:4000]
    prompt = SUFFICIENCY_PROMPT.format(context=context, question=question)

    try:
        result = llm.invoke(prompt).content.strip().upper()
        return result.startswith("YES")
    except Exception:
        # 检测失败时保守放行，避免误伤
        return True


def generate_with_guard(question: str, docs: List[Document]) -> Tuple[str, bool]:
    """带幻觉检测的生成流程。

    Returns:
        (answer, passed): answer 是最终答案，passed 表示是否通过了检测。
    """
    passed = check_sufficiency(question, docs)
    if not passed:
        return "根据现有资料无法回答该问题。", False

    from src.generate import generate_answer
    return generate_answer(question, docs), True