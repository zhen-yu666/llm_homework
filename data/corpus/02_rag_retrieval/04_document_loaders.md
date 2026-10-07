# 文档加载器

> 来源：https://docs.langchain.com/oss/python/integrations/document_loaders
> 抓取日期：2026-09-26
> 模块：02_rag_retrieval

## 概述

文档加载器负责从各种来源读取数据并将其转换为 LangChain Document 对象。支持的来源包括 PDF、CSV、HTML、Markdown、JSON、数据库、API 等。

## 常用加载器

- **PyPDFLoader**：从 PDF 文件加载文档，每个页面生成一个 Document
- **TextLoader**：从纯文本文件加载
- **CSVLoader**：从 CSV 文件加载，每行生成一个 Document
- **DirectoryLoader**：从目录批量加载文件，支持通配符模式
- **WebBaseLoader**：从网页加载内容
- **UnstructuredMarkdownLoader**：从 Markdown 文件加载，保留结构信息

## 加载器接口

所有文档加载器实现统一的 `load()` 和 `lazy_load()` 接口：

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("document.pdf")
documents = loader.load()
# documents 是 Document 对象列表
# 每个 Document 包含 page_content 和 metadata
```

## 元数据的重要性

加载器通常会自动填充元数据字段，如 `source`（文件路径）、`page`（页码）等。这些元数据在后续的检索和过滤中非常有用，可以在向量存储中用于元数据过滤，或在重排序阶段用于加权。