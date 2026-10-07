# 检索增强生成（RAG）概述

> 来源：https://docs.langchain.com/oss/python/deepagents/retrieval
> 抓取日期：2026-09-26
> 模块：02_rag_retrieval

## LLM 的两个关键限制

大型语言模型（LLM）功能强大，但有两个关键限制：有限上下文（无法一次性摄入整个语料库）和静态知识（训练数据在某个时间点冻结）。

## 构建知识库

知识库是检索期间使用的文档或结构化数据的存储库。如果你需要自定义知识库，可以使用 LangChain 的文档加载器和向量存储从自己的数据构建一个。如果你已经有知识库（例如 SQL 数据库、文档数据库、CRM 或内部文档系统），则不需要重建它。你可以：将其作为智能体在 Agentic RAG 中的工具连接，或查询它并将检索到的内容作为上下文提供给 LLM（2-Step RAG）。

## 从检索到 RAG

检索允许 LLM 在运行时访问相关上下文。但大多数实际应用更进一步：它们将检索与生成集成，以产生有依据的、上下文感知的答案。这就是检索增强生成（RAG）的核心思想。检索管道成为结合搜索与生成的更广泛系统的基础。

## 检索管道

典型的检索工作流包含以下模块化组件：加载器（Loaders）、分割器（Splitters）、嵌入（Embeddings）、向量存储（Vector Stores）。每个组件都是模块化的：你可以在不重写应用逻辑的情况下替换加载器、分割器、嵌入或向量存储。

## RAG 架构对比

RAG 可以根据系统需求以多种方式实现。

| 架构 | 描述 | 控制力 | 灵活性 | 延迟 | 示例用例 |
|---|---|---|---|---|---|
| **2-Step RAG** | 检索总是发生在生成之前。简单且可预测 | 高 | 低 | 快 | FAQ、文档机器人 |
| **Agentic RAG** | LLM 驱动的智能体在推理过程中决定何时以及如何检索 | 低 | 高 | 可变 | 具有多工具访问权限的研究助手 |
| **Hybrid** | 结合两种方法的特点，带有验证步骤 | 中 | 中 | 可变 | 需要质量验证的领域特定问答 |

**延迟说明**：2-Step RAG 的延迟通常更可预测，因为 LLM 调用的最大次数是已知且有限制的。这种可预测性假设 LLM 推理时间是主导因素。然而，实际延迟还可能受到检索步骤性能的影响，如 API 响应时间、网络延迟或数据库查询，这些可能因使用的工具和基础设施而异。

## 2-Step RAG

在 2-Step RAG 中，检索步骤始终在生成步骤之前执行。这种架构简单明了且可预测，适用于许多检索相关文档是生成答案的明确前提的应用场景。

## Agentic RAG

智能体检索增强生成（Agentic RAG）结合了检索增强生成与基于智能体的推理优势。智能体（由 LLM 驱动）不是在回答前直接检索文档，而是逐步推理并决定在交互过程中何时以及如何检索信息。智能体启用 RAG 行为所需的唯一条件是访问一个或多个可以获取外部知识的工具，如文档加载器、Web API 或数据库查询。

```python
import requests
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

@tool
def fetch_url(url: str) -> str:
    """Fetch text content from a URL"""
    response = requests.get(url)
    return response.text

agent = create_agent(
    model=init_chat_model("openai:gpt-5.5"),
    tools=[fetch_url]
)
```