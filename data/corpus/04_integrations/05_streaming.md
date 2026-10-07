# 流式传输

> 来源：https://docs.langchain.com/oss/python/langchain/streaming
> 抓取日期：2026-09-26
> 模块：04_integrations

## 事件流（推荐）

对于新应用，推荐使用事件流——LangChain v1.3 中引入的类型化投影 API。事件流为每个投影（消息、值、工具调用、子图）提供独立的迭代器，因此你可以独立消费它们，而无需根据 `stream_mode` 块进行分支判断。

## 事件流原理

LangChain 智能体构建于 LangGraph 之上，因此它们支持相同的流式传输栈，并针对消息、工具调用、状态和自定义更新提供了以智能体为中心的投影。事件流返回带有类型投影的运行对象，因此可以独立消费每个投影，而无需解析流模式元组。

## 使用方式

```python
async for event in agent.astream_events(
    {"messages": [{"role": "user", "content": "Hello"}]},
    version="v2"
):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")
```

## 投影类型

- **messages**：消息流
- **values**：状态值流
- **tool_calls**：工具调用流
- **subgraphs**：子图流