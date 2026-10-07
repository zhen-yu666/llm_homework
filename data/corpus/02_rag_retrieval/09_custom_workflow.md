# 自定义工作流（RAG 管道示例）

> 来源：https://docs.langchain.com/oss/python/langchain/multi-agent/custom-workflow
> 抓取日期：2026-09-26
> 模块：02_rag_retrieval

## 核心洞察

你可以在任何 LangGraph 节点中直接调用 LangChain 智能体，将自定义工作流的灵活性与预构建智能体的便利性结合起来。

## RAG 管道示例

一个常见用例是将检索与智能体结合。以下示例构建了一个 WNBA 统计助手，它从知识库中检索并可以获取实时新闻。

### 三种类型的节点

- **模型节点（Rewrite）**：使用结构化输出重写用户查询以改善检索
- **确定性节点（Retrieve）**：执行向量相似度搜索——不涉及 LLM
- **智能体节点（Agent）**：对检索到的上下文进行推理，并可以通过工具获取额外信息

### 状态管理

你可以使用 LangGraph 状态在工作流步骤之间传递信息。这允许工作流的每个部分读取和更新结构化字段，使数据在节点之间共享和传递变得容易。

```python
from typing import TypedDict
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

class State(TypedDict):
    question: str
    rewritten_query: str
    documents: list[str]
    answer: str

embeddings = OpenAIEmbeddings()
vector_store = InMemoryVectorStore(embeddings)
vector_store.add_texts([
    "New York Liberty 2024 roster: Breanna Stewart, Sabrina Ionescu, Jonquel Jones, Courtney Vandersloot.",
    "Las Vegas Aces 2024 roster: A'ja Wilson, Kelsey Plum, Jackie Young, Chelsea Gray.",
])
```