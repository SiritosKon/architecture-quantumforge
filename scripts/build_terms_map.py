"""Задание 2, шаг 3: генерация словаря замен terms_map.json.

Идея: берём известную модели вселенную (Warhammer 40,000) и заменяем все
ключевые термины на ВЫМЫШЛЕННЫЕ, чтобы LLM не могла ответить «по памяти», а была
вынуждена опираться только на наш векторный индекс (честный RAG).

Стратегия генерации (по выбору: faker/slugify + скрипт):
  * RNG берётся из Faker с ФИКСИРОВАННЫМ seed  -> результат воспроизводим:
    один и тот же прогон всегда даёт тот же словарь.
  * Имена собираются из слогов -> звучат как sci-fi, а не как случайный мусор,
    поэтому тексты остаются читаемыми.
  * КОНЦЕПТ-ОРИЕНТИРОВАННО: у одной сущности может быть несколько исходных форм
    (aliases) — «Space Marines», «Adeptus Astartes», «Astartes». Все они
    отображаются в ОДНО вымышленное имя, поэтому мир остаётся связным, а бот
    отвечает согласованно.

Результат: knowledge_base/terms_map.json — плоский словарь {оригинал: замена},
отсортированный так, что применять его нужно longest-match-first (см. anonymize.py).

Запуск:
    python scripts/build_terms_map.py
"""

import json
import os

from faker import Faker
from slugify import slugify

SEED = 40_000  # фиксируем для воспроизводимости (заодно оммаж вселенной)

OUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "knowledge_base", "terms_map.json",
)

# Слоги для генерации вымышленных sci-fi имён.
ONSETS = ["Vel", "Xar", "Kra", "Zor", "Thal", "Dra", "Nyx", "Qua", "Vor", "Kael",
          "Syn", "Tor", "Zeph", "Mal", "Grix", "Oth", "Ver", "Cyn", "Ael", "Rho",
          "Skar", "Ulth", "Bral", "Neth", "Pyr", "Vash", "Kor", "Zan", "Fel", "Dorn"]
MIDS = ["a", "o", "e", "i", "u", "ae", "ii", "yo", "ea", "ou"]
CODAS = ["gor", "th", "n", "ss", "x", "kar", "dûm", "vex", " mir", "los", "ryn",
         "dros", "kesh", "var", "thos", "nex", "mor", "dan", "lith", "quor",
         "tek", "gan", "sar", "vok", "rax", "nel", "dus", "phor", "yss", "ock"]


class NameFactory:
    """Генерирует уникальные вымышленные имена детерминированно (по seed)."""

    def __init__(self, seed: int):
        faker = Faker()
        Faker.seed(seed)
        self.rng = faker.random  # random.Random под капотом — воспроизводимо
        self._used = set()

    def _token(self) -> str:
        onset = self.rng.choice(ONSETS)
        coda = self.rng.choice(CODAS).strip()
        if self.rng.random() < 0.5:
            return (onset + self.rng.choice(MIDS) + coda).replace(" ", "")
        return (onset + coda).replace(" ", "")

    def make(self, words: int = 1) -> str:
        """Вымышленное имя из `words` токенов, гарантированно уникальное."""
        for _ in range(100):
            name = " ".join(self._token().capitalize() for _ in range(words))
            if name not in self._used:
                self._used.add(name)
                return name
        raise RuntimeError("не удалось сгенерировать уникальное имя")


