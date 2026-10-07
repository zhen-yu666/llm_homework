# VS Code 迁移改动表

## 结论

建议迁移到 VS Code，但运行环境应是 Ubuntu（推荐 VS Code Remote-SSH 或 WSL），不要把项目绑定到 Windows Python。改动规模为小到中等：不需要改 RAG 算法和实验逻辑，主要是解除机器相关配置、补充 VS Code 启动入口，并处理 Ubuntu 中文字体。

如果只能在 Windows 本机运行，而不能使用 WSL/Remote-SSH，建议继续使用 PyCharm 或先建立 Linux 环境。原因是项目的一键入口是 `run_all.sh`，并且 `faiss-cpu`、`sentence-transformers`、Matplotlib 中文字体和 Conda 环境在 Linux 上更容易保持一致；这不是代码迁移工作量过大，而是运行环境不一致的风险较高。

## 改动表

| 优先级 | 文件/位置 | 要做的改动 | 原因 | 验收方式 |
|---|---|---|---|---|
| P0 | `.vscode/settings.json` | 删除写死的 `python.defaultInterpreterPath`（当前为 `/home/linux/anaconda3/envs/torch2.4_cuda11.8/bin/python`）；保留编辑器设置，并将 Python 分析范围排除 `data/`、`index_store/`、`results/`、`docs/` | 该路径只对一台机器有效，且大数据目录会拖慢 Pylance | VS Code 中 Python 解释器由当前 Ubuntu 环境选择，状态栏不再指向不存在的路径 |
| P0 | `.vscode/settings.json` | 增加项目级 `python.analysis.extraPaths: ["${workspaceFolder}"]`，可选增加 `python.terminal.activateEnvironment: true` | 让 `from src...` 在编辑器和终端中一致解析 | 打开 `scripts/run_t1.py` 时没有 `src` 导入诊断 |
| P0 | `.vscode/launch.json` | 新增 T1、T7、T8-1 的 Python 启动配置；工作目录设为 `${workspaceFolder}`，环境变量从 `${workspaceFolder}/.env` 读取 | 在 VS Code 中可以直接运行/调试实验，不必手动拼参数 | 运行配置能启动脚本，并将结果写入 `results/` |
| P0 | `.vscode/tasks.json` | 新增“检查依赖”“构建 T1 索引”“快速跑全部实验”任务；任务命令使用已激活环境中的 `python -m pip`、`python scripts/run_t1.py --build-index`、`bash run_all.sh --fast`，不要使用已废弃的 `python.pythonPath` 变量 | 把 CLAUDE.md 中的常用命令变成 VS Code 可点击任务 | `Terminal -> Run Task` 能看到并执行这些任务 |
| P1 | `src/config.py` | 在读取配置前用 `python-dotenv` 加载项目根目录 `.env`；同时将 Matplotlib 字体从单一 `SimHei` 改为按 Ubuntu 可用字体选择，例如 `Noto Sans CJK SC`、`WenQuanYi Zen Hei`、`DejaVu Sans`，并保留 `axes.unicode_minus=False` | 让终端、调试配置都能读取 `.env`；Ubuntu 默认通常没有 `SimHei`，图表中文会变方框或产生字体警告 | 不设置 shell key 时，使用 `.env` 也能通过 key 检查；运行会生成中文可读的 PNG |
| P1 | `scripts/run_t2.py` | 删除重复的 `SimHei` 强制设置，统一复用 `src.config` 的字体配置 | 避免 T2 覆盖全局字体选择 | T2 生成的图表中文显示正常 |
| P1 | `.env.example` | 新增示例：`DASHSCOPE_API_KEY=sk-...`，可选列出 `OPENAI_MODEL`、`EMBEDDING_MODEL`、`OPENAI_BASE_URL` | 统一 VS Code 启动配置和终端的密钥来源；真实 `.env` 不提交 | 复制为 `.env` 后，启动脚本可读取 key；`.env` 被 `.gitignore` 忽略 |
| P1 | `.gitignore` | 当前规则整体忽略 `.vscode/`。如果 VS Code 配置需要随项目同步到 Ubuntu，应改为只忽略个人缓存，并允许提交可移植的 `settings.json`、`launch.json`、`tasks.json`；如果只在本机使用，则保持忽略并在 Ubuntu 手动创建 | 否则通过 Git 迁移时 VS Code 配置不会到达 Ubuntu | 根据选择检查 `git status`：配置应显示为待提交，或明确保持本地 |
| P2 | `requirements.txt` | 先不删包、不锁版本；在 Ubuntu 环境验证安装，只有确实安装失败时再针对性调整版本 | 当前依赖已覆盖脚本导入，盲目删包会影响实验 | `python -m pip install -r requirements.txt` 成功，导入检查成功 |

## Ubuntu/VS Code 执行顺序

在 VS Code 连接到 Ubuntu 后，从项目根目录执行。下面的 `python` 必须是 VS Code 当前选择的解释器：

```bash
python --version                 # 需要 Python 3.10+
python -m venv .venv              # 如果使用 venv；Conda 用户跳过
source .venv/bin/activate         # venv 用户执行
python -m pip install -r requirements.txt
cp .env.example .env              # 然后编辑 .env 填入 DASHSCOPE_API_KEY
python -c "import langchain, faiss, pandas, matplotlib, tqdm; print('依赖检查通过')"
python scripts/run_t1.py --build-index
python scripts/run_t7.py --skip-gen-eval
```

如果使用 Conda，先在 Ubuntu 终端激活环境，再在 VS Code 命令面板执行 `Python: Select Interpreter` 选择该环境；不要把某台机器的绝对路径写回 `settings.json`。加入 `load_dotenv` 后，终端命令和 VS Code 调试配置都可以读取项目根目录的 `.env`。

中文字体可选安装：

```bash
sudo apt update
sudo apt install -y fonts-noto-cjk
fc-cache -f
```

快速验证不产生 LLM 评分费用：

```bash
bash run_all.sh --fast --only t2
python scripts/run_t7.py --run-file results/t1_baseline.jsonl --skip-gen-eval
```

## 不需要改的部分

- `src/index.py` 已使用 `pathlib` 和项目根目录推导路径，不需要改成 Windows 路径。
- 各 `scripts/run_tN.py` 已注入项目根目录，不需要在 VS Code 中设置额外的 `PYTHONPATH` 才能运行；`extraPaths` 只用于编辑器提示。
- `run_all.sh` 已有依赖、数据和结果目录检查，不需要重写成 Python。
- `.idea/` 是 PyCharm 元数据，VS Code 运行时可以保留，不应复制到 `.vscode/`。

## 验收标准

1. VS Code 解释器来自当前 Ubuntu 环境，配置文件中没有机器专属绝对路径。
2. `python -m pip install -r requirements.txt` 和导入检查通过。
3. `python scripts/run_t1.py --build-index` 能生成 `index_store/faiss_index/`。
4. `bash run_all.sh --fast --only t1` 或单个实验能生成 `results/` 文件。
5. 至少一张中文图表中的中文不是方框。
6. `DASHSCOPE_API_KEY` 只存在于本地 `.env` 或 shell 环境，不进入提交内容。
