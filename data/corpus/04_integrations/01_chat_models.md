# 聊天模型

> 来源：https://docs.langchain.com/oss/python/langchain/models
> 抓取日期：2026-09-26
> 模块：04_integrations

## init_chat_model

在 LangChain 中独立使用模型的最简单入门方式是使用 `init_chat_model` 从你选择的对话模型提供商初始化模型。

```python
from langchain.chat_models import init_chat_model

openai_model = init_chat_model("openai:gpt-5.5")
anthropic_model = init_chat_model("anthropic:claude-sonnet-4-6")
```

## 两种使用方式

- **固定模型**：预先指定模型并获得即用型聊天模型
- **可配置模型**：选择在运行时通过 `config` 指定参数（包括模型名称）

## 支持的提供商

LangChain 支持来自许多提供商的聊天模型，包括 OpenAI、Anthropic、Google Gemini、AWS Bedrock、MistralAI、Cohere、Ollama（本地模型）等。需要安装对应的集成包（如 `pip install langchain-openai`）。

## 工具调用

聊天模型支持工具调用（Tool Calling）。模型根据对话上下文决定何时调用工具以及提供什么输入参数。工具是定义明确的输入和输出的可调用函数，传递给聊天模型。