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

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

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

    try:
        classifier = RuleBasedClassifier(Path(args.config))

        processor = MailProcessor(
            classifier=classifier,
            output_dir=args.out,
            report_dir=args.reports,
            copy_mode=args.copy,
            dry_run=args.dry_run
        )

        inbox_path = Path(args.inbox)

        if hasattr(processor, "process_inbox"):
            processor.process_inbox(inbox_path)
        elif hasattr(processor, "process_directory"):
            processor.process_directory(inbox_path)
        else:
            processor.process(inbox_path)

        print("\nОбработка писем завершена")
        return 0
    except Exception as e:
        logger.critical(f"Ошибка: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
