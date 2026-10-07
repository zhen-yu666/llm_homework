# Claude Code 执行工作流

这份文件是给 Claude Code 的执行计划。请在 Ubuntu 的 VS Code 工作区中，从项目根目录执行；不要在 Windows PowerShell 中运行实验，也不要执行提交、推送或删除操作。

## 任务说明

```text
请读取项目根目录的 CLAUDE.md 和 command/vscode_migration_plan.md，按计划把本项目配置为可在 Ubuntu + VS Code 中运行。

执行要求：
1. 先检查 git status、当前分支和工作区现有改动；不要覆盖用户已有改动。
2. 只修改迁移计划中涉及的配置和字体兼容代码，不重构 RAG 算法，不修改实验指标定义。
3. 将 .vscode/settings.json 改成可移植配置，删除机器专属的 python.defaultInterpreterPath；增加合理的分析排除项和工作区路径。
4. 新增 .vscode/launch.json 和 .vscode/tasks.json，至少覆盖 T1 建索引、T7 快速评估、T8-1 和 run_all.sh --fast。
5. 新增 .env.example；确认 .gitignore 忽略 .env、.venv/ 以及本地编辑器缓存，但不要误删或忽略 data/、现有结果和索引。
6. 在 `src/config.py` 读取 `DASHSCOPE_API_KEY` 之前调用 `load_dotenv` 加载项目根目录 `.env`，这样终端运行和 VS Code 调试都能使用同一份本地配置；不要打印或提交 key。
7. 修改 Matplotlib 字体选择，使 Ubuntu 没有 SimHei 时能够选择 Noto Sans CJK SC、WenQuanYi Zen Hei 或其他已安装字体；同步移除 run_t2.py 对 SimHei 的重复强制设置。
8. 不删除 requirements.txt 中的包，不锁定版本，除非安装或导入验证证明必须调整，并说明原因。
9. 不要求 Windows 可运行；运行验证在 Ubuntu 中完成。

补充检查：当前 `.gitignore` 整体忽略 `.vscode/`。如果这些配置要通过 Git 带到 Ubuntu，请把规则调整为忽略个人缓存、允许提交 `settings.json`、`launch.json`、`tasks.json`；如果配置只在本机使用，则保持现状并报告这一点，不要用 `git add -f` 绕过规则。

验证顺序：
  python --version
  python -m pip install -r requirements.txt
  python -c "import langchain, faiss, pandas, matplotlib, tqdm; print('imports ok')"
  python scripts/run_t1.py --build-index
  python scripts/run_t7.py --skip-gen-eval
  bash run_all.sh --fast --only t2

如果没有 DASHSCOPE_API_KEY、网络或依赖无法安装，不要伪造成功：完成静态检查，并明确报告阻塞点和已经验证的内容。不要运行完整的 LLM 评分实验，避免不必要的费用。

完成后报告：
- 修改了哪些文件，以及每个文件的目的；
- 实际执行过的命令和结果；
- 哪些验证因为缺少 key、字体、网络或依赖没有执行；
- 是否仍建议使用 VS Code，或需要退回 PyCharm。
```

## Claude Code 操作步骤

1. 在 Ubuntu 中打开项目目录，并确认 VS Code 使用的是目标 Conda/venv 解释器。
2. 将真实的 `DASHSCOPE_API_KEY` 放入本地 `.env` 或 Ubuntu shell 环境；不要把 key 写进 `settings.json`、`launch.json` 或代码。
3. 把上面的“任务说明”完整交给 Claude Code，要求它先读两个 Markdown 文件再编辑。
4. Claude Code 完成编辑后，人工查看 `git diff`，重点检查是否出现绝对路径、密钥、删除数据目录或意外修改实验逻辑。
5. 按计划中的验收命令运行最小验证。首次建索引会调用 embedding API，确认 key 和费用后再执行。
6. 验收通过后由用户自行提交 Git commit；本工作流不让 Claude Code 自动 commit 或 push。

## 出错处理

- `ModuleNotFoundError`：确认 VS Code 终端和 Python 启动配置使用同一个解释器，再执行 `python -m pip install -r requirements.txt`。
- `未检测到 DASHSCOPE_API_KEY`：检查当前终端的环境变量或 `.env` 是否被启动配置加载；不要把 key 硬编码到源码。
- Matplotlib 中文方框：安装 `fonts-noto-cjk`，执行 `fc-cache -f`，重新运行生成图表。
- FAISS 或 `sentence-transformers` 安装失败：保留错误日志，先确认 Ubuntu/Python 版本和网络，不要直接改算法或换成 Windows 专用方案。
- 只有在 Remote-SSH/WSL 的 Linux 解释器、依赖和字体都无法准备时，才认为 VS Code 迁移不适合当前环境，改用 PyCharm 的 Ubuntu 解释器。
