# RAG 评估指南

> 来源：https://docs.langchain.com/oss/python/langchain/evaluation
> 抓取日期：2026-09-26
> 模块：05_extensions

## 检索指标

在检索层面，评估指标包括：

- **Recall@k**：gold chunk 中至少有一个出现在 top-k 召回结果中的比例。Recall@k = 命中条数 / 总条数。
- **MRR@10**：gold chunk 首次出现位置的倒数取平均（未命中的记 0）。MRR 使用 gold chunk 首次出现位置的倒数取平均。
- **MAP**：平均精度均值，对每个查询计算精度-召回曲线下的面积，然后取平均。
- **Precision@k**：top-k 结果中相关结果的比例。

## 生成指标

在生成层面，评估指标包括：

- **Faithfulness（忠实度）**：答案中的每个事实陈述是否都能在被召回的片段中找到依据。可以逐条人工或 LLM 打分（1-5 分）。
- **Correctness（正确性）**：与 gold_answer 对比，可用 EM（精确匹配）/ ROUGE / LLM-as-Judge。
- **幻觉率**：无依据陈述数 / 总陈述数。

## 分层评估

按 L1-L4 四类分别统计指标，画出柱状图，指出系统在哪一级任务上表现最差。

## 失败归因

对表现最差的案例，逐条标注失败环节：

- **检索失败**：相关文档未被召回
- **排序失败**：相关文档被召回但排名靠后
- **生成失败**：文档正确但 LLM 生成错误
- **评测集歧义**：问题本身存在多种合理答案

## Ragas 集成

Ragas 是 RAG 评估的常用框架，与 LangChain 集成良好。Ragas 使用 LLM-as-Judge 方式评估 RAG 管道性能。核心指标包括 Faithfulness、Answer Relevancy、Context Recall 和 Context Precision。