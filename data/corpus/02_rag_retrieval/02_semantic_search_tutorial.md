# 语义搜索引擎构建教程

> 来源：https://docs.langchain.com/oss/javascript/langchain/knowledge-base
> 抓取日期：2026-09-26
> 模块：02_rag_retrieval

## 概述

使用 LangChain 嵌入和向量存储构建 PDF 语义搜索引擎。用它来检索与查询相似的段落，然后将检索器插入 RAG 或其他 LLM 工作流。本教程涵盖：从 PDF 创建 Document 对象、生成嵌入、加载和分割 PDF、在向量存储中索引块并按相似度查询、将存储包装为检索器。

## Document 抽象

LangChain 实现了 Document 抽象，用于表示文本单元及其关联的元数据。它具有三个属性：

- **pageContent**：表示内容的字符串
- **metadata**：包含任意元数据的字典
- **id**：（可选）文档的字符串标识符

metadata 可以捕获文档的来源、与其他文档的关系以及其他信息。单个 Document 通常表示较大文档的一个块。

```python
from langchain_core.documents import Document

documents = [
    Document(
        page_content="Dogs are great companions, known for their loyalty and friendliness.",
        metadata={"source": "mammal-pets-doc"}
    ),
    Document(
        page_content="Cats are independent pets that often enjoy their own space.",
        metadata={"source": "mammal-pets-doc"}
    )
]
```

## 生成嵌入

向量搜索存储与文本关联的数值向量。将查询嵌入为相同维度的向量，然后使用相似度度量（如余弦相似度）来查找相关文本。LangChain 支持来自许多提供商的嵌入。

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector1 = embeddings.embed_query(documents[0].page_content)
vector2 = embeddings.embed_query(documents[1].page_content)
```

## 加载和分割 PDF

使用文档加载器读取 PDF 内容，然后使用文本分割器将长文档拆分为可管理的块。这一步是检索质量的基础：块太大可能包含不相关信息，块太小可能丢失上下文。

## 索引和查询

将分割后的块存入向量存储，通过相似度搜索进行查询。FAISS 和 Chroma 是常用的本地向量存储选择。