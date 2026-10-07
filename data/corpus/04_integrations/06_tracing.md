# 追踪与可观测性（LangSmith）

> 来源：https://docs.langchain.com/langsmith/trace-with-langchain
> 抓取日期：2026-09-26
> 模块：04_integrations

## 概述

LangSmith 与 LangChain 无缝集成，提供智能体执行的完整追踪。所有 LangChain 智能体自动支持 LangSmith 追踪。

## 环境变量配置

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=<your-api-key>
```

## 快速开始

1. 在 smith.langchain.com 注册或登录
2. 设置环境变量
3. 运行你的 LangChain 应用

追踪将自动记录到名为 `default` 的项目中。可以配置自定义项目名称。

## 追踪内容

LangSmith 追踪记录：

- 每次 LLM 调用的输入和输出
- 工具调用的参数和结果
- 中间件的执行
- 状态变化
- 延迟和 token 使用量

## 用途

追踪对于调试和优化 RAG 系统至关重要。你可以查看检索到了哪些文档、LLM 使用了哪些上下文、生成了什么答案，以及每个步骤的耗时。这些数据直接支撑 T7 中的系统评估和失败归因。