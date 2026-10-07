# 检索器

> 来源：https://docs.langchain.com/oss/python/integrations/retrievers
> 抓取日期：2026-09-26
> 模块：02_rag_retrieval

## 概述

检索器返回给定文本查询的 Document 对象列表。LangChain 提供了多种检索器实现。

## BaseRetriever

`BaseRetriever` 是所有检索器的基类。它继承自 `RunnableSerializable`，支持标准的 Runnable 接口（`invoke()`、`batch()`、`stream()`）。

## MultiQueryRetriever

`MultiQueryRetriever` 给定一个用户查询，使用 LLM 生成一组查询，为每个查询检索文档，并返回所有检索到的文档的唯一并集。这种方法通过检索可能不完全匹配原始查询措辞的相关文档来提高召回率。

```python
from langchain.retrievers.multi_query import MultiQueryRetriever

multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=base_retriever,
    llm=llm,
    include_original=True  # 包含原始查询以获得更可靠的检索
)
```

每个生成的查询用于从向量存储中检索文档。所有查询的结果被组合和去重，以产生更丰富的检索上下文集合。

## ContextualCompressionRetriever

`ContextualCompressionRetriever` 包装一个基础检索器并压缩结果。它通过过滤和压缩检索到的文档来改善检索质量，然后将压缩后的上下文传递给语言模型。这可以减少不必要的上下文，只保留与查询最相关的信息。

```python
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)
```

工作原理：基础检索器首先从向量存储中检索初始候选文档集合，然后基础压缩器处理这些文档并移除不相关的内容，只保留与用户查询相关的部分。结果压缩后的上下文传递给 RAG 链，这有助于减少噪声并提高生成答案的质量。

## SelfQueryRetriever

`SelfQueryRetriever` 允许语言模型将用户的自然语言问题翻译为带有可选元数据过滤器的结构化查询。`SelfQueryRetriever.from_llm()` 将 LLM 与向量存储连接，使其能够解释问题并生成语义查询和元数据过滤器。

## EnsembleRetriever

`EnsembleRetriever` 将多个检索器的结果合并。常用于混合检索场景，将 BM25（稀疏）和向量检索（稠密）的结果通过 RRF（倒数排名融合）或加权方式结合。