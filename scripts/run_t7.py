"""T7 系统评估：检索 + 生成 + 分层 + 失败归因。"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import RESULTS_DIR
from src.evaluate import (
    load_qa_set, recall_at_k, mrr_at_10, precision_at_k,
    answer_correctness_llm, faithfulness_llm,
)
from src.generate import generate_answer
from src.index import build_chunks
from src.retriever import HybridRetriever


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-file", type=str, default="", help="已有 run 结果 jsonl，可选")
    parser.add_argument("--skip-gen-eval", action="store_true", help="跳过 LLM 生成指标")
    args = parser.parse_args()

    qa_set = load_qa_set()
    qa_map = {q["id"]: q for q in qa_set}

    if args.run_file:
        run_path = Path(args.run_file)
        rows = [json.loads(l) for l in run_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    else:
        chunks = build_chunks("header")
        hybrid = HybridRetriever(chunks)
        rows = []
        for q in tqdm(qa_set, desc="T7 run"):
            results = hybrid.search(q["question"], k=5)
            docs = [d for d, _ in results]
            answer = generate_answer(q["question"], docs)
            rows.append({
                "id": q["id"],
                "level": q["level"],
                "question": q["question"],
                "retrieved_chunk_ids": [d.metadata.get("chunk_id") for d in docs],
                "retrieved_texts": [d.page_content for d in docs],
                "answer": answer,
                "gold_answer": q.get("gold_answer", ""),
            })

    detail = []
    for r in rows:
        q = qa_map.get(r["id"], {})
        gold = q.get("gold_chunk_ids", [])
        retrieved = r.get("retrieved_chunk_ids", [])
        detail.append({
            "id": r["id"],
            "level": r.get("level", ""),
            "recall@1": recall_at_k(retrieved, gold, 1),
            "recall@3": recall_at_k(retrieved, gold, 3),
            "recall@5": recall_at_k(retrieved, gold, 5),
            "recall@10": recall_at_k(retrieved, gold, 10),
            "mrr@10": mrr_at_10(retrieved, gold),
            "precision@5": precision_at_k(retrieved, gold, 5),
        })
    df = pd.DataFrame(detail)
    df.to_csv(RESULTS_DIR / "t7_retrieval_detail.csv", index=False, encoding="utf-8-sig")

    layered = df.groupby("level")[
        ["recall@1", "recall@3", "recall@5", "recall@10", "mrr@10", "precision@5"]
    ].mean().reset_index()
    layered.to_csv(RESULTS_DIR / "t7_retrieval_layered.csv", index=False, encoding="utf-8-sig")
    print(layered)

    plt.figure(figsize=(8, 5))
    levels = layered["level"].tolist()
    x = list(range(len(levels)))
    plt.bar([i - 0.2 for i in x], layered["recall@5"], width=0.4, label="Recall@5")
    plt.bar([i + 0.2 for i in x], layered["mrr@10"], width=0.4, label="MRR@10")
    plt.xticks(x, levels)
    plt.xlabel("问题等级")
    plt.ylabel("指标值")
    plt.title("T7 分层检索指标")
    plt.legend()
    plt.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "t7_layered.png", dpi=150)

    if not args.skip_gen_eval:
        gen_rows = []
        for r in tqdm(rows, desc="生成指标"):
            q = qa_map.get(r["id"], {})
            corr = answer_correctness_llm(
                q.get("question", ""), q.get("gold_answer", ""), r.get("answer", "")
            )
            faith = faithfulness_llm(r.get("answer", ""), r.get("retrieved_texts", []))
            gen_rows.append({
                "id": r["id"], "level": r.get("level", ""),
                "correctness": corr, "faithfulness": faith,
            })
        gen_df = pd.DataFrame(gen_rows)
        gen_df.to_csv(RESULTS_DIR / "t7_generation_detail.csv", index=False, encoding="utf-8-sig")
        gen_layered = gen_df.groupby("level")[["correctness", "faithfulness"]].mean().reset_index()
        gen_layered.to_csv(RESULTS_DIR / "t7_generation_layered.csv",
                           index=False, encoding="utf-8-sig")
        print(gen_layered)

    worst = df.sort_values("recall@5").head(5)
    worst.to_csv(RESULTS_DIR / "t7_worst5.csv", index=False, encoding="utf-8-sig")
    print("最差 5 条：")
    print(worst[["id", "level", "recall@5", "mrr@10"]])


if __name__ == "__main__":
    main()