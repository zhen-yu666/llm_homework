# 文本分割器

> 来源：https://docs.langchain.com/oss/python/integrations/splitters/index
> 抓取日期：2026-09-26
> 模块：02_rag_retrieval

## 概述

文本分割器将大型文档拆分为更小的块，这些块可以单独检索并适合模型上下文窗口限制。有几种分割策略，每种都有自己的优势。对于大多数用例，从 `RecursiveCharacterTextSplitter` 开始。它在保持上下文完整和管理块大小之间提供了良好的平衡。这种默认策略开箱即用效果很好，只有在你需要针对特定应用微调性能时才应考虑调整它。

## 基于文本结构的分割

文本自然地组织为层次单元，如段落、句子和单词。我们可以利用这种固有结构来指导分割策略，创建保持自然语言流畅性、保持块内语义连贯性并适应不同文本粒度级别的分割。LangChain 的 `RecursiveCharacterTextSplitter` 实现了这一概念：

- `RecursiveCharacterTextSplitter` 尝试保持较大单元（如段落）完整
- 如果一个单元超过块大小，它移动到下一个级别（如句子）
- 如果需要，此过程继续下降到单词级别

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=0
)
texts = text_splitter.split_text(document)
```

## 基于长度的分割

一种直观的策略是根据文档长度进行分割。这种简单而有效的方法确保每个块不超过指定的大小限制。基于长度的分割的关键优势：实现简单、块大小一致、易于适应不同的模型要求。可以基于 token 数（适用于语言模型）或字符数（在不同文本类型之间更一致）进行分割。

```python
from langchain_text_splitters import CharacterTextSplitter

text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=100,
    chunk_overlap=0
)
texts = text_splitter.split_text(document)
```

## 基于文档结构的分割

某些文档具有固有结构，如 HTML、Markdown 或 JSON 文件。在这些情况下，基于其结构进行分割是有益的，因为它通常自然地分组语义相关的文本。基于结构的分割的关键优势：保留文档的逻辑组织、保持每个块内的上下文、对于检索或摘要等下游任务可能更有效。Markdown 按标题（如 `#`、`##`、`###`）分割；HTML 使用标签分割；JSON 按对象或数组元素分割；代码按函数、类或逻辑块分割。

## 默认参数

`RecursiveCharacterTextSplitter` 的默认分隔符列表为 `["\n\n", "\n", " ", ""]`，默认 `chunk_size` 为 1000，默认 `chunk_overlap` 为 200（JavaScript 版本）。Python 版本中 `chunk_size` 通过 `length_function` 测量（默认为字符数）。