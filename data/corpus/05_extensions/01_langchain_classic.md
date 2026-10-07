# langchain-classic 包

> 来源：https://docs.langchain.com/oss/python/migrate/langchain-v1
> 抓取日期：2026-09-26
> 模块：05_extensions

## 概述

LangChain v1 将旧版组件移至 `langchain-classic` 包。`langchain-classic` 包含：

- 旧版链条（Legacy Chains）
- 检索器（Retrievers）
- 索引（Indexes）
- Hub
- 嵌入辅助工具（如 `CacheBackedEmbeddings`）
- 社区重新导出的内容

## 安装

```bash
pip install langchain-classic
```

## 导入变化

旧版导入方式：

```python
from langchain.chains import ...
from langchain.retrievers import ...
```

v1 中改为：

```python
from langchain_classic.chains import ...
from langchain_classic.retrievers import ...
```

## 与主包的关系

`langchain-classic` 与主 `langchain` 包并行存在。主包聚焦于智能体构建模块（`create_agent`、中间件、工具），而 `langchain-classic` 保留旧版组件以支持向后兼容。