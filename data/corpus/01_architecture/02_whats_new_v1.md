# LangChain v1 新特性

> 来源：https://docs.langchain.com/oss/python/releases/langchain-v1
> 抓取日期：2026-09-26
> 模块：01_architecture

## 核心改进

LangChain v1 是一个聚焦的、生产就绪的智能体构建基础。框架围绕三个核心改进进行了精简：`create_agent`、中间件和包简化。升级命令为 `pip install -U langchain`。

## create_agent

`create_agent` 是 LangChain 1.0 中构建智能体的标准方式。它提供了比 `langgraph.prebuilt.create_react_agent` 更简单的接口，同时通过使用中间件提供了更大的自定义潜力。

```python
from langchain.agents import create_agent

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[search_web, analyze_data, send_email],
    system_prompt="You are a helpful research assistant."
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Research AI safety trends"}]
})
```

`create_agent` 构建在基本智能体循环之上——调用模型，让它选择要执行的工具，然后在它不再调用工具时结束。

## 中间件

中间件是 `create_agent` 的定义性特性。它提供了一个高度可定制的入口点，提升了你能构建的内容的上限。优秀的智能体需要上下文工程：在正确的时间向模型提供正确的信息。中间件通过可组合的抽象帮助你控制动态提示词、对话摘要、选择性工具访问、状态管理和护栏。

### 预置中间件

LangChain 为常见模式提供了若干预置中间件：

- **PIIMiddleware**：在发送给模型之前脱敏敏感信息
- **SummarizationMiddleware**：当对话历史过长时进行压缩
- **HumanInTheLoopMiddleware**：对敏感工具调用要求审批

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    PIIMiddleware,
    SummarizationMiddleware,
    HumanInTheLoopMiddleware
)

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[read_email, send_email],
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware(
            "phone_number",
            detector=(r"(?:\+?\d{1,3}[\s.-]?)?"
                      r"(?:\(?\d{2,4}\)?[\s.-]?)?"
                      r"\d{3,4}[\s.-]?\d{4}"),
            strategy="block"
        ),
        SummarizationMiddleware(
            model="claude-sonnet-4-6",
            trigger={"tokens": 500}
        ),
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {
                    "allowed_decisions": ["approve", "edit"]
                }
            }
        )
    ]
)
```