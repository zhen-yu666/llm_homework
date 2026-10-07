# PII 中间件

> 来源：https://docs.langchain.com/oss/python/langchain/guardrails
> 抓取日期：2026-09-26
> 模块：03_middleware

## 概述

LangChain 提供内置中间件来检测和处理对话中的个人身份信息（PII）。该中间件可以检测常见 PII 类型，如电子邮件、信用卡、IP 地址等。PII 检测中间件适用于医疗和金融应用等有合规要求的场景，需要清理日志的客户服务智能体，以及任何处理敏感用户数据的应用。

## 处理策略

PII 中间件支持多种策略来处理检测到的 PII：

| 策略 | 描述 | 示例 |
|---|---|---|
| `redact` | 替换为 `[REDACTED_{PII_TYPE}]` | `[REDACTED_EMAIL]` |
| `mask` | 部分遮蔽（如最后 4 位） | `****-****-****-1234` |
| `hash` | 替换为确定性哈希 | `a8f5f167...` |
| `block` | 检测到时抛出异常 | 抛出错误 |

## 内置 PII 类型

- `credit_card`：信用卡号（Luhn 验证）
- `email`：电子邮件地址
- `ip`：IP 地址
- `mac_address`：MAC 地址
- `url`：URL
- `phone_number`：电话号码（需要自定义检测器）
- `api_key`：API 密钥（需要自定义检测器）

## 使用示例

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[customer_service_tool, email_tool],
    middleware=[
        # 在发送给模型之前脱敏用户输入中的电子邮件
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True
        ),
        # 在用户输入中遮蔽信用卡
        PIIMiddleware(
            "credit_card",
            strategy="mask",
            apply_to_input=True
        ),
        # 阻止 API 密钥 - 检测到时抛出错误
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",
            strategy="block",
            apply_to_input=True
        ),
    ]
)
```

## 流式输出脱敏

使用 `apply_to_output=True` 时，PII 中间件还会通过注册的流转换器脱敏流式输出——文本增量、工具调用参数、工具输出和状态快照。需要 `langchain>=1.3.2`。