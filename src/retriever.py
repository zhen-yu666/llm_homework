"""稀疏/稠密/混合检索器。"""
from typing import List, Tuple

from langchain_core.documents import Document

from src.config import DEFAULT_TOP_K, RRF_K, get_embeddings
from src.index import load_index, build_chunks


class DenseRetriever:
    """基于 FAISS 的稠密检索。"""

    def __init__(self, index_name: str = "faiss_index"):
        self.vector_store = load_index(index_name)

    def search(self, query: str, k: int = DEFAULT_TOP_K) -> List[Tuple[Document, float]]:
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return results


class BM25Retriever:
    """基于 rank_bm25 的稀疏检索。"""

    def __init__(self, chunks: List[Document] = None):
        from rank_bm25 import BM25Okapi
        if chunks is None:
            chunks = build_chunks("header")
        self.chunks = chunks
        tokenized = [self._tokenize(c.page_content) for c in chunks]
        self.bm25 = BM25Okapi(tokenized)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        # 简单中英文分词：按空白和标点切，保留英文单词和数字
        import re
        tokens = re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", text.lower())
        return tokens

    def search(self, query: str, k: int = DEFAULT_TOP_K) -> List[Tuple[Document, float]]:
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [(self.chunks[i], float(scores[i])) for i in top_idx]


def rrf_fusion(result_lists: List[List[Tuple[Document, float]]],
               k: int = RRF_K, top_k: int = DEFAULT_TOP_K) -> List[Tuple[Document, float]]:
    """倒数排名融合（RRF）。"""
    score_map = {}
    doc_map = {}
    for results in result_lists:
        for rank, (doc, _) in enumerate(results, start=1):
            cid = doc.metadata.get("chunk_id", doc.page_content[:40])
            score_map[cid] = score_map.get(cid, 0.0) + 1.0 / (k + rank)
            doc_map[cid] = doc
    ranked = sorted(score_map.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [(doc_map[cid], score) for cid, score in ranked]


class HybridRetriever:
    """BM25 + Dense 混合检索，默认 RRF 融合。"""

    def __init__(self, chunks: List[Document] = None, index_name: str = "faiss_index"):
        self.dense = DenseRetriever(index_name)
        self.sparse = BM25Retriever(chunks)

    def search(self, query: str, k: int = DEFAULT_TOP_K,
               alpha: float = 0.5) -> List[Tuple[Document, float]]:
        """alpha=1 纯稠密，alpha=0 纯稀疏，中间为加权 RRF。"""
        dense_res = self.dense.search(query, k=k * 2)
        sparse_res = self.sparse.search(query, k=k * 2)
        if alpha >= 1.0:
            return dense_res[:k]
        if alpha <= 0.0:
            return sparse_res[:k]
        # 加权 RRF：给两路结果不同权重
        score_map = {}
        doc_map = {}
        for rank, (doc, _) in enumerate(dense_res, start=1):
            cid = doc.metadata.get("chunk_id", doc.page_content[:40])
            score_map[cid] = score_map.get(cid, 0.0) + alpha / (RRF_K + rank)
            doc_map[cid] = doc
        for rank, (doc, _) in enumerate(sparse_res, start=1):
            cid = doc.metadata.get("chunk_id", doc.page_content[:40])
            score_map[cid] = score_map.get(cid, 0.0) + (1 - alpha) / (RRF_K + rank)
            doc_map[cid] = doc
        ranked = sorted(score_map.items(), key=lambda x: x[1], reverse=True)[:k]
        return [(doc_map[cid], s) for cid, s in ranked]