# Концепты вселенной: canonical — для справки, surfaces — все формы в текстах,
# words — из скольких слов делать вымышленную замену (чтобы сохранить «вес» имени).
# Порядок surfaces внутри концепта не важен: сортировка по длине — в anonymize.py.
CONCEPTS = [
    # --- Персонажи ---
    {"id": "emperor", "words": 2, "surfaces": ["The Emperor of Mankind", "Emperor of Mankind", "The Emperor", "Emperor"]},
    {"id": "guilliman", "words": 2, "surfaces": ["Roboute Guilliman", "Guilliman"]},
    {"id": "horus", "words": 1, "surfaces": ["Horus Lupercal", "Horus"]},
    {"id": "sanguinius", "words": 1, "surfaces": ["Sanguinius"]},
    {"id": "leman-russ", "words": 2, "surfaces": ["Leman Russ"]},
    {"id": "abaddon", "words": 2, "surfaces": ["Abaddon the Despoiler", "Abaddon"]},
    {"id": "calgar", "words": 2, "surfaces": ["Marneus Calgar", "Calgar"]},
    {"id": "fabius-bile", "words": 2, "surfaces": ["Fabius Bile"]},

    # --- Фракции / организации ---
    {"id": "space-marines", "words": 1, "surfaces": ["Space Marines", "Space Marine", "Adeptus Astartes", "Astartes"]},
    {"id": "imperium", "words": 2, "surfaces": ["Imperium of Man", "The Imperium", "Imperium"]},
    {"id": "mechanicus", "words": 2, "surfaces": ["Adeptus Mechanicus", "Mechanicum", "Mechanicus", "Tech-priest", "Tech-priests"]},
    {"id": "inquisition", "words": 1, "surfaces": ["The Inquisition", "Inquisition", "Inquisitor", "Inquisitors"]},
    {"id": "chaos-marines", "words": 2, "surfaces": ["Chaos Space Marines", "Traitor Legions", "Traitor Marines"]},
    {"id": "chaos", "words": 1, "surfaces": ["Chaos Gods", "Chaos"]},
    {"id": "orks", "words": 1, "surfaces": ["Orks", "Orkish", "Ork"]},
    {"id": "aeldari", "words": 1, "surfaces": ["Aeldari", "Eldar"]},
    {"id": "tyranids", "words": 1, "surfaces": ["Tyranids", "Tyranid"]},
    {"id": "necrons", "words": 1, "surfaces": ["Necrons", "Necron"]},
    {"id": "tau", "words": 2, "surfaces": ["T'au Empire", "Tau Empire", "T'au", "Tau"]},
    {"id": "guard", "words": 2, "surfaces": ["Astra Militarum", "Imperial Guard"]},
    {"id": "ultramarines", "words": 1, "surfaces": ["Ultramarines", "Ultramarine"]},
    {"id": "blood-angels", "words": 2, "surfaces": ["Blood Angels"]},
    {"id": "space-wolves", "words": 2, "surfaces": ["Space Wolves"]},
    {"id": "primarch", "words": 1, "surfaces": ["Primarchs", "Primarch"]},

    # --- Планеты / локации ---
    {"id": "terra", "words": 1, "surfaces": ["Holy Terra", "Terra"]},
    {"id": "mars", "words": 1, "surfaces": ["Mars", "Martians", "Martian"]},
    {"id": "cadia", "words": 1, "surfaces": ["Cadia", "Cadians", "Cadian"]},
    {"id": "macragge", "words": 1, "surfaces": ["Macragge"]},
    {"id": "armageddon", "words": 1, "surfaces": ["Armageddon"]},
    {"id": "fenris", "words": 1, "surfaces": ["Fenris", "Fenrisians", "Fenrisian"]},
    {"id": "eye-of-terror", "words": 2, "surfaces": ["Eye of Terror"]},

    # --- Технологии / оружие ---
    {"id": "bolter", "words": 1, "surfaces": ["Bolter", "Boltgun", "Boltguns", "Bolters", "Bolt pistol"]},
    {"id": "chainsword", "words": 1, "surfaces": ["Chainsword", "Chainswords"]},
    {"id": "power-armour", "words": 2, "surfaces": ["Power Armour", "Power Armor"]},
    {"id": "lasgun", "words": 1, "surfaces": ["Lasgun", "Lasguns", "Las-gun"]},
    {"id": "titan", "words": 1, "surfaces": ["Titan Legions", "Titans", "Titan"]},
    {"id": "warp", "words": 1, "surfaces": ["The Warp", "Immaterium", "Warp"]},
    {"id": "gellar-field", "words": 2, "surfaces": ["Gellar Field", "Gellar Fields"]},

    # --- События ---
    {"id": "horus-heresy", "words": 2, "surfaces": ["The Horus Heresy", "Horus Heresy"]},
    {"id": "great-crusade", "words": 2, "surfaces": ["The Great Crusade", "Great Crusade"]},
    {"id": "battle-macragge", "words": 2, "surfaces": ["Battle of Macragge"]},

    # --- Доп. зачистка однозначных WH40k-маркеров и производных форм ---
    # (родовую лексику Legion/Chapter/Crusade/Hive/Millennium/Mankind оставляем
    #  осознанно: она не выдаёт конкретную вселенную)
    {"id": "setting", "words": 1, "surfaces": ["Warhammer 40,000", "Warhammer 40.000", "Warhammer 40K", "Warhammer 40k", "Warhammer"]},
    {"id": "imperial-adj", "words": 1, "surfaces": ["Imperials", "Imperial"]},
    {"id": "terran-adj", "words": 1, "surfaces": ["Terrans", "Terran"]},
    {"id": "warmaster", "words": 1, "surfaces": ["Warmaster"]},
    {"id": "heresy", "words": 1, "surfaces": ["Heresy"]},
    {"id": "xenos", "words": 1, "surfaces": ["Xenos"]},
    {"id": "custodes", "words": 2, "surfaces": ["Adeptus Custodes", "Custodes"]},
    {"id": "adeptus-terra", "words": 2, "surfaces": ["Adeptus Terra"]},
    {"id": "arbites", "words": 2, "surfaces": ["Adeptus Arbites", "Arbites"]},
    {"id": "administratum", "words": 2, "surfaces": ["Adeptus Administratum", "Administratum"]},
    {"id": "ministorum", "words": 2, "surfaces": ["Adeptus Ministorum", "Ministorum", "Ecclesiarchy"]},
    {"id": "sororitas", "words": 2, "surfaces": ["Adepta Sororitas", "Adeptus Sororitas", "Sisters of Battle", "Sororitas"]},
    {"id": "adeptus-generic", "words": 1, "surfaces": ["Adeptus", "Adepta"]},
    {"id": "ullanor", "words": 1, "surfaces": ["Ullanor"]},
    {"id": "segmentum", "words": 2, "surfaces": ["Segmentum Solar", "Segmentum"]},
    {"id": "sol", "words": 1, "surfaces": ["Sol System", "Sol"]},
    {"id": "craftworld", "words": 1, "surfaces": ["Craftworlds", "Craftworld"]},
    {"id": "grey-knights", "words": 2, "surfaces": ["Grey Knights"]},
    {"id": "genestealer", "words": 1, "surfaces": ["Genestealers", "Genestealer"]},
    {"id": "norn", "words": 1, "surfaces": ["Norn-Queen", "Norn"]},
    # Боги Хаоса — у каждого своё вымышленное имя (сохраняем различимость)
    {"id": "khorne", "words": 1, "surfaces": ["Khorne"]},
    {"id": "tzeentch", "words": 1, "surfaces": ["Tzeentch"]},
    {"id": "nurgle", "words": 1, "surfaces": ["Nurgle"]},
    {"id": "slaanesh", "words": 1, "surfaces": ["Slaanesh"]},
    {"id": "ynnead", "words": 1, "surfaces": ["Ynnead"]},
    {"id": "ork-gods", "words": 1, "surfaces": ["Gork and Mork", "Gork", "Mork"]},
    {"id": "slann", "words": 1, "surfaces": ["Slann"]},
]


