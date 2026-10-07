# 人在回路中间件

> 来源：https://docs.langchain.com/oss/python/langchain/middleware#built-in-middleware
> 抓取日期：2026-09-26
> 模块：03_middleware

## 概述

`HumanInTheLoopMiddleware` 对敏感工具调用要求人工审批。当智能体尝试调用指定的工具时，中间件会暂停执行并等待人工决策。

## 配置

通过 `interrupt_on` 参数指定需要审批的工具：

```python
HumanInTheLoopMiddleware(
    interrupt_on={
        "send_email": {
            "allowed_decisions": ["approve", "edit"]
        }
    }
)
```

## 允许的决策

- **approve**：批准工具调用，按原样执行
- **edit**：编辑工具调用的参数后执行
- **reject**：拒绝工具调用，智能体收到拒绝消息

## 使用场景

人在回路适用于需要人工监督的高风险操作，如发送电子邮件、执行金融交易、修改数据库或调用外部 API。