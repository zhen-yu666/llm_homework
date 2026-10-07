"""T8-1 幻觉治理对比实验：有/无检测层的幻觉率变化。"""
import json
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from tqdm import tqdm

from src.config import RESULTS_DIR
from src.evaluate import load_qa_set, faithfulness_llm
from src.generate import generate_answer
from src.hallucination_guard import generate_with_guard
from src.index import build_chunks
from src.retriever import HybridRetriever


def estimate_hallucination_rate(answer: str, contexts: list) -> float:
    """用 LLM 打分估算幻觉率：Faithfulness 越低，幻觉率越高。

    幻觉率 = (5 - faithfulness) / 4，将 1-5 分映射到 0-1 之间。
    """
    score = faithfulness_llm(answer, contexts)
    return (5 - score) / 4.0


def main():
    qa_set = load_qa_set()
    chunks = build_chunks("header")
    retriever = HybridRetriever(chunks)

    baseline_rows = []   # 无检测层
    guarded_rows = []    # 有检测层

    for q in tqdm(qa_set, desc="T8-1 对比实验"):
        results = retriever.search(q["question"], k=5)
        docs = [d for d, _ in results]
        contexts = [d.page_content for d in docs]

        # 无检测层：直接生成
        baseline_answer = generate_answer(q["question"], docs)
        baseline_halluc = estimate_hallucination_rate(baseline_answer, contexts)
        baseline_rows.append({
            "id": q["id"],
            "level": q["level"],
            "answer": baseline_answer,
            "faithfulness": 5 - baseline_halluc * 4,
            "hallucination_rate": baseline_halluc,
            "intercepted": False,
        })

        # 有检测层：先检测再生成
        guarded_answer, passed = generate_with_guard(q["question"], docs)
        if passed:
            guarded_halluc = estimate_hallucination_rate(guarded_answer, contexts)
        else:
            guarded_halluc = 0.0  # 拦截后返回"无法回答"，无幻觉
        guarded_rows.append({
            "id": q["id"],
            "level": q["level"],
            "answer": guarded_answer,
            "faithfulness": 5 - guarded_halluc * 4,
            "hallucination_rate": guarded_halluc,
            "intercepted": not passed,
        })

    # 保存详细结果
    with open(RESULTS_DIR / "t8_1_baseline.jsonl", "w", encoding="utf-8") as f:
        for r in baseline_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(RESULTS_DIR / "t8_1_guarded.jsonl", "w", encoding="utf-8") as f:
        for r in guarded_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 汇总对比
    df_b = pd.DataFrame(baseline_rows)
    df_g = pd.DataFrame(guarded_rows)
    summary = pd.DataFrame([{
        "variant": "baseline",
        "avg_hallucination_rate": df_b["hallucination_rate"].mean(),
        "avg_faithfulness": df_b["faithfulness"].mean(),
        "intercept_rate": 0.0,
    }, {
        "variant": "with_guard",
        "avg_hallucination_rate": df_g["hallucination_rate"].mean(),
        "avg_faithfulness": df_g["faithfulness"].mean(),
        "intercept_rate": df_g["intercepted"].mean(),
    }])
    summary.to_csv(RESULTS_DIR / "t8_1_comparison.csv", index=False, encoding="utf-8-sig")

    # 按等级分层统计
    layered = df_g.groupby("level")[["hallucination_rate", "faithfulness"]].mean().reset_index()
    layered.to_csv(RESULTS_DIR / "t8_1_layered.csv", index=False, encoding="utf-8-sig")

    print("\n===== T8-1 幻觉治理对比 =====")
    print(summary)
    print("\n===== 分层结果（检测层开启） =====")
    print(layered)
    print(f"\n已保存到 {RESULTS_DIR}")


if __name__ == "__main__":
    main()