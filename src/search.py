"""Задание 3: поиск по векторному индексу (проверка качества ретривера).

Загружает FAISS-индекс и по текстовому запросу возвращает ближайшие чанки
с их источником, позицией и оценкой близости.

Запуск:
    python src/search.py "Кто такой Skarkesh Drayomir?"     # свой запрос
    python src/search.py                                     # набор демо-запросов
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rag_common import load_vectorstore

# Демо-запросы на вымышленных терминах — проверяем, что поиск работает по нашей
# базе, а не по «памяти» модели о Warhammer.
DEMO_QUERIES = [
    "What weapon do the Vashtek use in battle?",   # -> Nethvok (Bolter)
    "Who is Skarkesh Drayomir?",                    # -> Emperor
    "What happened during Zephgor Verdros?",        # -> Horus Heresy
]


def search(vectorstore, query: str, k: int = 3) -> None:
    print(f"\n>>> Запрос: {query}")
    results = vectorstore.similarity_search_with_score(query, k=k)
    for rank, (doc, score) in enumerate(results, 1):
        meta = doc.metadata
        snippet = " ".join(doc.page_content.split())[:220]
        print(f"  [{rank}] score={score:.3f}  source={meta['source']} "
              f"(chunk {meta['chunk_index']}, {meta['category']})")
        print(f"      «{snippet}…»")


def main() -> None:
    vectorstore = load_vectorstore()
    queries = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else DEMO_QUERIES
    for query in queries:
        search(vectorstore, query)


if __name__ == "__main__":
    main()
