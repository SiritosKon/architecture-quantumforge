"""Задание 2, шаг 2: скачивание и очистка текстов из Warhammer 40,000 wiki.

TextExtracts (prop=extracts) на этой Fandom-вики отключён, поэтому берём
готовый HTML через MediaWiki API (action=parse&prop=text) и вычищаем его до
чистой прозы с помощью BeautifulSoup: оставляем только абзацы <p>, выкидываем
инфобоксы, таблицы, галереи, сноски и служебную разметку.

Результат: scripts/_raw/<slug>.txt — по одному файлу на сущность.
Каталог _raw/ в .gitignore: в репозиторий попадёт только анонимизированный
результат (после anonymize.py), «сырой» Warhammer-текст не коммитим.

Запуск:
    python scripts/fetch_pages.py
"""

import os
import re
import sys
import time
import warnings

import requests

warnings.filterwarnings("ignore")  # глушим NotOpenSSLWarning от urllib3 на macOS
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from entities import ENTITIES, WIKI_API_URL

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_raw")
HEADERS = {"User-Agent": "quantumforge-rag-edu/1.0 (educational RAG project)"}

# Максимум символов чистого текста на документ (чтобы база не распухала).
MAX_CHARS = 12_000

# CSS-селекторы блоков, которые НЕ являются прозой и должны быть удалены.
DROP_SELECTORS = [
    "table", "aside", "figure", "style", "script",
    ".navbox", ".infobox", ".portable-infobox", ".reference",
    "sup.reference", ".mw-editsection", ".toc", ".gallery",
    ".notice", ".messagebox", ".quote",
]


def clean_html_to_prose(html: str) -> str:
    """Из HTML страницы вики оставляет только читаемые абзацы."""
    soup = BeautifulSoup(html, "lxml")
    for selector in DROP_SELECTORS:
        for el in soup.select(selector):
            el.decompose()

    paragraphs = []
    total = 0
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        text = re.sub(r"\[\d+\]", "", text)      # сноски [12]
        text = re.sub(r"\s+", " ", text).strip()  # схлопываем пробелы
        if len(text) < 40:                        # выкидываем обрывки/подписи
            continue
        paragraphs.append(text)
        total += len(text)
        if total >= MAX_CHARS:
            break
    return "\n\n".join(paragraphs)


def fetch_page(title: str) -> str:
    """Получает очищенную прозу страницы вики по её заголовку."""
    params = {
        "action": "parse", "format": "json",
        "page": title, "prop": "text", "redirects": 1,
    }
    resp = requests.get(WIKI_API_URL, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(data["error"].get("info", "unknown API error"))
    html = data["parse"]["text"]["*"]
    return clean_html_to_prose(html)


def main() -> None:
    os.makedirs(RAW_DIR, exist_ok=True)
    ok, failed = 0, []

    for i, entity in enumerate(ENTITIES, 1):
        title, slug = entity["title"], entity["slug"]
        try:
            prose = fetch_page(title)
            if len(prose) < 300:
                raise RuntimeError(f"too short ({len(prose)} chars)")
            header = (
                f"# {title}\n"
                f"category: {entity['category']}\n"
                f"source: https://warhammer40k.fandom.com/wiki/"
                f"{title.replace(' ', '_')}\n\n"
            )
            path = os.path.join(RAW_DIR, f"{slug}.txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(header + prose + "\n")
            ok += 1
            print(f"[{i:2d}/{len(ENTITIES)}] OK   {title:28s} -> {slug}.txt ({len(prose)} chars)")
        except Exception as exc:  # noqa: BLE001 — логируем и продолжаем
            failed.append((title, str(exc)))
            print(f"[{i:2d}/{len(ENTITIES)}] FAIL {title:28s} -> {exc}")
        time.sleep(0.5)  # вежливая пауза между запросами к API

    print(f"\nГотово: {ok} успешно, {len(failed)} с ошибкой. Файлы в {RAW_DIR}")
    if failed:
        print("Ошибки:")
        for title, err in failed:
            print(f"  - {title}: {err}")


if __name__ == "__main__":
    main()
