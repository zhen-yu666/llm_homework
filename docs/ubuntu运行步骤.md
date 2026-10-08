# Ubuntu 端运行步骤（手动执行版）

本文件供你在 Ubuntu 上手动照做，不需要 Claude Code。内容整理自 `command/vscode_migration_plan.md` 的「Ubuntu + Conda + VS Code 逐步启动流程」。

## 开始前必读

1. **代码改动无需在 Ubuntu 上重做**。以下迁移改动已完成并随 git 同步到仓库：
   - `.vscode/settings.json`（已删除机器专属的解释器路径）、`.vscode/launch.json`、`.vscode/tasks.json`
   - `src/config.py`：自动加载项目根目录 `.env`（shell 环境变量优先）；中文字体自动选择（SimHei → Noto Sans CJK SC → WenQuanYi → DejaVu Sans 兜底）
   - `scripts/run_t2.py`：不再单独强制 SimHei
   - `.env.example`
2. **有两个文件不会随 git 同步**：
   - 本文件（`docs/` 被 `.gitignore` 忽略）→ 需要你手动拷贝到 Ubuntu；
   - `.env`（真实密钥文件，被忽略）→ 在 Ubuntu 上按第 4 步新建。
3. 所有命令都在 Ubuntu 的终端 / VS Code 集成终端中执行，不要在 Windows 里跑实验。
4. 项目根目录 = 能同时看到 `requirements.txt`、`src/`、`scripts/`、`data/` 的目录。

## 第 1 步：确认 Conda 环境

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

## 第 2 步：进入项目根目录

```bash
cd /项目实际路径/LLM_homework
test -f requirements.txt && test -d src && test -d scripts && echo "项目根目录正确"
```

> 注意：原迁移计划里的 `test -f CLAUDE.md` 已去掉——`CLAUDE.md` 被 `.gitignore` 忽略，Ubuntu 上不存在。

没有输出“项目根目录正确”就先用 `pwd`、`ls` 找到真正的项目目录，再执行 `cd`。进入正确目录后做只读检查：

```bash
git status --short
git branch --show-current
```

## 第 3 步：用 VS Code 打开工作区

Ubuntu 有图形界面时（在已激活 Conda 环境的终端执行）：

```bash
code .
```

从 Windows 用 VS Code 远程连接 Ubuntu 时：

1. Windows 侧 VS Code 安装 `Remote - SSH` 和 `Python` 扩展。
2. `Ctrl+Shift+P` → `Remote-SSH: Connect to Host...`，选择 Ubuntu 主机。
3. 在远程窗口 `File -> Open Folder...`，选择项目根目录。
4. 打开 VS Code 集成终端，确认终端提示符仍在项目根目录，并执行 `conda activate <环境名>`。

打开项目后按 `Ctrl+Shift+P` → `Python: Select Interpreter`，选择第 1 步确认过的 `.../envs/<环境名>/bin/python`。然后 `Terminal -> New Terminal`，在新终端再次确认：

```bash
conda activate <环境名>
which python
python --version
```

VS Code 状态栏和终端必须使用同一个 Conda 环境。不要把绝对路径写入 `.vscode/settings.json`；路径只在 VS Code 的解释器选择中保存。

## 第 4 步：创建 .env 并填入 key

```bash
cp .env.example .env
code .env        # 无图形界面时用 nano .env
```

在 `.env` 中填写真实的 `DASHSCOPE_API_KEY`，保存后关闭。不要把 key 写入 Python 源码、`settings.json`、`launch.json` 或 Git。确认 `.env` 被忽略：

```bash
git status --short --ignored .env
```

`.env` 会被 `src/config.py`（`load_dotenv`）自动读取，终端运行和 VS Code 调试配置（`launch.json` 的 `envFile`）都生效；shell 里已导出的 `DASHSCOPE_API_KEY` 优先于 `.env` 中的值。

## 第 5 步：安装依赖

