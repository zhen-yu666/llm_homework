# 智能体概念

> 来源：https://mintlify.wiki/langchain-ai/langchain/concepts/architecture
> 抓取日期：2026-09-26
> 模块：01_architecture

## 智能体循环

`create_agent` 创建一个智能体图，该图在循环中调用工具，直到满足停止条件。基本智能体循环的工作方式是：调用模型 → 模型选择工具 → 执行工具 → 将结果返回模型 → 循环直到模型不再调用工具。

## 函数签名

```python
def create_agent(
    model,           # 语言模型，可以是字符串标识符或模型实例
    tools,           # 工具列表
    system_prompt,   # 系统提示词
    middleware       # 中间件列表
) -> AgentGraph
```

## 使用示例

```python
from langchain.agents import create_agent

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[check_weather, search_web],
    system_prompt="You are a helpful assistant."
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in Beijing?"}]
})
```

## 与 Deep Agents 的关系

Deep Agents 在 `create_agent` 之上又加了一整套配套设施——记忆、工具集、子 agent 编排都自带。Deep Agents 可以理解成预先装备好的 `create_agent`。它由 LangChain 在 `create_agent` 和 LangGraph 之上构建，自带一整套基础设施：虚拟文件系统、记忆、工具集和子 agent 编排。