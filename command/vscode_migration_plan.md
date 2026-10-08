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

## Ubuntu + Conda + VS Code 逐步启动流程

以下流程假定代码已经位于 Ubuntu。项目根目录就是能同时看到 `CLAUDE.md`、`requirements.txt`、`src/` 和 `scripts/` 的目录。所有实验命令都在 Ubuntu 的 VS Code 终端中执行，不在 Windows PowerShell 中执行。

### 第 1 步：打开 Ubuntu 终端并确认 Conda

```bash
conda --version
conda env list
```

找到准备给本项目使用的环境名，记为 `<环境名>`。如果还没有专用环境，创建一个 Python 3.10 环境：

```bash
conda create -n rag-homework python=3.10 -y
```

然后激活环境，并确认 `python` 和 `pip` 都来自这个环境：

```bash
conda activate <环境名>
python --version
which python
python -m pip --version
```

`python --version` 应为 3.10 或更高；`which python` 应指向类似 `.../envs/<环境名>/bin/python` 的路径。如果仍指向 `/usr/bin/python` 或其他 Conda 环境，先不要继续，重新执行 `conda activate <环境名>`。

### 第 2 步：进入项目根目录

```bash
cd /项目实际路径/LLM_homework
test -f CLAUDE.md && test -f requirements.txt && test -d src && echo "项目根目录正确"
```

如果没有输出“项目根目录正确”，先用 `pwd` 和 `ls` 找到真正的项目目录，再执行 `cd`。进入正确目录后，先做只读检查：

```bash
git status --short
git branch --show-current
```

记下已有的改动；后面交给 Claude Code 时不能覆盖这些改动。

### 第 3 步：用 VS Code 打开 Ubuntu 工作区

如果 Ubuntu 有图形界面，继续在已激活 Conda 环境的终端执行：

```bash
code .
```

如果你是在 Windows 上使用 VS Code 连接 Ubuntu：

1. 在 Windows VS Code 安装 `Remote - SSH` 和 `Python` 扩展。
2. 按 `Ctrl+Shift+P`，执行 `Remote-SSH: Connect to Host...`，选择 Ubuntu 主机。
3. 在远程窗口执行 `File -> Open Folder...`，选择上一步的 Ubuntu 项目根目录。
4. 打开 VS Code 集成终端，确认终端提示符仍在项目根目录，并执行 `conda activate <环境名>`。

打开项目后按 `Ctrl+Shift+P`，执行 `Python: Select Interpreter`，选择第 1 步确认过的 `.../envs/<环境名>/bin/python`。然后点击 `Terminal -> New Terminal`，在新终端再次确认：

```bash
conda activate <环境名>
which python
python --version
```

VS Code 状态栏和终端必须使用同一个 Conda 环境。不要把这个绝对路径写入 `.vscode/settings.json`；路径只在 VS Code 的解释器选择中保存。

### 第 4 步：把迁移计划交给 Claude Code

确认 VS Code 终端位于项目根目录并且 Conda 已激活后，再启动 Claude Code：

```bash
claude
```

将 `command/claude_code_workflow.md` 中的“任务说明”交给 Claude Code。要求它先读取 `CLAUDE.md` 和本计划，再按工作流编辑文件。Claude Code 只负责修改配置和字体兼容代码，不要让它自动 `git commit`、`git push` 或删除文件。

它完成后，在 VS Code 终端执行：

```bash
git diff -- .vscode src/config.py scripts/run_t2.py .env.example .gitignore
git status --short
```

人工检查 diff 中没有 Windows 路径、真实 API key、删除 `data/` 或 `results/` 的操作。当前 `.gitignore` 整体忽略 `.vscode/`；如果要把 VS Code 配置同步到其他机器，必须按改动表调整该规则，否则配置只在当前工作区有效。

### 第 5 步：建立本地环境变量文件

Claude Code 创建 `.env.example` 后，在项目根目录执行：

```bash
cp .env.example .env
code .env
```

在 `.env` 中填写真实的 `DASHSCOPE_API_KEY`，保存后关闭文件。不要把 key 写入 Python 源码、`settings.json`、`launch.json` 或 Git。确认 `.env` 被忽略：

```bash
git status --short --ignored .env
```