```bash
python -m pip install -r requirements.txt
python -c "import langchain, faiss, pandas, matplotlib, tqdm; print('依赖检查通过')"
```

必须使用 `python -m pip`，不要直接使用系统的 `pip`。如果安装失败，保留完整错误信息，先检查 Python 版本、Conda 环境和网络，不要自行删除依赖或改实验代码。

## 第 6 步：安装并检查中文字体

先检查字体：

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

输出应显示 Noto CJK 或其他可显示中文的字体。字体装好后再运行会生成 PNG 的实验；`src/config.py` 会自动优先选择已安装的中文字体。

## 第 7 步：不调用 LLM 的基础检查

```bash
python -c "from src.config import PROJECT_ROOT, CORPUS_DIR, RESULTS_DIR; print(PROJECT_ROOT); print(CORPUS_DIR.exists(), RESULTS_DIR.exists())"
python -c "from src.index import load_corpus; print('语料文件数:', len(load_corpus()))"
```

这一步不应调用 DashScope。若导入报错，先根据错误检查依赖和当前解释器。

## 第 8 步：建立索引（会调用 embedding API）

确认 `.env` 中的 key 和费用后，先只构建索引：

```bash
python -c "from src.index import build_index; build_index(strategy='header')"
test -f index_store/faiss_index/index.faiss && echo "索引构建成功"
```

注意：

- `python scripts/run_t1.py --build-index` 不只是建索引，它还会对问答集调用 RAG 和裸 LLM；只有需要正式生成 T1 结果时才运行 `python scripts/run_t1.py`（需要重新建索引并同时生成时才加 `--build-index`）。
- `index_store/` 已随仓库同步到 Ubuntu，直接跑评估就能用现成索引；重建会调用 API 并覆盖现有索引。

## 第 9 步：按费用从低到高运行实验

先运行不做 LLM 评分的快速实验：

```bash
bash run_all.sh --fast --only t2
ls -lh results/
```

需要 T7 检索指标时（复用已有的 JSONL）：

```bash
python scripts/run_t7.py --run-file results/t1_baseline.jsonl --skip-gen-eval
```

注意：T7 不加 `--run-file` 会先调用 LLM 生成答案；`--skip-gen-eval` 只跳过后续 LLM-as-Judge 评分，**不会**跳过答案生成。正式运行其他实验前，先确认 API 费用和预计耗时。

## 第 10 步：在 VS Code 中使用任务和调试配置

1. `Ctrl+Shift+D` 打开“运行和调试”，选择 `T1: 构建索引 + 基线 RAG`、`T7: 快速评估（跳过 LLM 生成指标）` 或 `T8-1: 幻觉治理对比`。
2. `Ctrl+Shift+P` → `Tasks: Run Task`，可选任务：
   - `依赖：检查导入` / `依赖：安装 requirements.txt`
   - `T1：构建索引` / `T7：快速评估（跳过 LLM 生成指标）` / `T8-1：幻觉治理对比`
   - `全部实验：run_all.sh --fast`
3. 每次运行前确认左下角解释器仍是目标 Conda 环境，且终端当前目录是项目根目录。

若启动配置找不到模块，先在终端执行 `which python` 和 `python --version`，再重新选择解释器；不要通过添加机器专属绝对路径来修复。

## 第 11 步：验收清单

```bash
which python
python --version
python -c "import langchain, faiss, pandas, matplotlib, tqdm; print('imports ok')"
test -f index_store/faiss_index/index.faiss && echo "index ok"
find results -maxdepth 1 -type f | head
git diff --check
```

全部满足即迁移完成：

- 解释器来自 Ubuntu 当前 Conda 环境，配置文件中没有机器专属绝对路径；
- 依赖安装和导入检查通过；
- `index_store/faiss_index/` 存在；
- `results/` 能生成文件，至少一张中文图表中的中文不是方框；
- `DASHSCOPE_API_KEY` 只存在于本地 `.env` 或 shell 环境，不进入提交内容。

验收通过后由你自行 commit / push。
