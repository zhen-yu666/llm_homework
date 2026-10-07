"""T1 基线 RAG + 裸 LLM 对比。"""
import argparse
import json
from pathlib import Path

from tqdm import tqdm

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import RESULTS_DIR, DEFAULT_TOP_K
from src.evaluate import load_qa_set
from src.generate import generate_answer, generate_bare
from src.index import build_index
from src.retriever import DenseRetriever


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-index", action="store_true")
    parser.add_argument("--k", type=int, default=DEFAULT_TOP_K)
    args = parser.parse_args()

    if args.build_index:
        build_index(strategy="header")

    retriever = DenseRetriever()
    qa_set = load_qa_set()

    rag_path = RESULTS_DIR / "t1_baseline.jsonl"
    bare_path = RESULTS_DIR / "t1_bare_llm.jsonl"

    with open(rag_path, "w", encoding="utf-8") as f_rag, \
         open(bare_path, "w", encoding="utf-8") as f_bare:
        for q in tqdm(qa_set, desc="T1"):
            results = retriever.search(q["question"], k=args.k)
            docs = [d for d, _ in results]
            rag_answer = generate_answer(q["question"], docs)
            bare_answer = generate_bare(q["question"])

            f_rag.write(json.dumps({
                "id": q["id"], "level": q["level"], "question": q["question"],
                "retrieved_chunk_ids": [d.metadata.get("chunk_id") for d in docs],
                "answer": rag_answer,
            }, ensure_ascii=False) + "\n")

            f_bare.write(json.dumps({
                "id": q["id"], "level": q["level"], "question": q["question"],
                "answer": bare_answer,
            }, ensure_ascii=False) + "\n")

    print(f"已保存 {rag_path} 与 {bare_path}")


if __name__ == "__main__":
    main()