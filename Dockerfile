# Минимальный образ RAG-бота QuantumForge (FastAPI + FAISS внутри процесса).
FROM python:3.11-slim

WORKDIR /app

# Сначала зависимости — лучше кэшируется при пересборках.
COPY requirements.txt .
# CPU-only torch ставим отдельно с CPU-индекса: иначе тянутся ~3 ГБ CUDA-пакетов,
# не нужных для инференса эмбеддингов на CPU (образ раздувается, диск переполняется).
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

# Код, база знаний и готовый FAISS-индекс.
COPY . .

EXPOSE 8000

# Ключ LLM (GROQ_API_KEY и т.п.) прокидывается через env / docker compose (.env).
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
