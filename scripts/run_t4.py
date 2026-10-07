"""T4 检索策略对比：BM25 / Dense / Hybrid。"""
import argparse
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import RESULTS_DIR
from src.evaluate import load_qa_set, recall_at_k, mrr_at_10
from src.retriever import DenseRetriever, BM25Retriever, HybridRetriever
from src.index import build_chunks


def eval_retriever(retriever, qa_set, k_list=(1, 3, 5, 10)):
    metrics = {f"recall@{k}": [] for k in k_list}
    mrr = []
    for q in tqdm(qa_set, leave=False):
        results = retriever.search(q["question"], k=max(k_list))
        retrieved_ids = [d.metadata.get("chunk_id") for d, _ in results]
        gold = q.get("gold_chunk_ids", [])
        for k in k_list:
            metrics[f"recall@{k}"].append(recall_at_k(retrieved_ids, gold, k))
        mrr.append(mrr_at_10(retrieved_ids, gold))
    out = {name: sum(v) / len(v) for name, v in metrics.items()}
    out["mrr@10"] = sum(mrr) / len(mrr)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", action="store_true", help="输出稠密/稀疏赢的查询对照")
    args = parser.parse_args()

    qa_set = load_qa_set()
    chunks = build_chunks("header")
    dense = DenseRetriever()
    sparse = BM25Retriever(chunks)
    hybrid = HybridRetriever(chunks)

    rows = []
    for name, r in [("dense", dense), ("sparse", sparse), ("hybrid", hybrid)]:
        m = eval_retriever(r, qa_set)
        m["retriever"] = name
        rows.append(m)
        print(name, m)

    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_DIR / "t4_retrievers.csv", index=False, encoding="utf-8-sig")

    plt.figure(figsize=(8, 5))
    for name in ["dense", "sparse", "hybrid"]:
        sub = df[df["retriever"] == name].iloc[0]
        plt.plot(["@1", "@3", "@5", "@10"],
                 [sub["recall@1"], sub["recall@3"], sub["recall@5"], sub["recall@10"]],
                 marker="o", label=name)
    plt.xlabel("k")
    plt.ylabel("Recall@k")
    plt.title("T4 检索器对比")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "t4_recall.png", dpi=150)

    if args.cases:
        cases = []
        for q in qa_set:
            gold = q.get("gold_chunk_ids", [])
            d_res = dense.search(q["question"], k=3)
            s_res = sparse.search(q["question"], k=3)
            d_ids = [d.metadata.get("chunk_id") for d, _ in d_res]
            s_ids = [d.metadata.get("chunk_id") for d, _ in s_res]
            d_hit = any(g in d_ids for g in gold)
            s_hit = any(g in s_ids for g in gold)
            if d_hit and not s_hit:
                cases.append({"id": q["id"], "winner": "dense", "q": q["question"],
                              "dense_top3": d_ids, "sparse_top3": s_ids})
            elif s_hit and not d_hit:
                cases.append({"id": q["id"], "winner": "sparse", "q": q["question"],
                              "dense_top3": d_ids, "sparse_top3": s_ids})
        with open(RESULTS_DIR / "t4_cases.jsonl", "w", encoding="utf-8") as f:
            for c in cases:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        print(f"已保存 {len(cases)} 条对照案例")


if __name__ == "__main__":
    main()