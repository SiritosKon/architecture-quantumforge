"""Задание 3: построение векторного индекса базы знаний.

Пайплайн:
  1) читаем документы из knowledge_base/*.md,
  2) режем на чанки (RecursiveCharacterTextSplitter),
  3) считаем эмбеддинги (all-MiniLM-L6-v2, 384-мерные),
  4) складываем в FAISS-индекс и сохраняем в index/.

Каждому чанку сохраняем метаданные (source, title, category, chunk_index),
чтобы бот мог цитировать источник и позицию.

Запуск:
    python src/build_index.py
"""

import glob
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rag_common import EMBEDDING_MODEL, INDEX_DIR, KB_DIR, get_embeddings

# Параметры чанкинга (в символах). ~1000 символов ≈ 150–200 слов — в рамках
# рекомендованных заданием 100–300 слов; overlap сохраняет контекст на стыках.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def parse_document(path: str):
    """Разбирает .md-документ базы на (title, category, body)."""
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    head, _, body = raw.partition("\n\n")
    lines = head.splitlines()
    title = lines[0].lstrip("# ").strip() if lines else os.path.basename(path)
    category = ""
    for line in lines[1:]:
        if line.startswith("category:"):
            category = line.split(":", 1)[1].strip()
    return title, category, body.strip()


def load_documents():
    """Загружает все документы базы в объекты LangChain Document."""
    from langchain_core.documents import Document

    docs = []
    for path in sorted(glob.glob(os.path.join(KB_DIR, "*.md"))):
        title, category, body = parse_document(path)
        docs.append(
            Document(
                page_content=body,
                metadata={
                    "source": os.path.basename(path),
                    "title": title,
                    "category": category,
                },
            )
        )
    return docs


def split_documents(docs):
    """Режет документы на чанки и проставляет позицию чанка внутри документа."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    # chunk_index — порядковый номер чанка внутри своего документа (позиция).
    per_source = {}
    for chunk in chunks:
        src = chunk.metadata["source"]
        idx = per_source.get(src, 0)
        chunk.metadata["chunk_index"] = idx
        chunk.metadata["chunk_id"] = f"{src}#{idx}"
        per_source[src] = idx + 1
    return chunks


def main() -> None:
    from langchain_community.vectorstores import FAISS

    print(f"Читаю документы из {KB_DIR} ...")
    docs = load_documents()
    print(f"  документов: {len(docs)}")

    chunks = split_documents(docs)
    print(f"  чанков после разбивки: {len(chunks)} "
          f"(chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    print(f"Загружаю эмбеддинг-модель: {EMBEDDING_MODEL} ...")
    embeddings = get_embeddings()

    print("Считаю эмбеддинги и строю FAISS-индекс ...")
    t0 = time.perf_counter()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    elapsed = time.perf_counter() - t0

    os.makedirs(INDEX_DIR, exist_ok=True)
    vectorstore.save_local(INDEX_DIR)

    print("\n=== Индекс построен ===")
    print(f"  чанков в индексе : {vectorstore.index.ntotal}")
    print(f"  размерность      : {vectorstore.index.d}")
    print(f"  время генерации  : {elapsed:.1f} c ({len(chunks)/elapsed:.1f} чанков/с)")
    print(f"  сохранён в       : {INDEX_DIR}/ (index.faiss + index.pkl)")


if __name__ == "__main__":
    main()
