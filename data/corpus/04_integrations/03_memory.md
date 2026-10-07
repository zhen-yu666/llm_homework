# 记忆

> 来源：https://docs.langchain.com/oss/javascript/langchain/short-term-memory
> 抓取日期：2026-09-26
> 模块：04_integrations

## 短期记忆

短期记忆让应用在单个线程或对话中记住之前的交互。对话历史是最常见的短期记忆形式。长对话对当今的 LLM 构成挑战；完整历史可能无法放入 LLM 的上下文窗口，导致上下文丢失或错误。即使模型支持完整的上下文长度，大多数 LLM 在长上下文上仍然表现不佳。它们会被陈旧或离题的内容“分散注意力”，同时经历更慢的响应时间和更高的成本。

## 线程

线程在会话中组织多个交互，类似于电子邮件将消息分组到单个对话中的方式。需要在对话之间记住信息？使用长期记忆来存储和回忆跨不同线程和会话的用户特定或应用级数据。

## 使用方式

要向智能体添加短期记忆（线程级持久化），你需要在创建智能体时指定一个 checkpointer。LangChain 的智能体将短期记忆作为智能体状态的一部分进行管理。通过将这些内容存储在图的状态中，智能体可以访问给定对话的完整上下文，同时保持不同线程之间的隔离。状态使用 checkpointer 持久化到数据库（或内存），因此线程可以随时恢复。短期记忆在智能体被调用或步骤（如工具调用）完成时更新，状态在每个步骤开始时读取。

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

agent = create_agent(
    model="google-genai:gemini-3.6-flash",
    tools=[get_user_info],
    checkpointer=checkpointer
)

thread_config = {"configurable": {"thread_id": "1"}}

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Hi! My name is Bob."}]},
    thread_config
)
# "Hi Bob! Nice to see you here."

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    thread_config
)
# "You are Bob!"
```