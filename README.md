# RAG 课程实践作业

《大规模语言模型：从理论到实践》 检索增强生成实践作业。

## 一、任务与分工

- 学号1 姓名：负责索引构建、检索策略、评测集构造、报告撰写
- 学号2 姓名：负责生成模块、重排序与压缩、评估脚本、Demo

> 若为单人完成，请写“独立完成全部模块”。

## 二、环境与安装

### 环境要求

- 运行具体查看 `requirements.txt` 文件

### 复现步骤

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


### 配置环境变量

```bash
# 使用 Ollama（默认）
export LLM_PROVIDER=ollama
export OLLAMA_MODEL=qwen2.5:7b

# 或使用 OpenAI 兼容 API
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-xxx
export OPENAI_BASE_URL=https://api.openai.com/v1
export OPENAI_MODEL=gpt-4o-mini
```

## 三、目录说明

```text
data/corpus/        自建语料（LangChain 官方文档，26 篇）
data/eval/          评测集（qa_set.jsonl，25 条）
src/                核心模块
scripts/            实验入口脚本
index_store/        索引持久化
results/            实验结果（CSV/JSON/PNG）
```

## 四、运行命令

```bash
# 1. 构建索引（默认按 ## 标题切分）
python scripts/run_t1.py --build-index

# 2. T1 基线 RAG + 裸 LLM 对比
python scripts/run_t1.py

# 3. T2 分块策略网格实验
python scripts/run_t2.py

# 4. T3 查询优化（改写/多查询/分解/RRF）
python scripts/run_t3.py

# 5. T4 稀疏/稠密/混合检索对比
python scripts/run_t4.py

# 6. T5 重排与压缩
python scripts/run_t5.py

# 7. T7 系统评估
python scripts/run_t7.py
```

## 五、模块与课件章节对应

| 模块 | 文件 | 对应课件 |
|---|---|---|
| 索引构建与分块 | src/index.py | 9.2.1 |
| 检索前优化 | scripts/run_t3.py | 9.6 p39-40、9.2.2 |
| 稀疏/稠密/混合检索 | src/retriever.py | 9.2.3 |
| 检索后优化 | src/rerank.py | 9.2.4 |
| 生成 | src/generate.py | 9.6 |
| 评估 | src/evaluate.py | 9.5.4 |
| 系统评估（T7） | scripts/run_t7.py | 9.5 |

## 六、引用来源

- LangChain 官方文档：https://docs.langchain.com
- LangChain v1 迁移指南：https://docs.langchain.com/oss/python/migrate/langchain-v1
- Ragas 评估框架：https://docs.ragas.io
- rank_bm25：https://github.com/dorianbrown/rank_bm25
- sentence-transformers：https://www.sbert.net

代码参考 LangChain 官方教程并做修改，核心实验与分析独立完成。

## 七、复现说明

- 随机种子：`seed=42`（见 src/config.py）
- 版本固定：见 requirements.txt
- 一键复现：`bash run_all.sh`（可选）

## 八、局限性与讨论

- 评测集 25 条，样本量有限，结论不做显著性声明
- 本地 LLM 规模 7B，生成质量受模型能力限制
- PDF/网页解析质量未纳入本次变量分析
