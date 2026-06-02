import json
from pathlib import Path

def run_config_wizard(config_path: Path):
    print("\n=== Мастер настройки категорий ===")
    
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {"unknown_folder": "unknown", "empty_folder": "empty", "categories": []}

    print(f"Текущих категорий: {len(config['categories'])}")
    
    name = input("Введите название новой категории (или Enter для выхода): ").strip()
    if not name:
        return

    folder = input(f"Введите папку для перемещения (например, Important/{name}): ").strip()
    description = input("Введите описание категории: ").strip()
    
    try:
        priority = int(input("Введите приоритет (0-10, чем выше, тем важнее): ") or "0")
    except ValueError:
        priority = 0

    keywords_raw = input("Введите ключевые слова через запятую: ").strip()
    keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]

    new_cat = {
        "name": name,
        "folder": folder,
        "description": description,
        "priority": priority,
        "keywords": keywords,
        "patterns": []
    }

    config["categories"].append(new_cat)

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"\nКатегория '{name}' успешно добавлена в {config_path}")
