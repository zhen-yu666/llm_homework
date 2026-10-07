# 上下文工程

> 来源：https://docs.langchain.com/oss/python/langchain/context-engineering
> 抓取日期：2026-09-26
> 模块：05_extensions

## 概述

上下文工程是向模型提供正确信息以产生高质量输出的实践。对于智能体而言，这包括管理对话历史、检索相关文档、控制提示词内容和结构，以及在正确的时间注入正确的上下文。

## 中间件在上下文工程中的作用

中间件是实现上下文工程的核心工具。通过中间件，你可以：

- 在模型调用之前动态修改提示词（`beforeModel`）
- 在工具调用之前验证或修改参数（`wrapToolCall`）
- 在对话过长时自动摘要（`SummarizationMiddleware`）
- 在发送给模型之前脱敏敏感信息（`PIIMiddleware`）
- 在模型响应之后验证或转换输出（`afterModel`）

## RAG 中的上下文工程

在 RAG 系统中，上下文工程的关键决策包括：

- 检索多少个文档（`k` 值）
- 如何分块文档（chunk_size、overlap）
- 是否使用查询重写或多查询
- 是否使用重排序
- 是否压缩检索到的上下文

这些决策直接影响生成答案的质量、忠实度和幻觉率。