"""评估脚本：检索指标 + 生成指标 + 分层统计 + 失败归因。"""
import json
import re
from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.config import QA_SET_PATH, RESULTS_DIR, get_llm


def load_qa_set(path: Path = QA_SET_PATH) -> List[dict]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def recall_at_k(retrieved_ids: List[str], gold_ids: List[str], k: int) -> float:
    """gold 中至少一个出现在 top-k 召回中则命中。"""
    topk = set(retrieved_ids[:k])
    return 1.0 if any(g in topk for g in gold_ids) else 0.0


def mrr_at_10(retrieved_ids: List[str], gold_ids: List[str]) -> float:
    """gold 首次出现位置的倒数，未命中记 0。"""
    for rank, cid in enumerate(retrieved_ids[:10], start=1):
        if cid in gold_ids:
            return 1.0 / rank
    return 0.0


def precision_at_k(retrieved_ids: List[str], gold_ids: List[str], k: int) -> float:
    topk = retrieved_ids[:k]
    if not topk:
        return 0.0
    hit = sum(1 for cid in topk if cid in gold_ids)
    return hit / len(topk)


def answer_correctness_llm(question: str, gold: str, pred: str) -> int:
    """LLM-as-Judge，1-5 分。"""
    llm = get_llm()
    prompt = (
        f"问题：{question}\n参考答案：{gold}\n模型答案：{pred}\n\n"
        "请给模型答案与参考答案的一致性打分，1-5 分，只输出数字。"
    )
    try:
        s = llm.invoke(prompt).content.strip()
        nums = re.findall(r"[1-5]", s)
        return int(nums[0]) if nums else 1
    except Exception:
        return 1


def faithfulness_llm(answer: str, contexts: List[str]) -> int:
    """LLM-as-Judge，1-5 分。"""
    llm = get_llm()
    ctx = "\n\n".join(contexts)[:3000]
    prompt = (
        f"以下答案的每个事实是否都能在上下文中找到依据？\n\n"
        f"上下文：\n{ctx}\n\n答案：\n{answer}\n\n"
        "请打分 1-5，只输出数字。"
    )
    try:
        s = llm.invoke(prompt).content.strip()
        nums = re.findall(r"[1-5]", s)
        return int(nums[0]) if nums else 1
    except Exception:
        return 1


def evaluate_run(run_path: Path, eval_name: str = "run"):
    """对一次实验输出做评估，生成 CSV 与分层统计。"""
    qa_set = {q["id"]: q for q in load_qa_set()}
    rows = []
    with open(run_path, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            qid = r["id"]
            q = qa_set.get(qid, {})
            gold_ids = q.get("gold_chunk_ids", [])
            retrieved = r.get("retrieved_chunk_ids", [])
            rows.append({
                "id": qid,
                "level": q.get("level", ""),
                "recall@1": recall_at_k(retrieved, gold_ids, 1),
                "recall@3": recall_at_k(retrieved, gold_ids, 3),
                "recall@5": recall_at_k(retrieved, gold_ids, 5),
                "recall@10": recall_at_k(retrieved, gold_ids, 10),
                "mrr@10": mrr_at_10(retrieved, gold_ids),
                "precision@5": precision_at_k(retrieved, gold_ids, 5),
            })
    df = pd.DataFrame(rows)
    out_csv = RESULTS_DIR / f"{eval_name}_retrieval.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    # 分层统计
    layered = df.groupby("level")[["recall@5", "mrr@10"]].mean().reset_index()
    layered.to_csv(RESULTS_DIR / f"{eval_name}_layered.csv", index=False, encoding="utf-8-sig")
    print(f"[evaluate] 已保存 {out_csv} 与分层结果")
    return df, layered