"""Курированный список сущностей Warhammer 40,000 для базы знаний.

Задание 2, шаг 1: выбираем 30+ ключевых сущностей по 5 категориям
(персонажи, фракции, планеты/локации, технологии/оружие, события).

Каждая запись:
  title    — точный заголовок страницы на warhammer40k.fandom.com (для MediaWiki API)
  category — категория сущности (используется в метаданных и для контроля покрытия)
  slug     — короткое машинное имя файла в knowledge_base/ (1 файл = 1 сущность)

Список намеренно > 30, чтобы после возможных «промахов» API осталось 30+ документов.
"""

ENTITIES = [
    # --- Персонажи (characters) ---
    {"title": "The Emperor of Mankind", "category": "character", "slug": "emperor-of-mankind"},
    {"title": "Roboute Guilliman", "category": "character", "slug": "roboute-guilliman"},
    {"title": "Horus", "category": "character", "slug": "horus"},
    {"title": "Sanguinius", "category": "character", "slug": "sanguinius"},
    {"title": "Leman Russ", "category": "character", "slug": "leman-russ"},
    {"title": "Abaddon the Despoiler", "category": "character", "slug": "abaddon-the-despoiler"},
    {"title": "Marneus Calgar", "category": "character", "slug": "marneus-calgar"},
    {"title": "Fabius Bile", "category": "character", "slug": "fabius-bile"},

    # --- Фракции / организации (faction) ---
    {"title": "Space Marines", "category": "faction", "slug": "space-marines"},
    {"title": "Imperium of Man", "category": "faction", "slug": "imperium-of-man"},
    {"title": "Adeptus Mechanicus", "category": "faction", "slug": "adeptus-mechanicus"},
    {"title": "Inquisition", "category": "faction", "slug": "inquisition"},
    {"title": "Chaos Space Marines", "category": "faction", "slug": "chaos-space-marines"},
    {"title": "Orks", "category": "faction", "slug": "orks"},
    {"title": "Aeldari", "category": "faction", "slug": "aeldari"},
    {"title": "Tyranids", "category": "faction", "slug": "tyranids"},
    {"title": "Necrons", "category": "faction", "slug": "necrons"},
    {"title": "T'au Empire", "category": "faction", "slug": "tau-empire"},
    {"title": "Astra Militarum", "category": "faction", "slug": "astra-militarum"},
    {"title": "Ultramarines", "category": "faction", "slug": "ultramarines"},
    {"title": "Blood Angels", "category": "faction", "slug": "blood-angels"},
    {"title": "Space Wolves", "category": "faction", "slug": "space-wolves"},

    # --- Планеты / локации (location) ---
    {"title": "Terra", "category": "location", "slug": "terra"},
    {"title": "Mars", "category": "location", "slug": "mars"},
    {"title": "Cadia", "category": "location", "slug": "cadia"},
    {"title": "Macragge", "category": "location", "slug": "macragge"},
    {"title": "Armageddon", "category": "location", "slug": "armageddon"},
    {"title": "Fenris", "category": "location", "slug": "fenris"},
    {"title": "Eye of Terror", "category": "location", "slug": "eye-of-terror"},

    # --- Технологии / оружие (technology) ---
    {"title": "Bolter", "category": "technology", "slug": "bolter"},
    {"title": "Chainsword", "category": "technology", "slug": "chainsword"},
    {"title": "Power Armour", "category": "technology", "slug": "power-armour"},
    {"title": "Lasgun", "category": "technology", "slug": "lasgun"},
    {"title": "Titan", "category": "technology", "slug": "titan"},
    {"title": "The Warp", "category": "technology", "slug": "the-warp"},
    {"title": "Gellar Field", "category": "technology", "slug": "gellar-field"},

    # --- События (event) ---
    {"title": "Horus Heresy", "category": "event", "slug": "horus-heresy"},
    {"title": "Great Crusade", "category": "event", "slug": "great-crusade"},
    {"title": "Battle of Macragge", "category": "event", "slug": "battle-of-macragge"},
]

# Базовый URL MediaWiki API вики Warhammer 40,000 на Fandom.
WIKI_API_URL = "https://warhammer40k.fandom.com/api.php"

if __name__ == "__main__":
    from collections import Counter

    counts = Counter(e["category"] for e in ENTITIES)
    print(f"Всего сущностей: {len(ENTITIES)}")
    for cat, n in sorted(counts.items()):
        print(f"  {cat:12s}: {n}")
