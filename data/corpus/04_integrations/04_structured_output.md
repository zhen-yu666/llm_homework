# 结构化输出

> 来源：https://docs.langchain.com/oss/python/langchain/structured-output
> 抓取日期：2026-09-26
> 模块：04_integrations

## 概述

结构化输出允许智能体以特定、可预测的格式返回数据。无需解析自然语言响应，你获得的是类型化的结构化数据。

## 工作原理

用户设置所需的结构化输出 schema，当模型生成结构化数据时，系统会捕获、验证并将其返回到智能体状态的 `structuredResponse` 键中。

## with_structured_output

模型包装器，返回与给定 schema 匹配的格式化输出：

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-5.5")
structured_model = model.with_structured_output(SchemaClass)

result = structured_model.invoke("Extract the key information")
# result 是 SchemaClass 的实例
```

## 输出解析器

输出解析器将原始 LLM 文本转换为结构化数据。它们支持完整输出和流式部分输出。常用的解析器包括：

- **JsonOutputParser**：将 LLM 输出解析为 JSON
- **PydanticOutputParser**：解析为 Pydantic 模型
- **OpenAIToolsOutputParser**：使用 OpenAI 工具调用进行解析

## 推荐用法

对于 OpenAI 和兼容模型，推荐使用 `with_structured_output` 而不是手动解析。它利用 OpenAI 的结构化输出 API，提供更可靠的 schema 合规性。