def build() -> dict:
    factory = NameFactory(SEED)
    term_map: dict[str, str] = {}
    for concept in CONCEPTS:
        fictional = factory.make(concept["words"])
        for surface in concept["surfaces"]:
            term_map[surface] = fictional
    return term_map


def main() -> None:
    term_map = build()
    # Сортируем по убыванию длины ключа: длинные фразы заменяются раньше коротких
    # («Chaos Space Marines» -> раньше, чем «Space Marines» / «Chaos»).
    ordered = dict(sorted(term_map.items(), key=lambda kv: len(kv[0]), reverse=True))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(ordered, fh, ensure_ascii=False, indent=2)

    concepts = len(CONCEPTS)
    surfaces = len(term_map)
    fictional_names = len(set(term_map.values()))
    print(f"terms_map.json: {surfaces} исходных форм -> {fictional_names} вымышленных имён "
          f"({concepts} концептов)")
    print(f"Файл: {OUT_PATH}")
    print("Примеры замен:")
    for original in list(ordered)[:6]:
        print(f"  {original!r} -> {ordered[original]!r}")
    # slugify используется как машинный id концепта (напр. для отладки/отчёта)
    print("Пример slug концепта:", slugify(CONCEPTS[0]["surfaces"][0]))


if __name__ == "__main__":
    main()
