"""索引构建：加载 -> 切分 -> 向量化 -> 建 FAISS 索引，并保存 chunk_id 映射。

支持多种切分策略，供 T2 网格实验调用。
"""
import json
import re
from pathlib import Path
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from src.config import (
    CORPUS_DIR, INDEX_DIR, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP,
    get_embeddings,
)


def load_corpus() -> List[Document]:
    """递归加载 data/corpus 下所有 .txt / .md 文件。"""
    docs: List[Document] = []
    for path in sorted(CORPUS_DIR.rglob("*")):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        text = path.read_text(encoding="utf-8")
        doc_id = path.stem  # 文件名去扩展名，作为 chunk_id 前缀
        docs.append(Document(page_content=text, metadata={"doc_id": doc_id, "source": str(path)}))
    return docs


def split_by_headers(doc: Document) -> List[Document]:
    """按 Markdown ## 标题切分，每个 ## 小节为一个 chunk。"""
    text = doc.page_content
    doc_id = doc.metadata["doc_id"]
    # 用 ## 切分，保留标题
    parts = re.split(r"(?m)^(##\s+.+)$", text)
    chunks: List[Document] = []
    # parts[0] 是第一个 ## 之前的内容（文件头部），也保留
    if parts[0].strip():
        chunks.append(Document(
            page_content=parts[0].strip(),
            metadata={"doc_id": doc_id, "source": doc.metadata["source"]},
        ))
    # parts[1:] 成对出现：标题, 内容
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        content = f"{header}\n\n{body}".strip()
        if content:
            chunks.append(Document(
                page_content=content,
                metadata={"doc_id": doc_id, "source": doc.metadata["source"]},
            ))
    return chunks


def split_recursive(doc: Document, chunk_size: int, chunk_overlap: int) -> List[Document]:
    """递归字符切分。"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    pieces = splitter.split_text(doc.page_content)
    return [
        Document(
            page_content=p,
            metadata={"doc_id": doc.metadata["doc_id"], "source": doc.metadata["source"]},
        )
        for p in pieces
    ]


def assign_chunk_ids(chunks: List[Document]) -> List[Document]:
    """给每个 chunk 分配 chunk_id：{doc_id}#c{三位序号}。"""
    counter = {}
    for ch in chunks:
        doc_id = ch.metadata["doc_id"]
        counter[doc_id] = counter.get(doc_id, 0) + 1
        ch.metadata["chunk_id"] = f"{doc_id}#c{counter[doc_id]:03d}"
    return chunks


def build_chunks(strategy: str = "header", chunk_size: int = DEFAULT_CHUNK_SIZE,
                 chunk_overlap: int = DEFAULT_CHUNK_OVERLAP) -> List[Document]:
    """按指定策略构建所有 chunk。

    strategy: header | recursive | sliding
    """
    docs = load_corpus()
    all_chunks: List[Document] = []
    for doc in docs:
        if strategy == "header":
            all_chunks.extend(split_by_headers(doc))
        elif strategy == "recursive":
            all_chunks.extend(split_recursive(doc, chunk_size, chunk_overlap))
        elif strategy == "sliding":
            all_chunks.extend(split_recursive(doc, chunk_size, chunk_overlap))
        else:
            raise ValueError(f"未知切分策略：{strategy}")
    return assign_chunk_ids(all_chunks)


def build_index(strategy: str = "header", chunk_size: int = DEFAULT_CHUNK_SIZE,
                chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
                index_name: str = "faiss_index"):
    """构建 FAISS 索引并保存，同时输出 chunk 映射表。"""
    chunks = build_chunks(strategy, chunk_size, chunk_overlap)
    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    save_dir = INDEX_DIR / index_name
    save_dir.mkdir(parents=True, exist_ok=True)  # 关键：先创建目录
    vector_store.save_local(str(save_dir))

    # 保存 chunk_id -> 文本 映射
    mapping = {ch.metadata["chunk_id"]: ch.page_content for ch in chunks}
    with open(save_dir / "chunk_map.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"[index] 策略={strategy} size={chunk_size} overlap={chunk_overlap} "
          f"chunks={len(chunks)} 已保存到 {save_dir}")
    return vector_store, chunks


def load_index(index_name: str = "faiss_index"):
    """加载已保存的 FAISS 索引。"""
    save_dir = INDEX_DIR / index_name
    if not save_dir.exists():
        raise FileNotFoundError(
            f"索引目录不存在：{save_dir}\n"
            f"请先运行：python scripts/run_t1.py --build-index"
        )
    embeddings = get_embeddings()
    return FAISS.load_local(
        str(save_dir), embeddings, allow_dangerous_deserialization=True
    )

if __name__ == "__main__":
    build_index()