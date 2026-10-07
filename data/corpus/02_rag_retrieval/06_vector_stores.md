# 向量存储

> 来源：https://docs.langchain.com/oss/python/integrations/vectorstores
> 抓取日期：2026-09-26
> 模块：02_rag_retrieval

## 概述

向量存储用于存储和检索嵌入向量。LangChain 提供了统一的接口来与各种向量数据库交互。

## 常用向量存储

- **FAISS**：Facebook AI Similarity Search，高效的相似度搜索库，适合本地开发和中小规模数据。支持 CPU 和 GPU。
- **Chroma**：开发者友好的向量数据库，默认在本地运行，支持元数据过滤和持久化。适合中小型 RAG 系统。
- **InMemoryVectorStore**：LangChain 内置的内存向量存储，适合快速原型和小规模数据。
- **PGVector**：基于 PostgreSQL 的向量存储，适合已有 PostgreSQL 基础设施的场景。
- **Pinecone**：托管的向量数据库，适合生产环境大规模部署。

## FAISS 使用示例

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vector_store = FAISS.from_documents(documents, embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 5})
```

## Chroma 使用示例

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
db = Chroma.from_documents(
    documents,
    embeddings,
    persist_directory="db"
)
db.persist()  # 持久化保存
```

## 统一接口

所有向量存储实现统一的接口：`add_documents()`、`similarity_search()`、`similarity_search_with_score()`、`as_retriever()`。这使得在开发过程中可以轻松切换不同的向量存储后端。