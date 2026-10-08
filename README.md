# RAG 课程实践作业

《大规模语言模型：从理论到实践》 检索增强生成实践作业。

## 一、环境与安装

### 环境要求

- 运行具体查看 `requirements.txt` 文件

### 环境配置

```bash
# 配置conda环境
conda activate <环境名>
python --version
which python
python -m pip --version

# 创建.env并填入key，这里实验默认是阿里云百炼的API
cp .env.example .env
code .env

# 安装依赖
python -m pip install -r requirements.txt
python -c "import langchain, faiss, pandas, matplotlib, tqdm; print('依赖检查通过')"

# 安装并检查中文字体
fc-match "Noto Sans CJK SC"
```

## 二、目录说明

```text
data/corpus/        自建语料（LangChain 官方文档，26 篇）
data/eval/          评测集（qa_set.jsonl，25 条）
src/                核心模块
scripts/            实验入口脚本
index_store/        索引持久化
results/            实验结果（CSV/JSON/PNG）
```

## 三、复现命令

```bash
Ctrl+Shift+P → Tasks: Run Task（或菜单 终端 → 运行任务）→ 选任务
```

| 顺序 | 任务                              | 主要产出                                           |
| :--- | --------------------------------- | -------------------------------------------------- |
| 1    | 复现：检查导入                    | 无                                                 |
| 2    | 复现：仅构建 header 索引          | `index_store/faiss_index/`                         |
| 3    | 复现：T1 基线（建索引）           | `t1_baseline.jsonl、t1_bare_llm.jsonl`             |
| 4    | 复现：T2 分块（跳过LLM评分）      | `t2_grid.csv、t2_recall5.png`                      |
| 5    | 复现：T3 查询优化与 RRF           | `t3_strategies.csv、t3_rrf_alpha.csv/.png`         |
| 6    | 复现：T4 检索器对比               | `t4_retrievers.csv、t4_cases.jsonl、t4_recall.png` |
| 7    | 复现：T5 重排压缩（跳过答案生成） | `t5_summary.csv、各变体 jsonl `                    |
| 8    | 复现：T7 检索快速检查             | `t7_*.csv、t7_layered.png`                         |
| 9    | 复现：T7 统评估（完整）           | `t7_*.csv、t7_layered.png`                         |
| 10   | 复现：T8-1 幻觉治理               | `t8_1_*.csv/.jsonl`                                |

- 对于T5需要下载`BAAI/beg-reranker-base`

## 四、模块与课件章节对应

| 模块 | 文件 | 对应课件 |
|---|---|---|
| 索引构建与分块 | src/index.py | 9.2.1 |
| 检索前优化 | scripts/run_t3.py | 9.6 p39-40、9.2.2 |
| 稀疏/稠密/混合检索 | src/retriever.py | 9.2.3 |
| 检索后优化 | src/rerank.py | 9.2.4 |
| 生成 | src/generate.py | 9.6 |
| 评估 | src/evaluate.py | 9.5.4 |
| 系统评估（T7） | scripts/run_t7.py | 9.5 |

## 五、引用来源

- LangChain 官方文档：https://docs.langchain.com
- LangChain v1 迁移指南：https://docs.langchain.com/oss/python/migrate/langchain-v1
- Ragas 评估框架：https://docs.ragas.io
- rank_bm25：https://github.com/dorianbrown/rank_bm25
- sentence-transformers：https://www.sbert.net

代码参考 LangChain 官方教程并做修改，核心实验与分析独立完成。

## 六、复现说明

- 随机种子：`seed=42`（见 src/config.py）
- 版本固定：见 requirements.txt

## 七、局限性与讨论

- 评测集 25 条，样本量有限，结论不做显著性声明
- 本地 LLM 规模 7B，生成质量受模型能力限制
- PDF/网页解析质量未纳入本次变量分析
