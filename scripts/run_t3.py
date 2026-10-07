"""T3 检索前优化：查询改写 / 多查询 / 子查询 / RRF 融合权重扫描。"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import RESULTS_DIR, get_llm
from src.evaluate import load_qa_set, recall_at_k
from src.retriever import DenseRetriever, BM25Retriever, rrf_fusion
from src.index import build_chunks


def query_rewrite(question: str) -> str:
    llm = get_llm()
    prompt = f"把下面的问题改写为适合检索的查询，保留关键术语，只输出改写后的查询：\n{question}"
    return llm.invoke(prompt).content.strip()


def multi_query(question: str, n: int = 3):
    llm = get_llm()
    prompt = f"为下面的问题生成 {n} 个语义等价或互补的检索查询，每行一个，不要编号：\n{question}"
    text = llm.invoke(prompt).content
    return [line.strip("- ").strip() for line in text.splitlines() if line.strip()][:n]


def decompose(question: str):
    llm = get_llm()
    prompt = f"把下面的复合问题拆成若干独立子问题，每行一个，不要编号：\n{question}"
    text = llm.invoke(prompt).content
    return [line.strip("- ").strip() for line in text.splitlines() if line.strip()]


def run_strategy(qa_set, dense, sparse, query_fn, use_sparse=False, k=5):
    hits = []
    for q in tqdm(qa_set, leave=False):
        queries = query_fn(q["question"])
        result_lists = []
        for query in queries:
            result_lists.append(dense.search(query, k=k))
            if use_sparse:
                result_lists.append(sparse.search(query, k=k))
        fused = rrf_fusion(result_lists, top_k=k) if len(result_lists) > 1 else result_lists[0]
        retrieved_ids = [d.metadata.get("chunk_id") for d, _ in fused]
        hits.append(recall_at_k(retrieved_ids, q.get("gold_chunk_ids", []), k))
    return sum(hits) / len(hits) if hits else 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha-scan", action="store_true")
    args = parser.parse_args()

    qa_set = load_qa_set()
    dense = DenseRetriever()
    chunks = build_chunks("header")
    sparse = BM25Retriever(chunks)

    rows = [
        {"strategy": "baseline", "recall@5":
            run_strategy(qa_set, dense, sparse, lambda q: [q])},
        {"strategy": "rewrite", "recall@5":
            run_strategy(qa_set, dense, sparse, lambda q: [query_rewrite(q)])},
        {"strategy": "multi_query", "recall@5":
            run_strategy(qa_set, dense, sparse, lambda q: [q] + multi_query(q, 3))},
        {"strategy": "sub_query", "recall@5":
            run_strategy(qa_set, dense, sparse, lambda q: decompose(q) or [q])},
        {"strategy": "mq+dense+sparse", "recall@5":
            run_strategy(qa_set, dense, sparse, lambda q: [q] + multi_query(q, 3), use_sparse=True)},
    ]
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_DIR / "t3_strategies.csv", index=False, encoding="utf-8-sig")
    print(df)

    if args.alpha_scan:
        alphas = [0.0, 0.3, 0.5, 0.7, 1.0]
        scan_rows = []
        for alpha in alphas:
            hits = []
            for q in tqdm(qa_set, desc=f"alpha={alpha}", leave=False):
                d_res = dense.search(q["question"], k=10)
                s_res = sparse.search(q["question"], k=10)
                score_map, doc_map = {}, {}
                for rank, (doc, _) in enumerate(d_res, 1):
                    cid = doc.metadata.get("chunk_id")
                    score_map[cid] = score_map.get(cid, 0) + alpha / (60 + rank)
                    doc_map[cid] = doc
                for rank, (doc, _) in enumerate(s_res, 1):
                    cid = doc.metadata.get("chunk_id")
                    score_map[cid] = score_map.get(cid, 0) + (1 - alpha) / (60 + rank)
                    doc_map[cid] = doc
                ranked = sorted(score_map.items(), key=lambda x: x[1], reverse=True)[:5]
                retrieved = [cid for cid, _ in ranked]
                hits.append(recall_at_k(retrieved, q.get("gold_chunk_ids", []), 5))
            scan_rows.append({"alpha": alpha, "recall@5": sum(hits) / len(hits)})
        scan_df = pd.DataFrame(scan_rows)
        scan_df.to_csv(RESULTS_DIR / "t3_rrf_alpha.csv", index=False, encoding="utf-8-sig")

        plt.figure(figsize=(7, 4))
        plt.plot(scan_df["alpha"], scan_df["recall@5"], marker="o")
        plt.xlabel("alpha (dense 权重)")
        plt.ylabel("Recall@5")
        plt.title("RRF 权重扫描")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(RESULTS_DIR / "t3_rrf_alpha.png", dpi=150)
        print(f"已保存 {RESULTS_DIR / 't3_rrf_alpha.png'}")


if __name__ == "__main__":
    main()