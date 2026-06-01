from __future__ import annotations
import logging
import argparse
import shutil
import json
from pathlib import Path
from src.classifier import RuleBasedClassifier

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Система обработки корпоративной почты')
    parser.add_argument("--inbox", default="data/inbox", help="Входящие")
    parser.add_argument("--out", default="data", help="Папка с разложенными файлами")
    parser.add_argument("--config", default="config/categories.json", help="Правила классификации")
    parser.add_argument("--reports", default="reports", help="Отчеты")
    parser.add_argument("--log-file", default="data/logs/app.log", help="Журнал приложения")
    parser.add_argument("--copy", action="store_true", help="Копировать вместо перемещения")
    parser.add_argument("--dry-run", action="store_true", help="Классификация и отчеты без изменения файлов")

    return parser

class Message:
    def __init__(self, filename: str, text: str):
        self.filename = filename
        self.text = text

    def get_full_text(self) -> str:
        return self.text

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    inbox_dir = Path(args.inbox)
    output_dir = Path(args.out)
    reports_dir = Path(args.reports)
    log_path = Path(args.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        encoding='utf-8'
    )
    logger = logging.getLogger("Main")
    logger.info("Запуск приложения")

    if not inbox_dir.exists():
        return 1
    try:
        classifier = RuleBasedClassifier(Path(args.config))

        file_path = [f for f in inbox_dir.iterdir() if f.is_file()]

        logger.info("Обработка писем")

        messages = []
        file_map = {}

        for path in file_path:
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                msj = Message(filename=path.name, text=content)
                messages.append(msj)
                file_map[path.name] = path
            except Exception as e:
                logger.error(f"Ошибка чтения")

        res = classifier.classify(messages)
        stats = {"total" : len(res), "distribution": {}}
        errors_cnt = 0

        for r in res:
            stats["distribution"][r.category] = stats["distribution"].get(r.category, 0) + 1
            if r.category == "empty" or r.category == "unknown":
                errors_cnt += 1

        for i, r in enumerate(res):
            cur_message = messages[i]
            filename = cur_message.filename
            source_text = file_map[filename]

            if not args.dry_run:
                target_dir = output_dir / r.folder
                target_dir.mkdir(parents=True, exist_ok=True)
                target_path = target_dir / filename

                if args.copy:
                    shutil.copy(str(source_text), str(target_path))
                else:
                    shutil.move(str(source_text), str(target_path))

        reports_dir.mkdir(parents=True, exist_ok=True)
        with open(reports_dir / "reports.json", "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)


        logger.info(f"Обработка писем завершена. Писем обработано: {len(res)}, ошибок: {errors_cnt}")

        print(f"\nОбработано файлов: {len(res)} ")
        print(f"Возникло ошибок: {errors_cnt}")
        print(f"Папка с отчетами: {reports_dir.resolve()}")
        return 0

    except Exception as e:
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
