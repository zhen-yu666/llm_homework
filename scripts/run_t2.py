"""T2 分块策略网格实验：切分方法 × chunk_size × overlap。

输出 results/t2_grid.csv 与 results/t2_recall5.png。
"""
import argparse
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
# 中文字体统一由 src.config 配置（不再强制 SimHei）
import pandas as pd
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import RESULTS_DIR, get_embeddings
from src.evaluate import load_qa_set, recall_at_k, answer_correctness_llm
from src.generate import generate_answer
from src.index import load_corpus, split_by_headers, assign_chunk_ids


def sliding_window_split(doc: Document, chunk_size: int, overlap: int):
    """固定窗口滑动切分。"""
    text = doc.page_content
    chunks = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(text), step):
        end = start + chunk_size
        piece = text[start:end].strip()
        if piece:
            chunks.append(Document(
                page_content=piece,
                metadata={"doc_id": doc.metadata["doc_id"], "source": doc.metadata["source"]},
            ))
        if end >= len(text):
            break
    return chunks


def recursive_split(doc, chunk_size, overlap):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return [
        Document(page_content=p,
                 metadata={"doc_id": doc.metadata["doc_id"], "source": doc.metadata["source"]})
        for p in splitter.split_text(doc.page_content)
    ]


def build_chunks_with(strategy, chunk_size, overlap):
    docs = load_corpus()
    all_chunks = []
    for doc in docs:
        if strategy == "header":
            all_chunks.extend(split_by_headers(doc))
        elif strategy == "recursive":
            all_chunks.extend(recursive_split(doc, chunk_size, overlap))
        elif strategy == "sliding":
            all_chunks.extend(sliding_window_split(doc, chunk_size, overlap))
    return assign_chunk_ids(all_chunks)


def run_one_config(strategy, chunk_size, overlap, qa_set, k=5, skip_answer=False):
    chunks = build_chunks_with(strategy, chunk_size, overlap)
    embeddings = get_embeddings()
    vs = FAISS.from_documents(chunks, embeddings)

    hits, correctness = [], []
    for q in tqdm(qa_set, desc=f"{strategy}-{chunk_size}-{overlap}", leave=False):
        results = vs.similarity_search(q["question"], k=k)
        retrieved_ids = [d.metadata.get("chunk_id") for d in results]
        hits.append(recall_at_k(retrieved_ids, q.get("gold_chunk_ids", []), k))
        if not skip_answer:
            ans = generate_answer(q["question"], results)
            correctness.append(
                answer_correctness_llm(q["question"], q.get("gold_answer", ""), ans)
            )
    return {
        "strategy": strategy,
        "chunk_size": chunk_size,
        "chunk_overlap": overlap,
        "num_chunks": len(chunks),
        "recall@5": sum(hits) / len(hits) if hits else 0,
        "correctness": sum(correctness) / len(correctness) if correctness else None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-answer", action="store_true", help="跳过 LLM 打分以加速")
    args = parser.parse_args()

    qa_set = load_qa_set()

    configs = [("header", 512, 0)]
    for strategy in ["recursive", "sliding"]:
        for cs in [256, 512, 1024]:
            for ov in [0, 128]:
                configs.append((strategy, cs, ov))

    rows = []
    for strategy, cs, ov in configs:
        t0 = time.time()
        row = run_one_config(strategy, cs, ov, qa_set, skip_answer=args.skip_answer)
        row["elapsed_s"] = round(time.time() - t0, 1)
        rows.append(row)
        print(row)

    df = pd.DataFrame(rows)
    out_csv = RESULTS_DIR / "t2_grid.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    plt.figure(figsize=(10, 5))
    for strategy in df["strategy"].unique():
        sub = df[df["strategy"] == strategy].sort_values(["chunk_size", "chunk_overlap"])
        label = sub["strategy"].iloc[0]
        x = [f"{s}-{o}" for s, o in zip(sub["chunk_size"], sub["chunk_overlap"])]
        plt.plot(x, sub["recall@5"], marker="o", label=label)
    plt.xlabel("chunk_size-overlap")
    plt.ylabel("Recall@5")
    plt.title("T2 分块策略对比")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "t2_recall5.png", dpi=150)
    print(f"已保存 {out_csv} 与图表")


if __name__ == "__main__":
    main()