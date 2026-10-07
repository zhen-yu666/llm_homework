# LangChain v1 迁移指南

> 来源：https://docs.langchain.com/oss/python/migrate/langchain-v1
> 抓取日期：2026-09-26
> 模块：01_architecture

## 包结构变化

迁移到 LangChain v1 需要 `langchain>=1.0.0`、`langchain-core>=1.0.0` 和 Python 3.10+。旧版链条、检索器、索引、hub、嵌入辅助工具（如 `CacheBackedEmbeddings`）以及社区重新导出的内容已移至 `langchain-classic` 包。需要安装 `langchain-classic` 并将这些导入更新为 `langchain_classic.*`。

## 命名空间简化

LangChain v1.0 简化了命名空间：聚焦的导出保留在 `langchain.*` 中，而旧版代码移至 `langchain-classic`。

## create_agent 替代旧版 Agent

现在推荐使用 `langchain.agents.create_agent` 来构建智能体，替代之前的 `AgentExecutor` 等旧版组件。在 LangChain 1.2.0+ 中，旧组件（如 `AgentExecutor` 等）已移至 `langchain-classic` 包。

## 预模型钩子被中间件替代

预模型钩子现在实现为带有 `beforeModel` 方法的中间件。这种模式更具可扩展性——你可以定义多个中间件在模型调用之前运行，并在不同的智能体之间重用它们。工具错误处理也移至带有 `wrapToolCall` 的中间件。

## 动态模型选择

动态模型选择现在通过中间件进行，而不是通过预模型钩子。这提供了更灵活的方式来根据运行时条件选择不同的模型。