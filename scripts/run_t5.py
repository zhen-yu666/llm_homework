"""T5 检索后优化：重排与压缩。"""
import argparse
import json
import time

import pandas as pd
from tqdm import tqdm

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import RESULTS_DIR
from src.evaluate import load_qa_set, recall_at_k
from src.generate import generate_answer
from src.index import build_chunks
from src.rerank import (
    rule_rerank, cross_encoder_rerank, llm_judge_rerank, compress_context,
)
from src.retriever import HybridRetriever


def count_tokens(text: str) -> int:
    """粗略估算：中文约 2 字符 = 1 token。"""
    return len(text) // 2


def run_variant(name, reranker, qa_set, hybrid, use_compression=False, skip_answer=False):
    rows = []
    for q in tqdm(qa_set, desc=name, leave=False):
        t0 = time.time()
        base_results = hybrid.search(q["question"], k=5)
        if reranker is None:
            top_results = base_results[:3]
        else:
            top_results = reranker(q["question"], base_results)
        docs = [d for d, _ in top_results]
        if use_compression:
            docs = compress_context(q["question"], top_results)
        answer = generate_answer(q["question"], docs) if not skip_answer else ""
        elapsed = time.time() - t0
        rows.append({
            "id": q["id"],
            "level": q["level"],
            "retrieved_chunk_ids": [d.metadata.get("chunk_id") for d in docs],
            "answer": answer,
            "context_tokens": sum(count_tokens(d.page_content) for d in docs),
            "latency_s": round(elapsed, 2),
        })
    out = RESULTS_DIR / f"t5_{name}.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return rows


def summarize(name, rows, qa_set):
    qa_map = {q["id"]: q for q in qa_set}
    hits = []
    for r in rows:
        gold = qa_map[r["id"]].get("gold_chunk_ids", [])
        hits.append(recall_at_k(r["retrieved_chunk_ids"], gold, 3))
    return {
        "variant": name,
        "recall@3": sum(hits) / len(hits) if hits else 0,
        "avg_context_tokens": sum(r["context_tokens"] for r in rows) / len(rows),
        "avg_latency_s": sum(r["latency_s"] for r in rows) / len(rows),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-answer", action="store_true")
    args = parser.parse_args()

    qa_set = load_qa_set()
    chunks = build_chunks("header")
    hybrid = HybridRetriever(chunks)

    variants = [
        ("top3_direct", None, False),
        ("top5_rule_top3", lambda q, r: rule_rerank(r)[:3], False),
        ("top5_crossencoder_top3", lambda q, r: cross_encoder_rerank(q, r, top_k=3), False),
        ("top5_llmjudge_top3", lambda q, r: llm_judge_rerank(q, r, top_k=3), False),
        ("top5_crossencoder_compress", lambda q, r: cross_encoder_rerank(q, r, top_k=3), True),
    ]

    summary = []
    for name, reranker, compress in variants:
        rows = run_variant(name, reranker, qa_set, hybrid,
                           use_compression=compress, skip_answer=args.skip_answer)
        s = summarize(name, rows, qa_set)
        summary.append(s)
        print(s)

    df = pd.DataFrame(summary)
    df.to_csv(RESULTS_DIR / "t5_summary.csv", index=False, encoding="utf-8-sig")
    print(f"已保存 {RESULTS_DIR / 't5_summary.csv'}")


if __name__ == "__main__":
    main()