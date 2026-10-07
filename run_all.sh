#!/usr/bin/env bash
# ============================================================
# RAG 课程实践作业一键运行脚本
# 用法：
#   bash run_all.sh             # 完整跑一遍（含 LLM 打分，较慢）
#   bash run_all.sh --fast      # 快速模式（跳过 LLM 打分）
#   bash run_all.sh --only t1   # 只跑 T1
# ============================================================

set -euo pipefail

# ---------- 参数解析 ----------
FAST=0
ONLY=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --fast) FAST=1; shift ;;
        --only) ONLY="$2"; shift 2 ;;
        *) echo "未知参数：$1"; exit 1 ;;
    esac
done

# ---------- 环境检查 ----------
if [[ ! -f "requirements.txt" ]]; then
    echo "[错误] 请在项目根目录运行本脚本（requirements.txt 不存在）"
    exit 1
fi

if [[ ! -d "data/corpus" ]]; then
    echo "[错误] data/corpus/ 不存在，请先放入语料文件"
    exit 1
fi

if [[ ! -f "data/eval/qa_set.jsonl" ]]; then
    echo "[错误] data/eval/qa_set.jsonl 不存在"
    exit 1
fi

PYTHON=${PYTHON:-python}
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"

mkdir -p results index_store

# ---------- 辅助函数 ----------
should_run() {
    [[ -z "$ONLY" || "$ONLY" == "$1" ]]
}

fast_flag() {
    if [[ "$FAST" == "1" ]]; then echo "--skip-answer"; else echo ""; fi
}

banner() {
    echo ""
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
}

# ---------- 0. 依赖检查 ----------
banner "步骤 0：检查 Python 依赖"
$PYTHON -c "import langchain, faiss, pandas, matplotlib, tqdm" 2>/dev/null || {
    echo "[提示] 依赖未安装，正在安装 requirements.txt"
    $PYTHON -m pip install -r requirements.txt
}

# ---------- T1 ----------
if should_run "t1"; then
    banner "T1：基线 RAG + 裸 LLM 对比"
    $PYTHON scripts/run_t1.py --build-index
fi

# ---------- T2 ----------
if should_run "t2"; then
    banner "T2：分块策略网格实验"
    $PYTHON scripts/run_t2.py $(fast_flag)
fi

# ---------- T3 ----------
if should_run "t3"; then
    banner "T3：查询优化 + RRF 权重扫描"
    $PYTHON scripts/run_t3.py --alpha-scan
fi

# ---------- T4 ----------
if should_run "t4"; then
    banner "T4：稀疏/稠密/混合检索对比"
    $PYTHON scripts/run_t4.py --cases
fi

# ---------- T5 ----------
if should_run "t5"; then
    banner "T5：重排与压缩"
    $PYTHON scripts/run_t5.py $(fast_flag)
fi

# ---------- T7 ----------
if should_run "t7"; then
    banner "T7：系统评估"
    if [[ "$FAST" == "1" ]]; then
        $PYTHON scripts/run_t7.py --skip-gen-eval
    else
        $PYTHON scripts/run_t7.py
    fi
fi

# ---------- 汇总 ----------
banner "运行完成"
echo "结果已保存到 results/："
ls -1 results/ || true
echo ""
echo "图表文件："
ls -1 results/*.png 2>/dev/null || echo "（无）"
echo ""
echo "提示：报告里记得标注每个实验对应课件章节"
echo "  T2 -> 9.2.1  T3 -> 9.6 p39-40 / 9.2.2"
echo "  T4 -> 9.2.3  T5 -> 9.2.4  T7 -> 9.5.4"