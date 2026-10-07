# 使用 LangGraph 构建自定义 RAG 工作流

> 来源：https://docs.langchain.com/oss/python/langchain/multi-agent/custom-workflow
> 抓取日期：2026-09-26
> 模块：02_rag_retrieval

## 自定义工作流架构

在自定义工作流架构中，你使用 LangGraph 定义自己的定制执行流。你可以完全控制图结构，包括顺序步骤、条件分支、循环和并行执行。

## 关键特性

- 对图结构的完全控制
- 混合确定性逻辑与智能体行为
- 支持顺序步骤、条件分支、循环和并行执行
- 将其他模式作为工作流中的节点嵌入

## 何时使用

当标准模式（子智能体、技能等）不适合你的需求、你需要混合确定性逻辑与智能体行为、或者你的用例需要复杂路由或多阶段处理时，使用自定义工作流。工作流中的每个节点可以是简单函数、LLM 调用或带有工具的完整智能体。

## 基本实现

核心洞察是：你可以在任何 LangGraph 节点中直接调用 LangChain 智能体，将自定义工作流的灵活性与预构建智能体的便利性结合起来。

```python
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END

agent = create_agent(model="openai:gpt-5.5", tools=[...])

def agent_node(state: State) -> dict:
    """A LangGraph node that invokes a LangChain agent."""
    result = agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })
    return {"answer": result["messages"][-1].content}

workflow = (
    StateGraph(State)
    .add_node("agent", agent_node)
    .add_edge(START, "agent")
    .add_edge("agent", END)
    .compile()
)
```

## 自定义 RAG 工作流示例

一个常见用例是将检索与智能体结合。以下工作流展示了三种类型的节点：

- **模型节点（Rewrite）**：使用结构化输出重写用户查询以改善检索
- **确定性节点（Retrieve）**：执行向量相似度搜索——不涉及 LLM
- **智能体节点（Agent）**：对检索到的上下文进行推理，并可以通过工具获取额外信息

```python
from typing import TypedDict
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
```