应能看到 `.env` 被忽略。只有在 Claude Code 已按计划把 `load_dotenv` 加入 `src/config.py` 后，`.env` 才会被 Python 自动读取；在此之前可临时执行 `export DASHSCOPE_API_KEY="sk-..."`，但不要把命令写入仓库文件。

### 第 6 步：安装 Python 依赖

仍在已激活的 Conda 环境中执行：

```bash
python -m pip install -r requirements.txt
python -c "import langchain, faiss, pandas, matplotlib, tqdm; print('依赖检查通过')"
```

必须使用 `python -m pip`，不要直接使用系统的 `pip`。如果安装失败，保留完整错误信息，先检查 Python 版本、Conda 环境和网络，不要自行删除依赖或改实验代码。

### 第 7 步：安装并检查中文字体

先检查字体是否已经存在：

```bash
fc-match "Noto Sans CJK SC"
```

如果找不到合适的中文字体，再安装：

```bash
sudo apt update
sudo apt install -y fonts-noto-cjk
fc-cache -f
fc-match "Noto Sans CJK SC"
```

输出应显示 Noto CJK 或其他可显示中文的字体。字体安装完成后再运行会生成 PNG 的实验。

### 第 8 步：做不调用 LLM 的基础检查

确认配置、目录和模块可以导入：

```bash
python -c "from src.config import PROJECT_ROOT, CORPUS_DIR, RESULTS_DIR; print(PROJECT_ROOT); print(CORPUS_DIR.exists(), RESULTS_DIR.exists())"
python -c "from src.index import load_corpus; print('语料文件数:', len(load_corpus()))"
```

这一步不应调用 DashScope。若导入报错，先根据错误检查依赖和当前解释器。

### 第 9 步：建立索引并区分 API 费用

首次建立索引会调用 embedding API。确认 `.env` 中的 key 和费用后，先只构建索引：

```bash
python -c "from src.index import build_index; build_index(strategy='header')"
```

看到索引保存到 `index_store/faiss_index/` 后，再确认文件存在：

```bash
test -f index_store/faiss_index/index.faiss && echo "索引构建成功"
```

`python scripts/run_t1.py --build-index` 不只是建索引，它还会对问答集调用 RAG 和裸 LLM；只有需要正式生成 T1 结果时才运行：

```bash
python scripts/run_t1.py
```

如果要重新建索引并同时生成 T1 结果，才使用：

```bash
python scripts/run_t1.py --build-index
```

### 第 10 步：按费用从低到高运行实验

先运行不做 LLM 评分的快速实验：

```bash
bash run_all.sh --fast --only t2
```

检查是否生成了 `results/` 下的 CSV 或 PNG：

```bash
ls -lh results/
```

需要 T7 检索指标时，如果已经有可复用的 JSONL：

```bash
python scripts/run_t7.py --run-file results/t1_baseline.jsonl --skip-gen-eval
```

注意：如果没有 `--run-file`，T7 会先调用 LLM 生成答案；`--skip-gen-eval` 只跳过后续 LLM-as-Judge 评分，并不会跳过答案生成。正式运行其他实验前，先确认 API 费用和预计耗时。

### 第 11 步：在 VS Code 中使用启动配置和任务

Claude Code 创建配置后：

1. 按 `Ctrl+Shift+D` 打开“运行和调试”，选择 T1、T7 或 T8-1 配置。
2. 按 `Ctrl+Shift+P`，执行 `Tasks: Run Task`，选择依赖检查、构建索引或快速运行任务。
3. 每次运行前确认左下角解释器仍是目标 Conda 环境，并确认终端当前目录是项目根目录。

若启动配置找不到模块，先在终端执行 `which python` 和 `python --version`，再重新选择解释器；不要通过添加机器专属绝对路径来修复。

### 第 12 步：完成验收

下面全部满足后，才认为 VS Code 迁移完成：

```bash
which python
python --version
python -c "import langchain, faiss, pandas, matplotlib, tqdm; print('imports ok')"
test -f index_store/faiss_index/index.faiss && echo "index ok"
find results -maxdepth 1 -type f | head
git diff --check
```

验收通过后由你自行提交 Git commit。不要让 Claude Code 自动提交或推送。

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
