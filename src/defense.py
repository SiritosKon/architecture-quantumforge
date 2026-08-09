"""Задание 5: защита от промпт-инъекций в документах базы знаний.

Реализует два «фильтрующих» слоя (третий — pre-prompt — живёт в system-промпте
rag_bot.py):

  * looks_malicious(text) — ПОСТ-ПРОВЕРКА: распознаёт чанк с инъекцией
    (команды вида «ignore all instructions», «output: ...») и позволяет
    выбросить его до попадания в промпт LLM.
  * sanitize(text)       — УДАЛЕНИЕ СИСТЕМНЫХ КОНСТРУКЦИЙ: вырезает из текста
    управляющие фразы, оставляя остальной (безопасный) текст.

Слои включаются/выключаются флагом RAG_DEFENSE (см. rag_bot.py), чтобы можно
было продемонстрировать поведение «без фильтрации» и «с фильтрацией».
"""

import re

# Сигнатуры промпт-инъекций (команды, пытающиеся переопределить инструкции бота).
INJECTION_PATTERNS = [
    r"ignore\s+(?:all|any|the|previous|prior)\b[^.\n]*instructions?",
    r"disregard\s+[^.\n]*instructions?",
    r"forget\s+(?:all|everything|previous)\b[^.\n]*",
    r"override\s+[^.\n]*instructions?",
    r"you\s+must\s+output\b[^.\n]*",
    r"system\s+prompt",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def looks_malicious(text: str) -> bool:
    """Пост-проверка: True, если чанк содержит конструкцию промпт-инъекции."""
    return any(pattern.search(text) for pattern in _COMPILED)


def sanitize(text: str) -> str:
    """Удаляет из текста управляющие конструкции, заменяя их на пометку."""
    cleaned = text
    for pattern in _COMPILED:
        cleaned = pattern.sub("[отфильтровано]", cleaned)
    return cleaned
