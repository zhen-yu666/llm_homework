# LangChain 框架架构

> 来源：https://docs.langchain.com/oss/python/concepts/products
> 抓取日期：2026-09-26
> 模块：01_architecture

## 三层抽象：Runtime、Framework、Harness

LangChain 维护多个开源包，每个在智能体开发栈中服务于不同目的。理解智能体框架（如 LangChain）、智能体运行时（如 LangGraph）和智能体封装（如 Deep Agents SDK）之间的区别，有助于选择合适的工具。

| | Runtime | Framework | Harness |
|---|---|---|---|
| **增值点** | 持久执行、流式传输、HITL、持久化 | 抽象、集成 | 预定义工具、提示词、子智能体 |
| **适用场景** | 低层级控制、长时间运行的有状态工作流 | 快速入门、团队标准化 | 更自主的智能体、复杂非确定性任务 |
| **选项** | LangGraph、Temporal、Inngest | LangChain、Vercel AI SDK、CrewAI、OpenAI Agents SDK、Google ADK、LlamaIndex | Deep Agents SDK、Claude Agent SDK、Manus |

## 智能体框架（LangChain）

智能体框架提供抽象，使基于 LLM 构建应用更容易入门。LangChain 是一个智能体框架，提供结构化内容块、智能体循环和中间件等抽象。LangChain 的抽象设计旨在易于入门，同时为高级用例提供所需的灵活性。虽然 LangChain 构建于 LangGraph 之上，但你不需要了解 LangGraph 即可使用 LangChain。

### 何时使用 LangChain

- 你想要快速构建智能体和自主应用
- 你需要模型、工具和智能体循环的标准抽象
- 你想要一个易于使用但仍提供灵活性的框架
- 你正在构建不需要复杂编排的简单智能体应用

## 智能体运行时（LangGraph）

智能体运行时提供在生产环境中运行智能体的工具，支持的特性包括：持久执行（智能体在故障后持久化并可从断点恢复）、流式传输（支持工作流和响应的流式输出）、人在回路（通过检查或修改智能体状态纳入人工监督）、持久化（线程级和跨线程的状态持久化）、低层级控制（直接控制智能体编排，无需高层抽象）。

### 何时使用 LangGraph

- 你需要对智能体编排进行细粒度、低层级的控制
- 你需要长时间运行的有状态智能体的持久执行
- 你正在构建结合确定性步骤和智能体行为的复杂工作流
- 你需要生产就绪的智能体部署基础设施

## 智能体封装（Deep Agents SDK）

智能体封装是带有明确主张的、开箱即用的框架，内置工具和能力，用于构建复杂的长时间运行智能体。支持的工具包括规划能力（用待办列表跟踪多个任务）和任务委派（将子任务分配给子智能体）。

Deep Agents 可以理解为预先装备好的 `create_agent`。它由 LangChain 在 `create_agent` 和 LangGraph 之上构建，自带一整套基础设施，包括虚拟文件系统、记忆、工具集和子智能体编排。

## 分层而非竞争

LangChain、LangGraph 和 Deep Agents 是分层的，而非竞争选择。每一层构建在下一层之上。选择更高层并不会切断你使用更低层的能力——你可以在 Deep Agents 中使用 LangGraph 图，在 LangGraph 节点中使用 LangChain 工具。