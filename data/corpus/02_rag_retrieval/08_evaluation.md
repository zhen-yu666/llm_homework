# RAG 评估

> 来源：https://docs.langchain.com/oss/python/langchain/evaluation
> 抓取日期：2026-09-26
> 模块：02_rag_retrieval

## 评估方法

LangChain 提供了评估 RAG 系统的方法和工具。评估可以在检索模块和生成模块两个层面进行。

## LLM-as-Judge

LLM-as-Judge 使用另一个 LLM 作为评判者来评估 RAG 管道的性能。Ragas 是一个常用的 RAG 评估框架，它与 LangChain 集成良好。Ragas 使用另一个 LLM 作为裁判来评估 RAG 管道的性能。

### Ragas 核心指标

- **Faithfulness（忠实度）**：答案中的每个事实陈述是否都能在被召回的片段中找到依据
- **Answer Relevancy（答案相关性）**：答案与问题的相关程度
- **Context Recall（上下文召回率）**：检索到的上下文是否覆盖了回答问题所需的信息
- **Context Precision（上下文精确率）**：检索到的上下文中相关信息的比例

```python
from ragas.dataset_schema import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness

evaluator_llm = LangchainLLMWrapper(llm)
metric = Faithfulness(llm=evaluator_llm)
score = metric.single_turn_score(sample)
```

## AgentEvals

LangChain 的 `agentevals` 包提供了专门用于评估智能体轨迹的评估器。AgentEvals 允许你通过执行轨迹匹配（确定性比较）或使用 LLM 裁判（定性评估）来评估智能体的轨迹（消息的精确序列，包括工具调用）。

### 轨迹匹配

轨迹匹配评估器用于将智能体的执行轨迹与预期轨迹进行比较，或者使用 LLM 进行评判。这些评估器期望轨迹以 OpenAI 格式字典列表或 LangChain `BaseMessage` 类列表的形式提供。

## 检索指标

在检索层面，常用的评估指标包括：

- **Recall@k**：gold chunk 中至少有一个出现在 top-k 召回结果中的比例
- **MRR@10**：gold chunk 首次出现位置的倒数取平均（未命中的记 0）
- **MAP**：平均精度均值
- **Precision@k**：top-k 结果中相关结果的比例