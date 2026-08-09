"""Общие настройки и загрузчики для RAG-пайплайна (Задания 3–4).

Здесь живут: пути проекта, имя эмбеддинг-модели, фабрика эмбеддингов и загрузка
готового FAISS-индекса. Модуль импортируют build_index.py (Задание 3), search.py
и будущий rag_bot.py (Задание 4), чтобы эмбеддинги при индексации и при поиске
были ГАРАНТИРОВАННО одни и те же.
"""

import os

# Эмбеддинг-модель (выбрана в Задании 1): локальная, быстрая, 384-мерная.
#   Репозиторий: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
#   Размер вектора: 384
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Пути проекта (всё считаем от корня репозитория).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(PROJECT_ROOT, "knowledge_base")
INDEX_DIR = os.path.join(PROJECT_ROOT, "index")

# Отключаем предупреждение tokenizers о параллелизме (шум в логах).
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def get_embeddings():
    """Возвращает эмбеддинг-модель (один и тот же энкодер для индекса и запросов)."""
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},  # косинусная близость
    )


def load_vectorstore(embeddings=None):
    """Загружает сохранённый FAISS-индекс из INDEX_DIR."""
    from langchain_community.vectorstores import FAISS

    if embeddings is None:
        embeddings = get_embeddings()
    if not os.path.exists(os.path.join(INDEX_DIR, "index.faiss")):
        raise FileNotFoundError(
            f"FAISS-индекс не найден в {INDEX_DIR}. Сначала запустите: python src/build_index.py"
        )
    # allow_dangerous_deserialization: индекс мы собрали сами (доверенный источник).
    return FAISS.load_local(
        INDEX_DIR, embeddings, allow_dangerous_deserialization=True
    )
