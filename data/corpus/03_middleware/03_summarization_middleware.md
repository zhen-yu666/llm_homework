# 摘要中间件

> 来源：https://docs.langchain.com/oss/python/langchain/middleware#built-in-middleware
> 抓取日期：2026-09-26
> 模块：03_middleware

## 概述

`SummarizationMiddleware` 在对话历史变得过长时进行压缩。它监控对话的 token 数量，当超过指定阈值时自动生成对话摘要，用摘要替换原始消息，从而减少上下文长度。

## 触发条件

通过 `trigger` 参数配置触发条件：

```python
SummarizationMiddleware(
    model="claude-sonnet-4-6",
    trigger={"tokens": 500}
)
```

当对话的 token 数超过 500 时，中间件会自动触发摘要生成。

## 工作原理

摘要中间件在每次模型调用之前检查对话状态。如果 token 数超过阈值，它调用指定的模型生成对话摘要，然后用摘要替换对话历史。这有助于管理上下文窗口限制，降低 API 成本，并提高模型在长对话中的表现。