"""Задание 2, шаг 4: применение словаря замен к текстам.

Берём «сырые» тексты Warhammer 40,000 из scripts/_raw/, прогоняем через
terms_map.json и сохраняем анонимизированные документы в knowledge_base/*.md.

Принципы замены:
  * longest-match-first — terms_map.json уже отсортирован по убыванию длины
    ключа, поэтому «Chaos Space Marines» заменяется раньше, чем «Space Marines».
  * границы слов — заменяем только целые слова/фразы (никаких «Terra» внутри
    «terrain»); апострофы и дефисы (T'au, Tech-priest) учитываются.
  * сохранение регистра — «Bolter» -> «Zorvex», «bolter» -> «zorvex».

Анти-утечка вселенной:
  * имя файла = slug вымышленного имени (bolter.txt -> zorvex.md),
  * из заголовка убираем URL-источник на fandom (он выдал бы Warhammer).
    Источником для цитирования в Задании 3 служит само имя файла.

Запуск (после fetch_pages.py и build_terms_map.py):
    python scripts/anonymize.py
"""

import json
import os
import re
import sys

from slugify import slugify

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from entities import ENTITIES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_raw")
KB_DIR = os.path.join(ROOT, "knowledge_base")
TERMS_PATH = os.path.join(KB_DIR, "terms_map.json")


def load_rules():
    """Загружает terms_map.json и компилирует regex для каждой исходной формы."""
    with open(TERMS_PATH, encoding="utf-8") as fh:
        term_map = json.load(fh)  # уже отсортирован longest-first
    rules = []
    for surface, fictional in term_map.items():
        # (?<![...]) / (?![...]) — границы слова, но с учётом апострофов/дефисов
        pattern = re.compile(
            r"(?<![A-Za-z0-9])" + re.escape(surface) + r"(?![A-Za-z0-9])",
            re.IGNORECASE,
        )
        rules.append((pattern, fictional))
    return term_map, rules


def _replacement(fictional: str):
    """Возвращает функцию-замену, сохраняющую регистр найденного вхождения.

    Строчим вымышленное имя только если ВСЁ вхождение в нижнем регистре
    (нарицательное, напр. «bolter» -> «nethvok»). Если есть хоть одна заглавная
    (имя собственное, напр. «the Emperor of Mankind» — заглавная в «Emperor»),
    оставляем капитализацию вымышленного имени.
    """
    def repl(match: re.Match) -> str:
        found = match.group(0)
        return fictional if any(ch.isupper() for ch in found) else fictional.lower()
    return repl


def anonymize_text(text: str, rules) -> str:
    for pattern, fictional in rules:
        text = pattern.sub(_replacement(fictional), text)
    return text


def split_raw(raw: str):
    """Из сырого файла достаёт title, category и тело (без URL-источника)."""
    head, _, body = raw.partition("\n\n")
    lines = head.splitlines()
    title = lines[0].lstrip("# ").strip()
    category = ""
    for line in lines[1:]:
        if line.startswith("category:"):
            category = line.split(":", 1)[1].strip()
    return title, category, body.strip()


def main() -> None:
    term_map, rules = load_rules()
    os.makedirs(KB_DIR, exist_ok=True)

    written, missing = 0, []
    for entity in ENTITIES:
        raw_path = os.path.join(RAW_DIR, f"{entity['slug']}.txt")
        if not os.path.exists(raw_path):
            missing.append(entity["slug"])
            continue

        with open(raw_path, encoding="utf-8") as fh:
            raw = fh.read()
        title, category, body = split_raw(raw)

        fictional = term_map.get(title)
        if not fictional:
            # титул не покрыт словарём — пропускаем анонимизацию имени файла
            missing.append(f"{entity['slug']} (title '{title}' not in map)")
            continue

        # Собираем документ без URL-источника и анонимизируем целиком (вместе с заголовком)
        content = f"# {title}\ncategory: {category}\n\n{body}\n"
        content = anonymize_text(content, rules)

        out_name = f"{slugify(fictional)}.md"
        out_path = os.path.join(KB_DIR, out_name)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        written += 1
        print(f"{entity['slug']:24s} -> {out_name:22s} ({fictional})")

    print(f"\nГотово: записано {written} документов в knowledge_base/")
    if missing:
        print("Пропущены:", ", ".join(missing))


if __name__ == "__main__":
    main()
