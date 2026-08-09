"""Задание 4: REST-интерфейс RAG-бота на FastAPI.

Эндпоинты:
    GET  /health           -> проверка живости
    POST /ask  {question}  -> {question, answer, sources}

Запуск локально (нужен OPENAI_API_KEY в .env):
    uvicorn src.api:app --host 0.0.0.0 --port 8000
Тест:
    curl -X POST localhost:8000/ask -H 'Content-Type: application/json' \
         -d '{"question": "Who is Skarkesh Drayomir?"}'
"""

import os
import sys
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rag_bot import get_bot

app = FastAPI(
    title="QuantumForge RAG Bot",
    description="RAG-бот по корпоративной базе знаний (Задание 4).",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, examples=["Who is Skarkesh Drayomir?"])


class Source(BaseModel):
    source: Optional[str] = None
    chunk_id: Optional[str] = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source]
    defense: bool                      # включены ли слои защиты (Задание 5)
    filtered_chunks: List[str]         # chunk_id, отброшенные пост-фильтром инъекций


@app.on_event("startup")
def _warmup() -> None:
    # Прогреваем бота (загрузка эмбеддингов + индекса) один раз при старте.
    get_bot()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> dict:
    return get_bot().answer(request.question)
